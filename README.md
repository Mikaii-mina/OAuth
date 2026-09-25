# OAuth experiment platform

This is a fork of [cyllective/oauth-labs](https://github.com/cyllective/oauth-labs), based on upstream commit `5c97e34c8f18ee64a85306037641b12c53b8137a` (MIT license; see `LICENSE`). It retains the lab00 playground and adds an experiment scaffold and baseline checks. No vulnerability has been selected or implemented yet.

## Requirements

- Docker Engine with Compose and the ability to build containers
- Go 1.23.2 or newer (for configuration generation)
- Free local TCP ports 80 and 443
- DNS/hosts entries resolving `server-00.oauth.labs` and `client-00.oauth.labs` to `127.0.0.1`

Add these entries to `/etc/hosts` (requires administrator access):

```text
127.0.0.1 server-00.oauth.labs client-00.oauth.labs
```

Run **only on a trusted local machine**; Caddy binds to loopback. The first browser visit will show a certificate warning because Caddy issues a local CA certificate. Trust that CA for this isolated lab only if needed.

```sh
make config
make labs
make smoke
docker compose ps
```

Visit `https://server-00.oauth.labs` to register a lab account, then `https://client-00.oauth.labs` to run the authorization-code flow. The client uses `state` and PKCE; `lab00` is a learning playground rather than a verified secure reference implementation. The smoke test checks health, the authorization URL's `state` and S256 PKCE parameters, and rejection of a bogus callback state. It does **not** exercise a complete authenticated flow or prove the implementation secure. It skips verification of the local Caddy CA certificate; never use this script against external hosts. To stop and delete local database data, run `make labsdown`. `make config` regenerates credentials, so stop and remove old volumes before regenerating and restarting.

## Adding future experiments

Keep `lab00` unchanged as the reference playground. To scaffold a new isolated lab, run `python3 scripts/new_lab.py 1` (valid range 1–99). This copies the baseline source, adds Compose services and Caddy routes, and creates `lab01/scenario.json` and `lab01/README.md`. Review the generated files before use. No credentials are copied; `make config` discovers all `labNN` directories and generates new credentials and SQL for all of them. The configuration step **overwrites** all previously generated credentials: use `make labsdown` first, then `make config`, before starting again. Add `127.0.0.1 server-01.oauth.labs client-01.oauth.labs` to `/etc/hosts` for lab01.

Start and inspect a lab with `make lab-up LAB=01` and `make lab-test LAB=01`. `lab-test` checks health, `state`, and PKCE in the fixed version; `python3 scripts/smoke.py --lab 01 --health-only` checks availability without assuming a vulnerability type. `make lab-down` stops **all** services but preserves the named database volume; `make lab-reset` stops everything and deletes **all** Compose volumes. Before shipping an experiment, replace the `undecided`/`pending` fields in its scenario, implement exactly one controlled defect selected by `LAB_VARIANT` (`fixed` or `vulnerable`), and implement `lab01/reproduce.py --variant ...` to print one JSON object with Boolean `exploitable` and `impact_verified` fields. `make experiment LAB=01` runs both variants in turn, waits for health, asserts vulnerable=true/true and fixed=false/false, and **deletes all Compose volumes** before, between, and after runs. Do not run it against existing data. The generated `reproduce.py` deliberately fails until implemented; merely setting `LAB_VARIANT` does not introduce a defect. CI automatically runs both variants for completed scenarios and skips unfinished scaffolds. Do not use these images or generated credentials on public networks.
