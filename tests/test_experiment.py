import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "run_experiment", Path(__file__).resolve().parents[1] / "scripts" / "run_experiment.py"
)
experiment = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(experiment)


class ExperimentTests(unittest.TestCase):
    def test_unfinished_scenario_does_not_touch_docker(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lab = root / "lab01"
            lab.mkdir()
            (lab / "scenario.json").write_text(json.dumps({
                "id": "lab01", "vulnerable_component": "undecided",
                "expected_impact": "undecided", "reproduction": "pending",
                "fixed_comparison": "pending",
            }))
            with patch.object(experiment, "ROOT", root), patch.object(experiment.subprocess, "run") as command:
                with self.assertRaises(ValueError):
                    experiment.run("01")
                command.assert_not_called()

    def test_unimplemented_reproduction_does_not_touch_docker(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lab = root / "lab01"
            lab.mkdir()
            (lab / "scenario.json").write_text(json.dumps({
                "id": "lab01", "vulnerable_component": "client",
                "expected_impact": "test", "reproduction": "reproduce.py",
                "fixed_comparison": "LAB_VARIANT=fixed",
            }))
            (lab / "reproduce.py").write_text(
                'raise SystemExit("Not implemented: choose a vulnerability")\n'
            )
            with patch.object(experiment, "ROOT", root), patch.object(experiment.subprocess, "run") as command:
                with self.assertRaises(ValueError):
                    experiment.run("01")
                command.assert_not_called()

    def test_variants_are_run_and_compared(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lab = root / "lab01"
            lab.mkdir()
            (lab / "scenario.json").write_text(json.dumps({
                "id": "lab01", "vulnerable_component": "client",
                "expected_impact": "test", "reproduction": "reproduce.py",
                "fixed_comparison": "LAB_VARIANT=fixed",
            }))
            (lab / "reproduce.py").write_text("# test\n")
            variants = []

            def fake_run(args, **kwargs):
                if "--variant" in args:
                    variant = args[-1]
                    variants.append(variant)
                    exploitable = variant == "vulnerable"
                    return type("Result", (), {"stdout": json.dumps({
                        "exploitable": exploitable, "impact_verified": exploitable,
                    })})()
                return None

            with patch.object(experiment, "ROOT", root), patch.object(
                experiment.subprocess, "run", side_effect=fake_run
            ) as command:
                experiment.run("01")
                self.assertEqual(variants, ["vulnerable", "fixed"])
                self.assertEqual(sum(args.args[0][2:4] == ["down", "-v"] for args in command.call_args_list), 3)


if __name__ == "__main__":
    unittest.main()
