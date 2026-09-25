import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "new_lab", Path(__file__).resolve().parents[1] / "scripts" / "new_lab.py"
)
new_lab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(new_lab)


class NewLabTests(unittest.TestCase):
    def test_generates_isolated_lab_and_routing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "lab00" / "client").mkdir(parents=True)
            (root / "lab00" / "server").mkdir()
            (root / "lab00" / "client" / "go.mod").write_text("module example/lab00/client\n")
            (root / "lab00" / "server" / "go.mod").write_text("module example/lab00/server\n")
            (root / "lab00" / "client" / "config.yaml").write_text("do not copy")
            (root / "lab00" / "server" / "main.go").write_text('const LabNumber = "00"\n')
            (root / "lab00" / "client" / "client.go").write_text(
                'package client\nconst host = "client-00.oauth.labs"\nconst database = "client00"\n'
            )
            (root / "docker" / "caddy").mkdir(parents=True)
            (root / "docker" / "caddy" / "Caddyfile").write_text("baseline\n")
            (root / "docker-compose.yaml").write_text(
                "services:\n  caddy:\n    networks:\n      oauth-labs:\n"
                "        aliases:\n          - client-00.oauth.labs\nsecrets:\n  root: {}\n"
            )

            with patch.object(new_lab, "ROOT", root):
                new_lab.create_lab(1)
                with self.assertRaises(FileExistsError):
                    new_lab.create_lab(1)

            self.assertEqual((root / "lab01" / "server" / "main.go").read_text(), 'const LabNumber = "01"\n')
            self.assertIn("lab01/client", (root / "lab01" / "client" / "go.mod").read_text())
            self.assertIn("client-01.oauth.labs", (root / "lab01" / "client" / "client.go").read_text())
            self.assertIn("client01", (root / "lab01" / "client" / "client.go").read_text())
            self.assertFalse((root / "lab01" / "client" / "config.yaml").exists())
            self.assertIn("server-01.oauth.labs", (root / "docker" / "caddy" / "Caddyfile").read_text())
            self.assertIn("client-01:", (root / "docker-compose.yaml").read_text())
            self.assertIn("lab01", (root / "lab01" / "scenario.json").read_text())

    def test_rejects_baseline_number(self):
        with self.assertRaises(ValueError):
            new_lab.create_lab(0)


if __name__ == "__main__":
    unittest.main()
