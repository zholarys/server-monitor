# Server Monitor

Linux host CPU, RAM and root-filesystem monitoring with Telegram notifications. In Compose, psutil reads the explicitly mounted host `/proc` and measures the mounted host root filesystem, rather than implicitly treating the container filesystem as the server root. This does not measure per-container limits; Docker Desktop reports its Linux VM, not the Windows/macOS host.

## Run

```bash
cp .env.example .env
# Set your own bot token and authorized destination chat.
docker compose up --build -d
docker compose logs -f
```

Host mounts expose host information to this collector. It runs as a non-root user with dropped capabilities and a read-only container filesystem. On restricted hosts, verify that the configured host metric paths are readable.

Requests have connection/read timeouts and HTTP/API success checks. Delivery failures are logged without the token-bearing URL and retried on later metric samples. Sustained high usage sends at most one successful reminder per resource per 15 minutes; recovery is sent after a successfully notified incident clears. State is in memory and resets after restart. Thresholds, cooldown and polling interval are configured in Compose.

`Notification delivered` confirms API acceptance, not that a human read it. If the collector stops, it cannot report its own absence: use independent uptime/freshness monitoring. Rotate any credentials previously exposed in Git history; removing a file from the current tree does not revoke a token.

## Tests

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt pytest
python -m pytest -q
```

Tests mock Telegram and do not send real messages.
