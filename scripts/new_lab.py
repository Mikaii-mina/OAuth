#!/usr/bin/env python3
"""Create an isolated experiment from lab00 without generating credentials."""

import argparse
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent.parent


def create_lab(number: int) -> None:
    if number < 1 or number > 99:
        raise ValueError("lab number must be between 1 and 99")
    suffix = f"{number:02d}"
    source = ROOT / "lab00"
    target = ROOT / f"lab{suffix}"
    if target.exists():
        raise FileExistsError(target)
    compose = ROOT / "docker-compose.yaml"
    compose_text = compose.read_text()
    if "secrets:\n" not in compose_text or "          - client-00.oauth.labs\n" not in compose_text:
        raise ValueError("compose file is missing the baseline insertion points")
    caddyfile = ROOT / "docker" / "caddy" / "Caddyfile"
    if not caddyfile.is_file():
        raise ValueError("Caddyfile is missing")

    shutil.copytree(source, target, ignore=shutil.ignore_patterns("bin", "tmp", ".cache", "config.yaml"))
    for path in target.rglob("*"):
        if path.is_file() and path.suffix in {".go", ".mod"}:
            content = path.read_text()
            content = content.replace("lab00", f"lab{suffix}")
            content = content.replace("server-00", f"server-{suffix}")
            content = content.replace("client-00", f"client-{suffix}")
            content = content.replace("server00", f"server{suffix}")
            content = content.replace("client00", f"client{suffix}")
            content = content.replace('LabNumber = "00"', f'LabNumber = "{suffix}"')
            path.write_text(content)

    (target / "scenario.json").write_text(json.dumps({
        "id": f"lab{suffix}",
        "title": "New OAuth experiment",
        "vulnerable_component": "undecided",
        "expected_impact": "undecided",
        "reproduction": "pending",
        "fixed_comparison": "pending",
    }, indent=2) + "\n")
    (target / "README.md").write_text(
        f"# Lab {suffix}\n\nStart from lab00. Use LAB_VARIANT=fixed or vulnerable "
        "to select the implementation of exactly one control. Document the reproduction "
        "and expected impact here. Implement reproduce.py (see its generated contract).\n"
    )
    (target / "reproduce.py").write_text(
        '#!/usr/bin/env python3\n"""Implement the attack and print JSON: '
        '{"exploitable": bool, "impact_verified": bool}."""\n'
        'raise SystemExit("Not implemented: choose a vulnerability and write its reproduction")\n'
    )
    services = f"""  server-{suffix}:
    environment:
      LAB_VARIANT: ${{LAB_VARIANT:-fixed}}
    build:
      context: .
      dockerfile: ./docker/Dockerfile.baselab
      args:
        LAB_NUMBER: '{suffix}'
        COMPONENT: server
    depends_on:
      - caddy
      - db
      - valkey
    volumes:
      - ./docker/lab{suffix}/server.config.yaml:/app/config.yaml
    networks:
      - oauth-labs
    cpus: 1
    mem_limit: 1g

  client-{suffix}:
    environment:
      LAB_VARIANT: ${{LAB_VARIANT:-fixed}}
    build:
      context: .
      dockerfile: ./docker/Dockerfile.baselab
      args:
        LAB_NUMBER: '{suffix}'
        COMPONENT: client
    depends_on:
      - caddy
      - db
      - valkey
      - server-{suffix}
    volumes:
      - ./docker/lab{suffix}/client.config.yaml:/app/config.yaml
    networks:
      - oauth-labs
    cpus: 1
    mem_limit: 1g

"""
    compose_text = compose_text.replace("secrets:\n", services + "secrets:\n", 1)
    compose_text = compose_text.replace(
        "          - client-00.oauth.labs\n",
        f"          - client-00.oauth.labs\n          - server-{suffix}.oauth.labs\n          - client-{suffix}.oauth.labs\n",
        1,
    )
    compose.write_text(compose_text)
    with caddyfile.open("a") as caddy:
        caddy.write(f"""
server-{suffix}.oauth.labs {{
    import common
    reverse_proxy server-{suffix}:3000
}}

client-{suffix}.oauth.labs {{
    import common
    reverse_proxy client-{suffix}:3000
}}
""")
    print(f"Created {target.name}; run `make config` before starting the new lab.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("number", type=int, help="lab number 1–99")
    args = parser.parse_args()
    create_lab(args.number)
