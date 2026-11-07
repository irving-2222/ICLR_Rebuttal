import base64
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from difflib import SequenceMatcher
import json
import mimetypes
import os
from pathlib import Path
import re
import threading
import time

from .data import AXES, digest


class AgentCallError(RuntimeError):
    pass


class APIAgents:
    def __init__(self, config, media_root):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.environ["COEVOMED_API_KEY"], base_url=os.environ["COEVOMED_BASE_URL"],
                             timeout=config.get("timeout", 300), max_retries=2)
        self.config = config
        self.media_root = Path(media_root).resolve()
        self.usage = []; self.lock = threading.Lock()

    def call(self, role, system, payload, images=()):
        from openai import APIConnectionError, APIStatusError
        start = time.monotonic()
        content = [{"type": "text", "text": json.dumps(payload, ensure_ascii=True)}]
        for name in images:
            path = (self.media_root / name).resolve()
            if not path.is_relative_to(self.media_root):
                raise ValueError("Image path escapes configured media root")
            content.append({"type": "image_url", "image_url": {"url":
                f"data:{mimetypes.guess_type(path)[0] or 'image/png'};base64," + base64.b64encode(path.read_bytes()).decode()}})
        response, error_type = None, None
        try:
            response = self.client.chat.completions.create(
                model=self.config[role], temperature=0,
                messages=[{"role": "system", "content": system + " Return a JSON object only."},
                          {"role": "user", "content": content}], response_format={"type": "json_object"},
                max_tokens=self.config.get("max_tokens", 3000))
            if not response.choices:
                raise ValueError("Agent returned no choices")
            value = json.loads(response.choices[0].message.content or "")
            if not isinstance(value, dict):
                raise ValueError("Agent did not return an object")
            return value
        except APIConnectionError as error:
            error_type = type(error).__name__
            raise AgentCallError(f"{role}: {error_type}") from error
        except APIStatusError as error:
            error_type = type(error).__name__
            if error.status_code in {408, 409, 429} or error.status_code >= 500:
                raise AgentCallError(f"{role}: {error_type}") from error
            raise
        except (ValueError, TypeError) as error:
            error_type = type(error).__name__
            raise
        finally:
            with self.lock:
                self.usage.append({"role": role, "model": self.config[role], "elapsed_seconds": time.monotonic() - start,
                                   "tokens": response.usage.model_dump() if response and response.usage else None,
                                   "error_type": error_type})

    def plan(self, cell, lane):
        result = self.call("planner", "Translate learning responses into a data-rewriting target. Summarize residual errors; "
                           "never reproduce any full validation question. Do not change task axes or quota.",
                           {"cell": cell, "lane": lane, "output": {"intent": "specific construction objective"}})
        if not str(result.get("intent", "")).strip():
            raise ValueError("Planner returned no target")
        return result["intent"]

    def select_evidence(self, candidates, *, target, lane, intent, count):
        result = self.call("selector", "Select supporting medical evidence for the supplied construction target. "
                           "All candidates already match the task and capability attributes. Rank your choices by "
                           "relevance to the target and coverage of supported facts. Use only supplied source IDs; "
                           "return exactly the requested number of distinct IDs. Do not rewrite or invent facts.",
                           {"target": target, "lane": lane, "intent": intent, "count": count,
                            "candidates": [{"source_id": r["id"], "evidence_id": r["evidence_id"], "facts": r["facts"]}
                                           for r in candidates],
                            "output": {"source_ids": ["selected source ID in order of preference"]}})
        return result.get("source_ids")

    def construct(self, assignment, principle):
        source = assignment["source"]
        return self.call("constructor", "Create evidence-grounded medical supervision. You cannot inspect an image. "
                         "Only the selected facts justify the answer. Apply the construction principle, keep axes fixed, "
                         "preserve negation and laterality. Never invent medical evidence. MCQ requires four options "
                         "and one correct letter; reports use the configured report request and source-supported sections.",
                         {"facts": source["facts"], "target": assignment["target"], "benchmark": assignment["benchmark"],
                          "lane": assignment["lane"], "intent": assignment.get("intent", ""),
                          "principle": principle["strategy"],
                          "output": {"question": "...", "answer": "...", "fact_ids": ["supported fact ID"]}})

    def verify(self, assignment, candidate):
        return self.call("verifier", "Inspect all source images and facts. Check factual consistency, image dependence, "
                         "medical task alignment, correct task form, and answer validity. Fail unsupported findings, "
                         "incorrect option answers, invented comparisons, or invalid report sections.",
                         {"target": assignment["target"], "facts": assignment["source"]["facts"], "candidate": candidate,
                          "output": {"factual": True, "visual": True, "aligned": True, "valid": True, "reason": "..."}},
                         images=assignment["source"]["images"])

    def revise(self, active, cells):
        extracted = self.call("revision", "Extract non-copying error semantics from validation cases. Retain useful medical "
                              "terms, but no complete questions or case identifiers. Recommend rewriting operations, not quality warnings.",
                              {"cells": cells, "output": {"error_semantics": ["..."], "rewrite_targets": ["..."]}})
        proposal = self.call("revision", "Revise one or two question/answer/contrast/diversity strategy fields. Preserve "
                             "semantic_goal and hard_constraints exactly. Alter evidence-response relationships, not just synonyms. "
                             "The principle cannot add facts; each use must stay conditional on available evidence.",
                             {"current": active, "feedback": extracted,
                              "output": {"strategy": active["strategy"], "reason": "error-linked revision"}})
        return proposal["strategy"], proposal["reason"], extracted

    def review(self, active, candidate, feedback, pairs):
        """Semantic assessment is a second step of the revision agent."""
        return self.call("revision", "Compare current and candidate supervision on identical evidence and targets. "
                         "Confirm an observable semantic change, better alignment with the residual errors, and preserved factual support. "
                         "Style-only and synonym-only changes do not count. Judge the displayed examples, not the proposal's claim.",
                         {"current_principle": active, "candidate_principle": candidate, "feedback": feedback, "pairs": pairs[:30],
                          "output": {"applied": True, "alignment": "improved|same|worse",
                                     "evidence_preserved": True, "reason": "paired evidence"}})


