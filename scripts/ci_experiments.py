#!/usr/bin/env python3
"""Run completed lab scenarios; leave incomplete scaffolds for later work."""

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
PENDING = {None, "", "undecided", "pending"}
REQUIRED = ("vulnerable_component", "expected_impact", "reproduction", "fixed_comparison")


def completed_labs(root: Path):
    for scenario_path in sorted(root.glob("lab[0-9][0-9]/scenario.json")):
        scenario = json.loads(scenario_path.read_text())
        if scenario.get("id") != scenario_path.parent.name:
            raise ValueError(f"incorrect scenario ID in {scenario_path}")
        if all(scenario.get(field) not in PENDING for field in REQUIRED):
            yield scenario_path.parent.name[3:]


if __name__ == "__main__":
    for number in completed_labs(ROOT):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "run_experiment.py"), "--lab", number], check=True)
