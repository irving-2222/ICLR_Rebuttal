import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import time

import torch

from .data import digest, dump_json, load_json, load_training_job, read_jsonl, validate_training_record


def freeze_vision_tower(model):
    frozen = 0
    for name, parameter in model.named_parameters():
        if "visual." in name and "merger" not in name:
            parameter.requires_grad_(False)
            frozen += getattr(parameter, "ds_numel", parameter.numel())
    if not frozen:
        raise ValueError("Could not locate Qwen vision tower to freeze")
    return frozen


def response_labels(full_ids, prompt_ids, attention_mask):
    length = prompt_ids.shape[-1]
    if length >= full_ids.shape[-1] or not torch.equal(full_ids[:length], prompt_ids):
        raise ValueError("Chat template prefix mismatch or empty response; cannot construct an assistant-only loss")
    labels = full_ids.clone()
    labels[:length] = -100
    labels[attention_mask == 0] = -100
    return labels


def response_nll(logits, labels):
    if logits.ndim != 3 or labels.shape != logits.shape[:2]:
        raise ValueError("Expected [batch, sequence, vocabulary] logits and aligned labels")
    targets = labels[:, 1:]
    if not targets.numel() or (targets != -100).sum(dim=1).min() == 0:
        raise ValueError("Every example must contain a response token")
    losses = torch.nn.functional.cross_entropy(
        logits[:, :-1].float().transpose(1, 2), targets, reduction="none", ignore_index=-100)
    return losses.sum(dim=1).mean()


class ResponseNLLMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_accepts_loss_kwargs = False

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        inputs = dict(inputs)
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        loss = response_nll(outputs.logits, labels)
        return (loss, outputs) if return_outputs else loss


def image_paths(row, media_root):
    root = Path(media_root).resolve()
    result = [(root / name).resolve() for name in row["images"]]
    if any(not p.is_relative_to(root) or not p.is_file() for p in result):
        raise ValueError("Missing image or media path outside root")
    return result


def verify_media(rows, media_root):
    from .preprocessing import rgb_digest
    checked = {}
    for row in rows:
        for path, expected in zip(image_paths(row, media_root), row["image_rgb_sha256"]):
            if path not in checked:
                checked[path] = rgb_digest(path)
            if checked[path] != expected:
                raise ValueError(f"Image content differs from the frozen inventory: {row['id']}")
    return len(checked)


def training_kwargs(config, output):
    fields = ("learning_rate", "optim", "adam_beta1", "adam_beta2", "adam_epsilon", "weight_decay",
              "warmup_ratio", "lr_scheduler_type", "max_grad_norm", "gradient_accumulation_steps",
              "bf16", "tf32", "gradient_checkpointing", "seed", "max_steps")
    options = {key: config[key] for key in fields}
    options.update(output_dir=str(Path(output) / "trainer"), num_train_epochs=config["epochs"],
                   per_device_train_batch_size=config["per_device_batch_size"],
                   save_strategy="no", logging_steps=10, report_to="none", remove_unused_columns=False,
                   eval_strategy="no", load_best_model_at_end=False, save_safetensors=True,
                   gradient_checkpointing_kwargs={"use_reentrant": False}, ddp_find_unused_parameters=False,
                   dataloader_num_workers=0, dataloader_drop_last=False, data_seed=config["seed"],
                   accelerator_config={"split_batches": False, "even_batches": True, "use_seedable_sampler": True},
                   deepspeed=deepcopy(config["deepspeed"]))
    return options


def messages(row):
    return [{"role": "user", "content": [{"type": "image"} for _ in row["images"]] +
             [{"type": "text", "text": row["question"]}]}]


class ResponseCollator:
    def __init__(self, processor, media_root, max_length):
        self.processor = processor; self.media_root = media_root; self.max_length = max_length
        self.response_tokens = 0

    def __call__(self, rows):
        from PIL import Image
        images, texts, prompts = [], [], []
        for row in rows:
            pictures = []
            for path in image_paths(row, self.media_root):
                with Image.open(path) as image:
                    pictures.append(image.convert("RGB"))
            chat = messages(row)
            prompt = self.processor.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
            full = self.processor.apply_chat_template(chat + [{"role": "assistant", "content": [{"type": "text", "text": row["answer"]}]}],
                                                       tokenize=False, add_generation_prompt=False)
            prompt_ids = self.processor(text=[prompt], images=pictures, return_tensors="pt")["input_ids"][0]
            prompts.append(prompt_ids); texts.append(full); images.extend(pictures)
        batch = self.processor(text=texts, images=images, padding=True, return_tensors="pt")
        if batch["input_ids"].shape[1] > self.max_length:
            raise ValueError("Example exceeds frozen token limit")
        batch["labels"] = torch.stack([response_labels(ids, prefix, mask) for ids, prefix, mask in
                                       zip(batch["input_ids"], prompts, batch["attention_mask"])])
        self.response_tokens += int((batch["labels"][:, 1:] != -100).sum())
        return batch


