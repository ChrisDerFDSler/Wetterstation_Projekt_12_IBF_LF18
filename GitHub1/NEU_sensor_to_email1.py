import time
import json
import network
import os
from machine import Pin, I2C
from bme680 import BME680_I2C
from umail import SMTP

# ===============================
# WLAN & Konfiguration
# ===============================
WIFI_SSID = "dd-wrt"
WIFI_PASSWORD = "54tzck23"
SENSOR_MID = 8 
EMAIL_ENABLED = True
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_SENDER_EMAIL = "cameraabsender998@gmail.com"
SMTP_APP_PASSWORD = "glco mzfh cgqj fyop"
EMAIL_RECIPIENT = "wetter.station.2026@fds-limburg.schule"
EMAIL_SUBJECT = "David Wetterstation BME680 JSON"
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
    return False

# ===============================
# E-Mail senden
# ===============================
def send_email_with_cache(new_data):
    # 1. Bestehende Daten laden und neue Messung anhängen
    all_data = load_cache()
    all_data.append(new_data)
    
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
        
        print("✅ Erfolg! Cache wird geleert.")
        clear_cache() # Erst hier werden die alten Daten gelöscht!

    except Exception as e:
        print("❌ Fehler beim Senden:", e)
        save_cache(all_data) # Bei Fehler alles zurück in die Datei

# ===============================
# Sensor initialisieren
# ===============================
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
sensor = BME680_I2C(i2c)

# ===============================
# Hauptschleife
# ===============================
print("▶ Wetterstation gestartet")
connect_wlan()

while True:
    # WLAN-Check (versucht reconnect falls abgebrochen)
    if not is_connected():
        connect_wlan()

    # Zeitstempel
    t = time.localtime()
    timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )

    # Messung
    data = {
        "mid": SENSOR_MID,
        "temperatur": float(sensor.temperature),
        "feuchte": float(sensor.humidity),
        "druck": float(sensor.pressure),
        "qualitaet": float(sensor.gas),
        "timestamp": timestamp
    }

    if EMAIL_ENABLED:
        send_email_with_cache(data)
    
    #time.sleep(300)
    time.sleep(60)