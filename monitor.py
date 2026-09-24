import logging
import os
import time

import psutil
import requests

logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "900"))
DISK_PATH = os.getenv("DISK_PATH", "/")
THRESHOLDS = {
    "CPU": int(os.getenv("CPU_THRESHOLD", "80")),
    "RAM": int(os.getenv("RAM_THRESHOLD", "85")),
    "DISK": int(os.getenv("DISK_THRESHOLD", "90")),
}


def send_alert(message):
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message},
            timeout=(3, 10),
        )
        response.raise_for_status()
        if response.json().get("ok") is not True:
            logger.error("Telegram rejected the notification")
            return False
    except (requests.RequestException, ValueError) as error:
        # Exception text can contain the bot token embedded in the URL.
        logger.error("Telegram delivery failed (%s)", type(error).__name__)
        return False
    logger.info("Notification delivered")
    return True


def check_metrics():
    return {
        "CPU": psutil.cpu_percent(interval=1),
        "RAM": psutil.virtual_memory().percent,
        "DISK": psutil.disk_usage(DISK_PATH).percent,
    }


def notify_changes(metrics, states, now):
    for name, value in metrics.items():
        threshold = THRESHOLDS[name]
        state = states.setdefault(name, {"active": False, "last_sent": None})
        if value > threshold:
            if state["last_sent"] is None or now - state["last_sent"] >= ALERT_COOLDOWN:
                if send_alert(f"{name} high: {value:.1f}% (threshold {threshold}%)"):
                    state.update(active=True, last_sent=now)
        elif state["active"]:
            if send_alert(f"{name} recovered: {value:.1f}%"):
                state.update(active=False, last_sent=None)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not BOT_TOKEN or not CHAT_ID:
        raise SystemExit("Set BOT_TOKEN and CHAT_ID before starting")
    if CHECK_INTERVAL <= 0 or ALERT_COOLDOWN < 0:
        raise SystemExit("CHECK_INTERVAL must be positive and ALERT_COOLDOWN nonnegative")
    if not all(0 <= threshold <= 100 for threshold in THRESHOLDS.values()):
        raise SystemExit("Thresholds must be percentages between 0 and 100")
    psutil.PROCFS_PATH = os.getenv("PROCFS_PATH", "/proc")
    if not os.path.isdir(psutil.PROCFS_PATH) or not os.path.isdir(DISK_PATH):
        raise SystemExit("Configured host metric paths are missing")
    logger.info("Monitoring procfs=%s disk=%s", psutil.PROCFS_PATH, DISK_PATH)
    states = {}
    while True:
        try:
            metrics = check_metrics()
            logger.info("CPU=%.1f%% RAM=%.1f%% DISK=%.1f%%", metrics["CPU"], metrics["RAM"], metrics["DISK"])
            notify_changes(metrics, states, time.monotonic())
        except (OSError, psutil.Error) as error:
            logger.error("Metric collection failed (%s)", type(error).__name__)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
