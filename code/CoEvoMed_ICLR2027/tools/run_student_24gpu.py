import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys

from coevomed.data import load_training_job


def launch_command(args):
    job, _, _ = load_training_job(args.job)
    if job["learner"]["world_size"] != 24:
        raise ValueError("The 24-GPU launcher requires a 24-process training recipe")
    ds = job["learner"]["deepspeed"]
    if not ds or ds.get("zero_optimization", {}).get("stage") != 3:
        raise ValueError("The 24-GPU launcher requires the frozen ZeRO-3 configuration")
    output = Path(args.output).resolve()
    worker = ["-m", "coevomed.student_worker", "--job", str(Path(args.job).resolve()),
              "--media-root", str(Path(args.media_root).resolve())]
    if args.mode == "check":
        return [sys.executable, *worker, "--output", str(output / "check"), "--check-only"], job
    if args.node_rank not in (0, 1, 2) or not args.master_addr or not 1 <= args.master_port <= 65535:
        raise ValueError("Specify --node-rank 0/1/2 and the same --master-addr/--master-port on all nodes")
    command = [sys.executable, "-m", "torch.distributed.run", "--nnodes=3", "--nproc-per-node=8",
               f"--node-rank={args.node_rank}", f"--master-addr={args.master_addr}",
               f"--master-port={args.master_port}", "--max-restarts=0",
               "--log-dir", str(output / "logs" / args.mode / f"node_{args.node_rank}"), "--redirects=3", "--tee=3"]
    command.extend(worker)
    if args.mode == "train":
        command.extend(["--output", str(output / "train")])
    else:
        command.extend(["--output", str(output / "answers"), "--inference-only",
                        "--checkpoint", str(output / "train/checkpoint_final"),
                        "--training-record", str(output / "train/train_completed.json")])
    return command, job


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "train", "answer"))
    parser.add_argument("--job", required=True)
    parser.add_argument("--media-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--node-rank", type=int, choices=(0, 1, 2))
    parser.add_argument("--master-addr")
    parser.add_argument("--master-port", type=int, default=29500)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    command, job = launch_command(args)
    print(json.dumps({"job_id": job["job_id"], "checkpoint_in": job["checkpoint_in"],
                      "budget": job["training_budget"], "command": shlex.join(command)}, indent=2), flush=True)
    if not args.dry_run:
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
