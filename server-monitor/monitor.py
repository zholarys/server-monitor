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
TARGET_HOST = os.getenv("TARGET_HOST", "localhost")

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})

def check_target():
    try:
        r = requests.get(f"http://{TARGET_HOST}/api/health", timeout=5)
        return r.status_code == 200
    except:
        return False

def check_metrics():
    alerts = []
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    if cpu > CPU_THRESHOLD:
        alerts.append(f"🔴 <b>CPU Alert!</b> {TARGET_HOST}\nUsage: {cpu}% (threshold: {CPU_THRESHOLD}%)")
    if ram > RAM_THRESHOLD:
        alerts.append(f"🔴 <b>RAM Alert!</b> {TARGET_HOST}\nUsage: {ram}% (threshold: {RAM_THRESHOLD}%)")
    if disk > DISK_THRESHOLD:
        alerts.append(f"🔴 <b>Disk Alert!</b> {TARGET_HOST}\nUsage: {disk}% (threshold: {DISK_THRESHOLD}%)")
    if not check_target():
        alerts.append(f"🔴 <b>Service Down!</b>\n{TARGET_HOST}/api/health не отвечает!")

    return cpu, ram, disk, alerts

def main():
    send_alert(f"✅ <b>Monitor Started</b>\nМониторю сервер: {TARGET_HOST}")
    print(f"Monitor started. Target: {TARGET_HOST}")

    while True:
        cpu, ram, disk, alerts = check_metrics()
        print(f"CPU: {cpu}% | RAM: {ram}% | Disk: {disk}% | Service: {'OK' if check_target() else 'DOWN'}")
        for alert in alerts:
            send_alert(alert)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
