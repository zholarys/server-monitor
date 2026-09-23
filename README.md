# Server Monitor

Lightweight server monitoring script with Telegram alerts, containerized with Docker.

## What it does

- Polls server metrics on an interval
- Sends alerts to a Telegram chat when thresholds are crossed
- Runs as a Docker container for easy deployment on any host

## Stack

- Python
- Docker / Docker Compose
- Telegram Bot API

## Usage

1. Set your Telegram bot token and chat ID (see `monitor.py` / environment variables)
2. Build and run:
```bash
   docker compose up -d
```
3. Check container logs to confirm alerts are being sent:
```bash
   docker compose logs -f
```
