import imaplib
import email
import json
import mysql.connector
import time
import os

# ============================
# E-Mail Zugang (IServ-Schul-Mail)
# ============================
IMAP_SERVER = "imap.fds-limburg.schule"
IMAP_PORT = 993
EMAIL_ACCOUNT = "wetter.station.2026"
EMAIL_PASSWORD = "54tzck232026"

# ============================
# MySQL Datenbank
# ============================
DB_HOST = "10.118.49.89"
DB_USER = "wetterstation2026_db"
DB_PASSWORD = "54tzck232026"
DB_NAME = "wetterstation2026_db"

# ============================
# Log-Ordner erstellen
# ============================
LOG_FOLDER = "logs"
if not os.path.exists(LOG_FOLDER):
    os.mkdir(LOG_FOLDER)

# ============================
# DB Verbindung herstellen
# ============================
def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        autocommit=False
    )

conn = connect_db()
cursor = conn.cursor()
print("▶ Starte Mail → DB Service")

# ============================
# Logdatei schreiben
# ============================
def write_log(data):
    log_file = os.path.join(LOG_FOLDER, f"log_mid_{data['mid']}.txt")
    with open(log_file, "a") as f:
        f.write(json.dumps(data) + "\n")

# ============================
# Endlosschleife
# ============================
while True:
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')

        if status == "OK" and messages[0] != b'':
            for num in messages[0].split():
                status, data = mail.fetch(num, "(RFC822)")
                if status != "OK":
                    continue

                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                # JSON aus Mail extrahieren
                json_text = None
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() in ["application/json", "text/plain"]:
                            payload = part.get_payload(decode=True)
                            if payload:
                                json_text = payload.decode(errors="ignore").strip()
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        json_text = payload.decode(errors="ignore").strip()

                if not json_text or not json_text.startswith(("{","[")):
                    print("⚠ Ungültiges JSON, übersprungen")
                    continue

                try:
                    data_array = json.loads(json_text)
                    if isinstance(data_array, dict):
                        data_array = [data_array]

                    if not conn.is_connected():
                        print("🔄 DB reconnect...")
                        conn = connect_db()
                        cursor = conn.cursor()

                    for data in data_array:
                        ts = data.get("timestamp", "")
                        if "." in ts:
                            try:
                                parts = ts.split(" ")
                                d, m, y = parts[0].split(".")
                                ts = f"{y}-{m}-{d} {parts[1]}"
                            except:
                                ts = ts

                        sql = """
                        INSERT INTO messungen
                        (mid, temperatur, feuchte, druck, qualitaet, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (
                            data["mid"],
                            data["temperatur"],
                            data["feuchte"],
                            data["druck"],
                            data["qualitaet"],
                            ts
                        ))

                        # Logdatei pro MID
                        write_log(data)

                    conn.commit()
                    print(f"💾 {len(data_array)} Datensätze gespeichert")

                    # Mail löschen
                    mail.store(num, '+FLAGS', '\\Deleted')

                except Exception as e:
                    print("❌ Fehler beim JSON/DB Verarbeiten:", e)

            mail.expunge()  # endgültig löschen

        else:
            print("⏱ Keine neuen Mails")

        mail.logout()

    except Exception as e:
        print("❌ Fehler beim Abrufen:", e)

    print("⏱ Warte 60 Sekunden...\n")
    time.sleep(60)