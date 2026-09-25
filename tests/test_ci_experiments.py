import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "ci_experiments", Path(__file__).resolve().parents[1] / "scripts" / "ci_experiments.py"
)
ci_experiments = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ci_experiments)


class DiscoveryTests(unittest.TestCase):
    def test_only_completed_scenarios_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, reproduction in (("lab01", "pending"), ("lab02", "reproduce.py")):
                lab = root / name
                lab.mkdir()
                (lab / "scenario.json").write_text(json.dumps({
                    "id": name, "vulnerable_component": "client",
                    "expected_impact": "test", "reproduction": reproduction,
                    "fixed_comparison": "LAB_VARIANT=fixed",
                }))
            self.assertEqual(list(ci_experiments.completed_labs(root)), ["02"])


if __name__ == "__main__":
    unittest.main()
