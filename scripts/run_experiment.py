#!/usr/bin/env python3
"""Run both variants of a completed lab in fresh local containers."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def run(number: str) -> None:
    lab = ROOT / f"lab{number}"
    scenario = json.loads((lab / "scenario.json").read_text())
    if scenario.get("id") != lab.name:
        raise ValueError("scenario ID must match the lab directory")
    for field in ("vulnerable_component", "expected_impact", "reproduction", "fixed_comparison"):
        if scenario.get(field) in (None, "", "undecided", "pending"):
            raise ValueError(f"scenario field {field} must be completed before running an experiment")

    reproduction = lab / "reproduce.py"
    if not reproduction.is_file():
        raise FileNotFoundError(reproduction)
    if "Not implemented: choose a vulnerability" in reproduction.read_text():
        raise ValueError("replace the generated reproduction stub before running an experiment")
    compose = ["docker", "compose"]
    try:
        for variant, expected in (("vulnerable", True), ("fixed", False)):
            subprocess.run(compose + ["down", "-v"], cwd=ROOT, check=True)
            environment = {**os.environ, "LAB_VARIANT": variant}
            subprocess.run(
                compose + ["up", "-d", "--build", f"server-{number}", f"client-{number}"],
                cwd=ROOT, env=environment, check=True,
            )
            smoke = [sys.executable, str(ROOT / "scripts" / "smoke.py"), "--lab", number]
            if variant == "vulnerable":
                smoke.append("--health-only")
            subprocess.run(smoke, cwd=ROOT, check=True)
            result = subprocess.run(
                [sys.executable, str(reproduction), "--variant", variant],
                cwd=ROOT, env=environment, capture_output=True, text=True, check=True,
            )
            outcome = json.loads(result.stdout)
            if outcome.get("exploitable") is not expected or outcome.get("impact_verified") is not expected:
                raise AssertionError(f"{variant} result did not match expected={expected}: {outcome}")
            print(f"{lab.name} {variant}: expected outcome confirmed")
    finally:
        subprocess.run(compose + ["down", "-v"], cwd=ROOT, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", required=True, choices=[f"{n:02d}" for n in range(1, 100)])
    args = parser.parse_args()
    run(args.lab)