def normalize(text):
    return " ".join(re.findall(r"\w+", text.casefold()))


def near_validation_copy(question, validation_questions):
    q = normalize(question)
    return any(q == normalize(v) or (len(q.split()) >= 5 and
               SequenceMatcher(None, q, normalize(v)).ratio() >= 0.9) for v in validation_questions)


def generate_batch(assignments, registry, agents, validation_questions, *, workers=8, override=None):
    def process(assignment):
        try:
            principle = override or registry.active(assignment["principle_id"])
            candidate = agents.construct(assignment, principle)
            if not isinstance(candidate.get("question"), str) or not candidate["question"].strip():
                raise ValueError("empty_question")
            if not isinstance(candidate.get("answer"), str) or not candidate["answer"].strip():
                raise ValueError("empty_answer")
            facts = {f["id"] for f in assignment["source"]["facts"]}
            if not candidate.get("fact_ids") or not set(candidate["fact_ids"]) <= facts:
                raise ValueError("unsupported_fact_ids")
            if assignment["target"]["task_form"] != "report_gen" and near_validation_copy(candidate["question"], validation_questions):
                raise ValueError("validation_question_copy")
            verdict = agents.verify(assignment, candidate)
            if not all(verdict.get(k) is True for k in ("factual", "visual", "aligned", "valid")):
                raise ValueError("verifier_rejected: " + str(verdict.get("reason", "")))
            source = assignment["source"]
            row = {**{k: source[k] for k in ("evidence_id", "images")}, **assignment["target"],
                   "id": assignment["id"], "role": "train", "benchmark": assignment["benchmark"],
                   "source_id": source["id"], "fact_ids": candidate["fact_ids"], "lane": assignment["lane"],
                   "principle_id": principle["id"], "principle_version": principle["version"],
                   "question": candidate["question"], "answer": candidate["answer"], "verifier": verdict}
            row.update({k: source[k] for k in ("image_rgb_sha256", "study_id", "split_provenance") if k in source})
            if "toy_features" in source:
                row["toy_features"] = source["toy_features"]; row["toy_label"] = source["toy_label"]
            return row, None
        except (ValueError, KeyError, TypeError, AgentCallError) as error:
            return None, {"assignment_id": assignment["id"], "reason": str(error),
                          "failure_type": "api" if isinstance(error, AgentCallError) else "validation"}
    for assignment in assignments:
        registry.active(assignment["principle_id"])
    with ThreadPoolExecutor(max_workers=workers) as executor:
        completed = list(executor.map(process, assignments))
    accepted, rejected, seen = [], [], set()
    for row, error in completed:
        if error:
            rejected.append(error); continue
        key = digest([row["evidence_id"], normalize(row["question"]), normalize(row["answer"])])
        if key in seen:
            rejected.append({"assignment_id": row["id"], "reason": "duplicate_supervision"})
        else:
            seen.add(key); accepted.append(row)
    return accepted, rejected
