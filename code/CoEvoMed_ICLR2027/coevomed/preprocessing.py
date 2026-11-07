from collections import defaultdict
import hashlib
from pathlib import Path
import random
import re

from .data import ABILITIES, REPORTS, digest


def task_form(question, answer, benchmark):
    if benchmark in REPORTS:
        return "report_gen"
    if all(re.search(rf"(?:^|\s){letter}\s*[:.)]", question) for letter in "ABCD"):
        return "mcq"
    if answer.strip().lower().strip(".! ") in {"yes", "no", "true", "false"}:
        return "closed_binary"
    return "open_short" if len(re.findall(r"\b\w+\b", answer)) <= 5 else "open_long"


def rgb_digest(path):
    from PIL import Image
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        h = hashlib.sha256(str(rgb.size).encode()); h.update(rgb.tobytes())
        return h.hexdigest()


def report_sections(row):
    structured = {key: row[key].strip() for key in ("findings", "impression")
                  if isinstance(row.get(key), str) and row[key].strip()}
    if structured:
        return structured
    text = row.get("answer", "").strip()
    headings = list(re.finditer(r"\b(findings|impression)\s*:", text, flags=re.I))
    if not headings:
        return {"unsectioned": text} if text else {}
    result = {}
    prefix = text[:headings[0].start()].strip()
    if prefix:
        result["unsectioned"] = prefix
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end():end].strip()
        if body:
            key = heading.group(1).lower()
            result[key] = (result.get(key, "") + " " + body).strip()
    return result


def normalize_native(row, *, role, media_root, agents=None):
    from .data import validate_record
    if row.get("split_provenance") in {None, "", "unknown"}:
        raise ValueError("Original split provenance is required")
    if role in {"validation", "support", "train"} and row.get("reserved_external", False):
        raise ValueError("An external evaluation record cannot enter adaptive feedback or training")
    result = dict(row); result["role"] = role
    result["task_form"] = row.get("task_form") or task_form(row.get("question", ""), row.get("answer", ""), row["benchmark"])
    result["image_rgb_sha256"] = [rgb_digest(Path(media_root) / p) for p in row["images"]]
    if row["benchmark"] in REPORTS:
        result.update({"visual_ability": "holistic_description", "modality": "chest_xray", "anatomy": "chest"})
    if row.get("source_kind") == "report":
        result["report_sections"] = report_sections(row)
    if row["benchmark"] not in REPORTS and not all(row.get(k) for k in ("visual_ability", "modality", "anatomy")):
        if agents is None:
            raise ValueError("Missing axes require the vision annotator")
        labels = agents.call("verifier", "Assign one principal visual capability and evidence attributes. Keep known "
                             "modality unchanged. Use unknown/other when unsupported; do not guess.",
                             {"question": row.get("question"), "reference": row.get("answer"),
                              "visual_capability_enum": ABILITIES, "known_modality": row.get("modality"),
                              "output": {"visual_ability": "...", "modality": "...", "anatomy": "..."}}, images=row["images"])
        for k in ("visual_ability", "modality", "anatomy"):
            result[k] = row.get(k) or labels[k]
    if role == "support" and not row.get("facts"):
        if row.get("source_kind") in {"qa", "classification"}:
            text = f"Question: {row.get('question', '')} Supported answer: {row['answer']}"
            facts = [text]
        elif row.get("source_kind") == "report":
            facts = [{"text": text.strip(), "section": section}
                     for section, body in result["report_sections"].items()
                     for text in re.split(r"(?<=[.!?])\s+", body) if text.strip()]
        else:
            if agents is None:
                raise ValueError("Caption-to-fact extraction requires the configured model")
            extracted = agents.call("verifier", "Extract atomic facts explicitly supported by the supplied caption and image. "
                                    "Keep negation, laterality, and uncertainty. Do not infer new diagnoses or clinical history.",
                                    {"caption": row.get("source_text", ""), "output": {"facts": ["..."]}}, images=row["images"])
            facts = extracted["facts"]
        result["facts"] = [{"id": f"{row['id']}-f{i}", **(fact if isinstance(fact, dict) else {"text": fact})}
                           for i, fact in enumerate(facts)]
    validate_record(result, role)
    return result


def stratified_validation(rows, count=500, seed=42):
    if len({r["benchmark"] for r in rows}) != 1:
        raise ValueError("Select each task's validation panel separately; count is per task")
    if len(rows) < count:
        raise ValueError(f"Only {len(rows)} eligible validation examples; requested {count}")
    if any(r["role"] != "validation" for r in rows):
        raise ValueError("Selection is restricted to an independently assigned validation pool")
    groups = defaultdict(list)
    for r in rows:
        mcq_letter = ""
        if r["task_form"] == "mcq":
            from .scoring import option_letter
            mcq_letter = option_letter(r["answer"]) or "unknown"
        key = (r.get("language", "unknown"), r["task_form"], r["visual_ability"], len(r["images"]),
               mcq_letter, min(len(r["question"].split()) // 10, 4))
        groups[key].append(r)
    from .curriculum import largest_remainder
    keys = sorted(groups)
    quotas = largest_remainder(count, [len(groups[k]) for k in keys])
    result = []
    for key, quota in zip(keys, quotas):
        rng = random.Random(int(digest([seed, key])[:16], 16))
        result.extend(rng.sample(sorted(groups[key], key=lambda r: r["id"]), quota))
    return result


def deduplicate_support(rows):
    from .data import identity_tokens
    seen = set(); retained = []; rejected = []
    for row in rows:
        keys = {t for t in identity_tokens(row) if t[0] in {"id", "image", "rgb"}}
        if keys & seen:
            rejected.append({"id": row["id"], "reason": "duplicate_id_path_or_rgb"})
        else:
            retained.append(row); seen.update(keys)
    return retained, rejected
