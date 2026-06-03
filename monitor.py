import psutil
import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
CPU_THRESHOLD = int(os.getenv("CPU_THRESHOLD", "80"))
RAM_THRESHOLD = int(os.getenv("RAM_THRESHOLD", "85"))
DISK_THRESHOLD = int(os.getenv("DISK_THRESHOLD", "90"))

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})

def check_metrics():
    alerts = []

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    if cpu > CPU_THRESHOLD:
        alerts.append(f"🔴 <b>CPU Alert!</b> Usage: {cpu}% (threshold: {CPU_THRESHOLD}%)")

    if ram > RAM_THRESHOLD:
        alerts.append(f"🔴 <b>RAM Alert!</b> Usage: {ram}% (threshold: {RAM_THRESHOLD}%)")

    if disk > DISK_THRESHOLD:
        alerts.append(f"🔴 <b>Disk Alert!</b> Usage: {disk}% (threshold: {DISK_THRESHOLD}%)")

    return cpu, ram, disk, alerts

def main():
    send_alert("✅ <b>Server Monitor Started</b>\nMonitoring AWS server...")
    print("Monitor started")

    while True:
        cpu, ram, disk, alerts = check_metrics()
        print(f"CPU: {cpu}% | RAM: {ram}% | Disk: {disk}%")

        for alert in alerts:
            send_alert(alert)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
