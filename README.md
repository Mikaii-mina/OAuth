# OAuth lab baseline

This is a local, lab00-only derivative of [cyllective/oauth-labs](https://github.com/cyllective/oauth-labs), based on upstream commit `5c97e34c8f18ee64a85306037641b12c53b8137a` (MIT license; see `LICENSE`). This checkout is **not** a GitHub fork. No vulnerability experiment or vulnerable/fixed comparison has been added yet.

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
docker compose ps
```

Visit `https://server-00.oauth.labs` to register a lab account, then `https://client-00.oauth.labs` to run the authorization-code flow. The client uses `state` and PKCE; `lab00` is a learning playground rather than a verified secure reference implementation. To stop and delete local database data, run `make labsdown`. `make config` regenerates credentials, so stop and remove old volumes before regenerating and restarting.

## Adding future experiments

Keep `lab00` unchanged as the reference playground. Add a new lab directory with separate server/client code and config generation, then explicitly add the service, Caddy route and SQL database provisioner for that lab. Introduce one controlled defect per experiment and test both its reproduction and its corrected variant. Do not use these images or generated credentials on public networks.

This first step deliberately removes upstream labs 01–05, index and victim simulator. The vulnerable/fixed variants, automatic repro harness, and CI belong to the next step; they are not implemented here.
