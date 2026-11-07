import os
from pathlib import Path

import pytest
import torch
from PIL import Image

from coevomed.data import load_json, training_budget
from coevomed.student_worker import (ResponseCollator, ResponseNLLMixin, freeze_vision_tower,
                                      infer, training_kwargs)


@pytest.mark.skipif(not os.environ.get("COEVOMED_TEST_PROCESSOR"), reason="Requires local Qwen3-VL processor assets")
def test_real_qwen_processor_training_save_reload_and_answer(tmp_path):
    transformers = pytest.importorskip("transformers")
    if transformers.__version__ != "4.57.1":
        pytest.skip("Student integration targets Transformers 4.57.1")
    from transformers import (AutoModelForImageTextToText, AutoProcessor, Qwen3VLConfig,
                              Qwen3VLForConditionalGeneration, Trainer, TrainingArguments)

    torch.set_num_threads(1)
    torch.manual_seed(42)
    processor = AutoProcessor.from_pretrained(os.environ["COEVOMED_TEST_PROCESSOR"], local_files_only=True)
    processor.tokenizer.padding_side = "right"
    config = Qwen3VLConfig(
        text_config={"vocab_size": 151936, "hidden_size": 64, "intermediate_size": 128,
                     "num_hidden_layers": 2, "num_attention_heads": 4, "num_key_value_heads": 2,
                     "head_dim": 16, "max_position_embeddings": 8192,
                     "rope_scaling": {"rope_type": "default", "mrope_section": [2, 3, 3], "mrope_interleaved": True},
                     "bos_token_id": 151643, "eos_token_id": 151645},
        vision_config={"depth": 1, "hidden_size": 32, "intermediate_size": 64, "num_heads": 2,
                       "out_hidden_size": 64, "patch_size": 16, "temporal_patch_size": 2,
                       "spatial_merge_size": 2, "deepstack_visual_indexes": [0], "num_position_embeddings": 64},
        image_token_id=151655, video_token_id=151656, vision_start_token_id=151652, vision_end_token_id=151653)
    model = Qwen3VLForConditionalGeneration(config)
    assert freeze_vision_tower(model) > 0
    rows = []
    for index, color in enumerate(("red", "blue", "green")):
        path = tmp_path / f"image_{index}.png"
        Image.new("RGB", (128, 128), color).save(path)
        rows.append({"id": f"train-{index}", "images": [path.name], "question": "Describe the color.",
                     "answer": f"The image is {color}."})
    rows[1]["images"].append(rows[0]["images"][0])
    rows[1]["answer"] = "One view is blue and the other is red."
    collator = ResponseCollator(processor, tmp_path, 4096)
    batch = collator(rows[:2])
    assert batch["labels"].shape == batch["input_ids"].shape
    assert torch.all(batch["labels"][batch["attention_mask"] == 0] == -100)
    assert batch["image_grid_thw"].shape[0] == 3
    collator.response_tokens = 0

    class StudentTrainer(ResponseNLLMixin, Trainer):
        pass

    learner = load_json(Path(__file__).resolve().parents[1] / "configs/demo_vqarad_mimic.json")["learner"]
    learner.update(world_size=1, epochs=2, gradient_accumulation_steps=2, deepspeed=None, bf16=False, tf32=False)
    options = training_kwargs(learner, tmp_path / "worker")
    options.update(use_cpu=True, disable_tqdm=True)
    trainer = StudentTrainer(model=model, args=TrainingArguments(**options), train_dataset=rows, data_collator=collator)
    budget = training_budget(len(rows), learner)
    assert len(trainer.get_train_dataloader()) == budget["batches_per_rank"]
    before = model.lm_head.weight.detach().clone()
    result = trainer.train()
    assert torch.isfinite(torch.tensor(result.training_loss))
    assert trainer.state.global_step == budget["training_steps"] == 4
    assert trainer.state.epoch == pytest.approx(2.0)
    assert collator.response_tokens > 0
    assert not torch.equal(before, model.lm_head.weight)

    final = tmp_path / "checkpoint_final"
    trainer.save_model(str(final))
    processor.save_pretrained(final)
    restored = AutoModelForImageTextToText.from_pretrained(final, local_files_only=True)
    restored_processor = AutoProcessor.from_pretrained(final, local_files_only=True)
    assert torch.equal(model.lm_head.weight, restored.lm_head.weight)
    predictions = infer(restored, restored_processor, rows[:1], tmp_path, max_new_tokens=4)
    assert predictions[0]["id"] == rows[0]["id"] and predictions[0]["prediction"]
