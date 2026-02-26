import time
import json
import network
from machine import Pin, I2C
from bme680 import BME680_I2C
from umail import SMTP

# ===============================
# Konfiguration
# ===============================
WIFI_SSID = " "
WIFI_PASSWORD = " "
SENSOR_MID = x  # eindeutige ID des Sensors
EMAIL_ENABLED = True
SMTP_SERVER = " "
SMTP_PORT = 465  # Gmail SSL-Port
SMTP_SENDER_EMAIL = " "
SMTP_APP_PASSWORD = " "
EMAIL_RECIPIENT = " "
EMAIL_SUBJECT = " "
CACHE_FILE = "cache.json"

# ===============================
# Hilfsfunktionen für den Cache
# ===============================
def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []

def save_cache(data_list):
    with open(CACHE_FILE, "w") as f:
        json.dump(data_list, f)

def clear_cache():
    save_cache([])

# ===============================
# WLAN verbinden
# ===============================
def is_connected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("📡 WLAN verbinden...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    if wlan.isconnected():
        print("✅ WLAN verbunden:", wlan.ifconfig())
        return True
    else:
        print("⚠ WLAN nicht verbunden, Offline-Modus")
        return False

# ===============================
# E-Mail senden (mit Cache)
# ===============================
def send_email(data):
    all_data = load_cache()
    all_data.append(data)

    if not is_connected():
        print("⚠ Kein Internet. Speichere im Cache (Gesamt: {})".format(len(all_data)))
        save_cache(all_data)
        return

    try:
        print("📧 Versuche {} Messungen zu senden...".format(len(all_data)))
        smtp = SMTP(
            SMTP_SERVER,
            SMTP_PORT,
            username=SMTP_SENDER_EMAIL,
            password=SMTP_APP_PASSWORD,
            ssl=True
        )

        payload = json.dumps(all_data)
        msg = (
            "Subject: {}\r\n"
            "To: {}\r\n"
            "From: {}\r\n"
            "Content-Type: application/json\r\n\r\n{}"
        ).format(EMAIL_SUBJECT, EMAIL_RECIPIENT, SMTP_SENDER_EMAIL, payload)

        smtp.to(EMAIL_RECIPIENT, mail_from=SMTP_SENDER_EMAIL)
        smtp.send(msg.encode("utf-8"))
        smtp.quit()
        print("✅ E-Mail gesendet: {} Messungen".format(len(all_data)))
        clear_cache()

    except Exception as e:
        print("❌ Fehler beim Senden:", e)
        save_cache(all_data)

# ===============================
# Sensor initialisieren
# ===============================
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
sensor = BME680_I2C(i2c)

# ===============================
# Start
# ===============================
internet = connect_wlan()
print("▶ Wetterstation gestartet")

# ===============================
# Hauptschleife
# ===============================
while True:
    if not is_connected():
        internet = connect_wlan()

    t = time.localtime()
    timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )

    data = {
        "mid": SENSOR_MID,
        "temperatur": float(sensor.temperature),
        "feuchte": float(sensor.humidity),
        "druck": float(sensor.pressure),
        "qualitaet": float(sensor.gas),
        "timestamp": timestamp
    }

    # E-Mail senden / Cache speichern
    if EMAIL_ENABLED:
        send_email(data)
    else:
        cache = load_cache()
        cache.append(data)
        save_cache(cache)
        print("⚠ Messung in Cache gespeichert (Email deaktiviert)")

    # Messintervall 5 Minuten

    time.sleep(10)  # 300 Sekunden = 5 Minuten

