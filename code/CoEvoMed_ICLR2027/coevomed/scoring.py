import re
import string
import warnings

from .data import REPORTS, unit_score


def tokens(text):
    text = re.sub(r"<think>.*?</think>", " ", text, flags=re.S | re.I).lower()
    text = text.translate(str.maketrans({c: " " for c in string.punctuation}))
    return [w for w in text.split() if w not in {"a", "an", "the"}]


def report_metrics(prediction, reference):
    from nltk.corpus import wordnet
    from nltk.translate.bleu_score import sentence_bleu
    from nltk.translate.meteor_score import single_meteor_score
    wordnet.ensure_loaded()
    predicted, expected = tokens(prediction), tokens(reference)
    if not predicted or not expected:
        raise ValueError("Empty report prediction/reference")
    previous = [0] * (len(expected) + 1)
    for p in predicted:
        current = [0]
        for i, r in enumerate(expected, 1):
            current.append(previous[i - 1] + 1 if p == r else max(previous[i], current[-1]))
        previous = current
    rouge = 2 * previous[-1] / (len(predicted) + len(expected))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bleu = sentence_bleu([expected], predicted, weights=(0.25,) * 4)
    meteor = single_meteor_score(expected, predicted)
    return {"rougeL": float(rouge), "bleu4": float(bleu), "meteor": float(meteor)}


def option_letter(text):
    text = re.sub(r"^\s*(?:answer|option)\s*(?:is|:)\s*", "", text, flags=re.I)
    match = re.match(r"^\s*([A-D])(?:[.):]|\s|$)", text)
    return match.group(1) if match else None


def score_predictions(panel, predictions, *, agents=None, semantic_open=False, report_scope="full"):
    if report_scope not in {"full", "iu_findings"}:
        raise ValueError("Unknown frozen report scoring scope")
    expected = {r["id"]: r for r in panel}
    if len(expected) != len(panel) or len({r["id"] for r in predictions}) != len(predictions):
        raise ValueError("Duplicate IDs")
    if set(expected) != {r["id"] for r in predictions}:
        raise ValueError("Missing/extra predictions for the fixed evaluation panel")
    result = []
    for prediction in predictions:
        row = expected[prediction["id"]]
        text = prediction["prediction"].strip()
        if not text or prediction.get("error"):
            raise ValueError("Inference error or empty prediction")
        item = {"id": row["id"], "benchmark": row["benchmark"], "role": row["role"], "prediction": text}
        if row["benchmark"] in REPORTS:
            ref, hypothesis = row["answer"], text
            if row["benchmark"] == "iu_xray" and report_scope == "iu_findings":
                ref, hypothesis = findings(ref), findings(hypothesis)
            item["metrics"] = report_metrics(hypothesis, ref)
            item["metric_protocol"] = f"nltk_sentence_bleu4_no_smoothing_meteor_rougeL_v1:{report_scope}"
        else:
            if row["task_form"] == "mcq":
                a, b = option_letter(text), option_letter(row["answer"])
                correct = a == b if a and b else (not a and not b and bool(tokens(text)) and tokens(text) == tokens(row["answer"]))
            else:
                correct = bool(tokens(text)) and tokens(text) == tokens(row["answer"])
            if semantic_open and row["task_form"] in {"open_short", "open_long"}:
                if agents is None:
                    raise ValueError("Semantic matching requires a configured judge")
                verdict = agents.call("judge", "Judge whether the predicted medical answer has the same meaning as the reference "
                                      "given the question. Preserve negation, laterality, anatomy, quantity, and uncertainty. "
                                      "Extra contradictory claims make an answer incorrect.",
                                      {"question": row["question"], "reference": row["answer"], "prediction": text,
                                       "output": {"correct": True, "reason": "..."}})
                if type(verdict.get("correct")) is not bool:
                    raise ValueError("Judge returned invalid correctness")
                correct = verdict["correct"]
            item["correct"] = bool(correct)
            judge_model = getattr(agents, "config", {}).get("judge", "unspecified")
            item["metric_protocol"] = f"semantic_open_v2:{judge_model}" if semantic_open else "exact_v2"
        result.append(item)
    return result


def findings(text):
    match = re.search(r"\bfindings\s*:\s*(.*?)(?:\bimpression\s*:|$)", text, flags=re.I | re.S)
    return match.group(1).strip() if match else text.strip()


def ratescore(predictions, references):
    if len(predictions) != len(references) or not predictions:
        raise ValueError("RaTEScore inputs must be nonempty and paired")
    from RaTEScore import RaTEScore
    values = list(RaTEScore().compute_score(predictions, references))
    if len(values) != len(predictions):
        raise ValueError("RaTEScore returned an incomplete panel")
    return sum(unit_score(float(v)) for v in values) / len(values)
