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

## 团队使用流程

队友使用相同的启动流程，但每台电脑的 Docker 数据卷和配置文件都是本地的，不从 GitHub 共享。

**首次使用（每台电脑只需一次）：**安装并启动 Docker Desktop、安装 Go 1.23.2+，按上文配置 `/etc/hosts`，然后运行：

```sh
git clone https://github.com/Mikaii-mina/OAuth.git
cd OAuth
make config
make lab00
docker compose ps
make smoke
```

**日常使用：**先启动 Docker Desktop，在仓库目录运行 `make lab00`，确认 `docker compose ps` 中 `caddy`、`db`、`valkey`、`server-00` 和 `client-00` 均为 `Up`，再运行 `make smoke`。打开 `https://server-00.oauth.labs/register` 注册实验账号，然后访问 `https://client-00.oauth.labs` 演示授权流程。用完执行 `make lab-down`，保留本地实验数据。

**需要清空环境时：**运行 `make lab-reset`、`make config`、`make lab00`、`make smoke`。`make lab-reset` 会删除本地数据库数据；不要单独运行 `make config`，否则新密码可能与旧数据库卷不一致。配置文件和凭据已被 Git 忽略，不要手动提交。

The client uses `state` and PKCE; `lab00` is a learning playground rather than a verified secure reference implementation. The smoke test checks health, the authorization URL's `state` and S256 PKCE parameters, and rejection of a bogus callback state. It does **not** exercise a complete authenticated flow or prove the implementation secure. It skips verification of the local Caddy CA certificate; never use this script against external hosts.

## Adding future experiments

Keep `lab00` unchanged as the reference playground. To scaffold a new isolated lab, run `python3 scripts/new_lab.py 1` (valid range 1–99). This copies the baseline source, adds Compose services and Caddy routes, and creates `lab01/scenario.json` and `lab01/README.md`. Review the generated files before use. No credentials are copied; `make config` discovers all `labNN` directories and generates new credentials and SQL for all of them. The configuration step **overwrites** all previously generated credentials: use `make labsdown` first, then `make config`, before starting again. Add `127.0.0.1 server-01.oauth.labs client-01.oauth.labs` to `/etc/hosts` for lab01.

Start and inspect a lab with `make lab-up LAB=01` and `make lab-test LAB=01`. `lab-test` checks health, `state`, and PKCE in the fixed version; `python3 scripts/smoke.py --lab 01 --health-only` checks availability without assuming a vulnerability type. `make lab-down` stops **all** services but preserves the named database volume; `make lab-reset` stops everything and deletes **all** Compose volumes. Before shipping an experiment, replace the `undecided`/`pending` fields in its scenario, implement exactly one controlled defect selected by `LAB_VARIANT` (`fixed` or `vulnerable`), and implement `lab01/reproduce.py --variant ...` to print one JSON object with Boolean `exploitable` and `impact_verified` fields. `make experiment LAB=01` runs both variants in turn, waits for health, asserts vulnerable=true/true and fixed=false/false, and **deletes all Compose volumes** before, between, and after runs. Do not run it against existing data. The generated `reproduce.py` deliberately fails until implemented; merely setting `LAB_VARIANT` does not introduce a defect. CI automatically runs both variants for completed scenarios and skips unfinished scaffolds. Do not use these images or generated credentials on public networks.
