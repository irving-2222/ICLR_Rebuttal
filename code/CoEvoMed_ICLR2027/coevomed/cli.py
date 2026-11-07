import argparse
import json
from pathlib import Path

from .data import dump_json, load_json, read_jsonl, write_jsonl


def main(argv=None):
    parser = argparse.ArgumentParser(description="CoEvoMed paper-aligned demo and split execution")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo")
    demo.add_argument("--output", required=True); demo.add_argument("--rounds", type=int, default=6)
    init = commands.add_parser("init")
    init.add_argument("--config", required=True); init.add_argument("--inputs", required=True)
    init.add_argument("--baseline", required=True); init.add_argument("--actor", required=True)
    init.add_argument("--checkpoint", required=True); init.add_argument("--run", required=True)
    for command in ("prepare", "complete"):
        item = commands.add_parser(command); item.add_argument("--run", required=True)
        item.add_argument("--media-root", required=True)
        if command == "complete": item.add_argument("--result", required=True)
    score = commands.add_parser("score")
    score.add_argument("--job", required=True); score.add_argument("--result", required=True)
    score.add_argument("--output", required=True); score.add_argument("--config", required=True)
    score.add_argument("--media-root", default=".")
    panel_score = commands.add_parser("score-panel")
    panel_score.add_argument("--panel", required=True); panel_score.add_argument("--predictions", required=True)
    panel_score.add_argument("--output", required=True); panel_score.add_argument("--config", required=True)
    panel_score.add_argument("--media-root", default=".")
    bc = commands.add_parser("pretrain")
    bc.add_argument("--labeled-states", required=True); bc.add_argument("--output", required=True)
    teacher = commands.add_parser("teacher-data")
    teacher.add_argument("--baseline-summary", required=True); teacher.add_argument("--config", required=True)
    teacher.add_argument("--output", required=True)
    summarize = commands.add_parser("summarize")
    summarize.add_argument("--panel", required=True); summarize.add_argument("--outcomes", required=True)
    summarize.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if args.command == "demo":
        from .demo import run_demo
        run_demo(args.output, args.rounds); return
    if args.command == "summarize":
        from .feedback import summary
        dump_json(args.output, summary(read_jsonl(args.panel), read_jsonl(args.outcomes))); return
    if args.command == "pretrain":
        from .pretrain import train_actor
        metrics = train_actor(read_jsonl(args.labeled_states), args.output)
        print(json.dumps({k: v for k, v in metrics.items() if k != "history"})); return
    if args.command == "teacher-data":
        from .pretrain import build_states, teacher_label
        from .agents import APIAgents
        config = load_json(args.config); agents = APIAgents(config["agents"], ".")
        rows = build_states(load_json(args.baseline_summary), horizon=config["horizon"])
        write_jsonl(args.output, teacher_label(rows, agents, config["workers"])); return
    if args.command == "score":
        from .scoring import score_predictions
        config = load_json(args.config); result = load_json(args.result)
        agents = None
        if config["metrics"]["semantic_open"]:
            from .agents import APIAgents
            agents = APIAgents(config["agents"], args.media_root)
        result["outcomes"] = score_predictions(read_jsonl(Path(args.job) / "validation.jsonl"), result.pop("predictions"),
            agents=agents, semantic_open=config["metrics"]["semantic_open"], report_scope=config["metrics"]["report_scope"])
        dump_json(args.output, result); return
    if args.command == "score-panel":
        from .scoring import score_predictions
        config = load_json(args.config); agents = None
        if config["metrics"]["semantic_open"]:
            from .agents import APIAgents
            agents = APIAgents(config["agents"], args.media_root)
        outcomes = score_predictions(read_jsonl(args.panel), read_jsonl(args.predictions), agents=agents,
                                    semantic_open=config["metrics"]["semantic_open"], report_scope=config["metrics"]["report_scope"])
        write_jsonl(args.output, outcomes); return
    from .runner import Runner
    if args.command == "init":
        p = Path(args.inputs)
        original = read_jsonl(p / "train.jsonl") if (p / "train.jsonl").exists() else []
        baseline = read_jsonl(args.baseline)
        Runner.initialize(args.run, load_json(args.config), read_jsonl(p / "support.jsonl"),
                          read_jsonl(p / "validation.jsonl"), read_jsonl(p / "external.jsonl"), baseline,
                          original=original, actor_path=args.actor, checkpoint=args.checkpoint)
        return
    from .agents import APIAgents
    config = load_json(Path(args.run) / "config.json")
    runner = Runner(args.run, APIAgents(config["agents"], args.media_root))
    if args.command == "prepare": print(runner.prepare())
    else: print(json.dumps(runner.complete(load_json(args.result)), indent=2))


if __name__ == "__main__":
    main()