def infer(model, processor, rows, media_root, max_new_tokens):
    from PIL import Image
    processor.tokenizer.padding_side = "left"
    model.eval(); outputs = []
    for row in rows:
        pictures = []
        for path in image_paths(row, media_root):
            with Image.open(path) as image:
                pictures.append(image.convert("RGB"))
        prompt = processor.apply_chat_template(messages(row), tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[prompt], images=pictures, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            output = model.generate(**inputs, do_sample=False, num_beams=1, use_cache=True, max_new_tokens=max_new_tokens)
        text = processor.batch_decode(output[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip()
        if not text:
            raise ValueError(f"Empty prediction for {row['id']}")
        outputs.append({"id": row["id"], "prediction": text})
    return outputs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True); parser.add_argument("--media-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--checkpoint", help="Completed checkpoint for inference-only; training uses job.checkpoint_in")
    parser.add_argument("--deepspeed", help="Explicit DeepSpeed config; requires a separate compatible installation")
    parser.add_argument("--inference-only", action="store_true")
    parser.add_argument("--training-record", help="Required for inference-only: the corresponding train_completed.json")
    parser.add_argument("--check-only", action="store_true", help="Verify job, images and training budget without loading a model")
    args = parser.parse_args(argv)
    job_dir = Path(args.job); job = load_json(job_dir / "job.json")
    config = job["learner"]; output = Path(args.output)
    checkpoint = args.checkpoint or job["checkpoint_in"]
    record = None
    if args.inference_only:
        if args.deepspeed:
            raise ValueError("Inference-only loads full weights per GPU and must not use --deepspeed")
        if not args.training_record or not args.checkpoint:
            raise ValueError("Inference-only requires --training-record and --checkpoint for the completed update")
        record = load_json(args.training_record)
        validate_training_record(job, record, record.get("checkpoint"))
        if Path(record["checkpoint"]).resolve() != Path(checkpoint).resolve():
            raise ValueError("Training record does not match this inference checkpoint")
    elif args.training_record:
        raise ValueError("--training-record is only valid with --inference-only")
    elif args.checkpoint and Path(checkpoint).resolve() != Path(job["checkpoint_in"]).resolve():
        raise ValueError("Training must continue from job.checkpoint_in, not a different --checkpoint")
    job, rows, panel = load_training_job(job_dir)
    if args.deepspeed and load_json(args.deepspeed) != config["deepspeed"]:
        raise ValueError("DeepSpeed settings differ from the frozen learner recipe")
    if args.check_only:
        images = verify_media(rows + panel, args.media_root)
        print(json.dumps({"job_id": job["job_id"], "training_budget": job["training_budget"],
                          "verified_images": images, "external_examples_in_training_job": 0}))
        return
    from transformers import AutoModelForImageTextToText, AutoProcessor, Trainer, TrainingArguments
    rank = int(os.environ.get("RANK", 0)); world = int(os.environ.get("WORLD_SIZE", 1))
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    if not args.inference_only and world != config["world_size"]:
        raise ValueError(f"Training requires {config['world_size']} processes; got {world}")
    if not torch.cuda.is_available():
        raise RuntimeError("Qwen3-VL worker requires CUDA; use the CPU mechanism demo instead")
    torch.cuda.set_device(local_rank)
    if world > 1 and not torch.distributed.is_initialized():
        torch.distributed.init_process_group("nccl")
    errors = ["Output must be empty" if rank == 0 and output.exists() and any(output.iterdir()) else None]
    if world > 1:
        torch.distributed.broadcast_object_list(errors, src=0)
    if errors[0]:
        raise ValueError(errors[0])
    media_error = [None]
    if rank == 0:
        try:
            verify_media(rows + panel, args.media_root)
        except (OSError, ValueError) as error:
            media_error[0] = str(error)
    if world > 1:
        torch.distributed.broadcast_object_list(media_error, src=0)
    if media_error[0]:
        raise ValueError(media_error[0])
    processor = AutoProcessor.from_pretrained(checkpoint, local_files_only=True, trust_remote_code=False)
    processor.tokenizer.padding_side = "right"
    train_args = TrainingArguments(**training_kwargs(config, output)) if not args.inference_only else None
    model = AutoModelForImageTextToText.from_pretrained(checkpoint, torch_dtype=torch.bfloat16,
              local_files_only=True, trust_remote_code=False, attn_implementation=config["attention_implementation"])
    if model.config.model_type != "qwen3_vl" or config["backend"] != "qwen3_vl" or not config["bf16"]:
        raise ValueError("This worker implements bf16 Qwen3-VL full SFT")
    if config["freeze_vision"] and not args.inference_only:
        freeze_vision_tower(model)
    start = time.monotonic()
    collator = ResponseCollator(processor, args.media_root, config["max_length"])
    class ResponseTrainer(ResponseNLLMixin, Trainer):
        pass

    final = (output / "checkpoint_final").resolve()
    if not args.inference_only:
        trainer = ResponseTrainer(model=model, args=train_args, train_dataset=rows, data_collator=collator)
        if len(trainer.get_train_dataloader()) != job["training_budget"]["batches_per_rank"]:
            raise ValueError("Distributed data loader differs from the planned training budget")
        trainer.train()
        if trainer.state.global_step != job["training_budget"]["training_steps"]:
            raise ValueError("Student did not complete the prescribed optimizer steps")
        trainer.save_model(str(final))
        if trainer.is_world_process_zero():
            processor.save_pretrained(str(final))
    if world > 1:
        torch.distributed.barrier()
    trained_seconds = time.monotonic() - start if not args.inference_only else None
    response_tokens = torch.tensor(collator.response_tokens, dtype=torch.long, device=torch.device("cuda", local_rank))
    if world > 1: torch.distributed.all_reduce(response_tokens)
    response_count = int(response_tokens) if not args.inference_only else None
    if not args.inference_only:
        record = {k: job[k] for k in ("job_id", "checkpoint_in", "training_digest", "validation_digest", "exclusions_digest")}
        record.update({"checkpoint": str(final), "resolved_checkpoint_in": str(Path(checkpoint).resolve()),
                       "learner_digest": digest(config), "training_steps": trainer.state.global_step,
                       "training_budget": job["training_budget"], "completed_epochs": trainer.state.epoch,
                       "loss_reduction": "response_sum_example_mean",
                       "training_seconds": trained_seconds, "response_tokens": response_count})
        validate_training_record(job, record, str(final))
        if rank == 0:
            dump_json(output / "train_completed.json", record)
            dump_json(output / "learner_settings.json", config)
    else:
        trained_seconds = record["training_seconds"]; response_count = record["response_tokens"]
    if config["deepspeed"] and not args.inference_only:
        if world > 1:
            torch.distributed.barrier()
            torch.distributed.destroy_process_group()
        return
    inference_model = model if args.inference_only else trainer.accelerator.unwrap_model(trainer.model)
    inference_model.to(torch.device("cuda", local_rank))
    predictions = infer(inference_model, processor, panel[rank::world], args.media_root, config["max_new_tokens"])
    output.mkdir(parents=True, exist_ok=True)
    dump_json(output / f"predictions_rank{rank:03d}.json", predictions)
    if world > 1:
        torch.distributed.barrier()
    if rank == 0:
        merged = [p for r in range(world) for p in load_json(output / f"predictions_rank{r:03d}.json")]
        result = {k: job[k] for k in ("job_id", "checkpoint_in", "training_digest", "validation_digest")}
        result.update({"checkpoint_out": record["checkpoint"], "resolved_checkpoint_in": checkpoint,
                       "fixture_mode": False, "predictions": merged, "learner_seconds": trained_seconds,
                       "response_tokens": response_count, "worker_seconds": time.monotonic() - start,
                       "scoring": "not_performed_on_worker", "loss_reduction": "response_sum_example_mean",
                       "training_record": record})
        dump_json(output / "predictions.json", result)
    if world > 1:
        torch.distributed.barrier()
        torch.distributed.destroy_process_group()


def panel_main(argv=None):
    parser = argparse.ArgumentParser(description="Standalone Qwen3-VL panel inference")
    parser.add_argument("--panel", required=True); parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--media-root", required=True); parser.add_argument("--output", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    args = parser.parse_args(argv)
    from transformers import AutoModelForImageTextToText, AutoProcessor
    from .data import write_jsonl
    rank = int(os.environ.get("RANK", 0)); world = int(os.environ.get("WORLD_SIZE", 1))
    local = int(os.environ.get("LOCAL_RANK", 0)); torch.cuda.set_device(local)
    if world > 1:
        torch.distributed.init_process_group("nccl")
    root = Path(args.output)
    errors = ["Output must be empty" if rank == 0 and root.exists() and any(root.iterdir()) else None]
    if world > 1: torch.distributed.broadcast_object_list(errors, src=0)
    if errors[0]: raise ValueError(errors[0])
    root.mkdir(parents=True, exist_ok=True)
    processor = AutoProcessor.from_pretrained(args.checkpoint, local_files_only=True)
    model = AutoModelForImageTextToText.from_pretrained(args.checkpoint, torch_dtype=torch.bfloat16,
                local_files_only=True, attn_implementation="sdpa").to(torch.device("cuda", local))
    panel = read_jsonl(args.panel)
    predictions = infer(model, processor, panel[rank::world], args.media_root, args.max_new_tokens)
    write_jsonl(root / f"rank{rank:03d}.jsonl", predictions)
    if world > 1: torch.distributed.barrier()
    if rank == 0:
        write_jsonl(root / "predictions.jsonl", [p for r in range(world) for p in read_jsonl(root / f"rank{r:03d}.jsonl")])
        dump_json(root / "manifest.json", {"checkpoint": args.checkpoint, "panel_digest": digest(panel),
                  "decoding": "greedy", "max_new_tokens": args.max_new_tokens, "scoring": "not_performed"})


if __name__ == "__main__":
    main()
