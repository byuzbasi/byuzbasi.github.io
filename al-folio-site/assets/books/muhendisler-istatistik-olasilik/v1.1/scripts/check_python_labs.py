"""Run every standalone Python lab through the same non-interactive pathway."""

from __future__ import annotations

import os
import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = ROOT / "labs" / "python"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="Use 64 numerical replications; do not reproduce full-study estimates.")
    args = parser.parse_args()
    labs = sorted(LAB_DIR.glob("*.py"))
    if not labs:
        raise SystemExit("No Python labs found.")

    environment = os.environ.copy()
    environment.setdefault("MPLBACKEND", "Agg")
    if args.smoke:
        environment["BOOK_SMOKE"] = "1"
    print("Mode: " + ("SMOKE (64 replications)" if environment.get("BOOK_SMOKE") == "1" else "REFERENCE"), flush=True)
    failures: list[str] = []
    for lab in labs:
        completed = subprocess.run(
            [sys.executable, str(lab)],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if completed.returncode != 0:
            failures.append(
                f"{lab.name}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )
        else:
            print(f"PASS {lab.name}")

    if failures:
        raise SystemExit("\n\n".join(failures))
    print(f"Python lab checks passed for {len(labs)} file(s).")


if __name__ == "__main__":
    main()
