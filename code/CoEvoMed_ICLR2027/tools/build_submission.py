import argparse
import ast
import json
from pathlib import Path
import re
import zipfile

ALLOWED_TOP = {"coevomed", "configs", "tests", "tools", "docs"}
ALLOWED_ROOT = {"README.md", "pyproject.toml", "NOTICE.md", "requirements-demo.txt"}
SUFFIXES = {".py", ".md", ".json", ".toml", ".txt"}
FORBIDDEN = [r"sk-[A-Za-z0-9]{12,}", r"/cpfs\d+/", r"/home/[A-Za-z0-9_]+/", r"/Users/[A-Za-z0-9_]+/",
             r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", r"cfff-[0-9a-f]{8,}",
             r"why_[0-9]+", "wang" + "haoyu", "xiao" + "xinyu", r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"]


def audit(root):
    files, errors = [], []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if "__pycache__" in rel.parts or any(p.startswith(".") for p in rel.parts):
            continue
        if rel.parts[0] not in ALLOWED_TOP and str(rel) not in ALLOWED_ROOT:
            continue
        if path.suffix not in SUFFIXES:
            errors.append(f"Unexpected binary/type: {rel}"); continue
        if path.is_symlink():
            errors.append(f"Symlink: {rel}"); continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN:
            if re.search(pattern, text): errors.append(f"Possible identifier/secret: {rel} ({pattern})")
        if path.suffix == ".py":
            ast.parse(text, filename=str(rel))
        elif path.suffix == ".json":
            json.loads(text)
        files.append(path)
    if errors:
        raise ValueError("\n".join(errors))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    files = audit(root)
    output = Path(args.output)
    if output.exists():
        raise ValueError("Archive already exists; use a new filename or explicitly remove your old build")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            info = zipfile.ZipInfo("CoEvoMed/" + path.relative_to(root).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP integrity verification failed")
    print(json.dumps({"files": len(files), "archive_bytes": output.stat().st_size, "anonymity_scan": "passed",
                      "note": "Automated checks supplement, not replace, author anonymity review."}))


if __name__ == "__main__":
    main()
