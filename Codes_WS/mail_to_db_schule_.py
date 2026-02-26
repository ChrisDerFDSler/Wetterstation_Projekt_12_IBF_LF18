import imaplib
import email
import json
import mysql.connector
import time

# ============================
# E-Mail Zugang (IServ-Schul-Mail)
# ============================
IMAP_SERVER = ""
IMAP_PORT = 993
EMAIL_ACCOUNT = ""
EMAIL_PASSWORD = ""

# ============================
# MySQL Datenbank
# ============================
DB_HOST = ""
DB_USER = ""
DB_PASSWORD = ""
DB_NAME = ""

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

                # ----------------------------
                # JSON aus Mail extrahieren
                # ----------------------------
                json_text = None
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type in ["application/json", "text/plain"]:
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

                # ----------------------------
                # JSON verarbeiten
                # ----------------------------
                try:
                    data_array = json.loads(json_text)
                    if isinstance(data_array, dict):
                        data_array = [data_array]

                    # DB reconnect falls nötig
                    if not conn.is_connected():
                        print("🔄 DB reconnect...")
                        conn = connect_db()
                        cursor = conn.cursor()

                    for data in data_array:
                        ts = data.get("timestamp", "")
                        if "." in ts:  # z.B. DD.MM.YYYY
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

                    conn.commit()
                    print(f"💾 {len(data_array)} Datensätze gespeichert")
                    mail.store(num, '+FLAGS', '\\Seen')

                except Exception as e:
                    print("❌ Fehler beim JSON/DB Verarbeiten:", e)

        else:
            print("⏱ Keine neuen Mails")

        mail.logout()

    except Exception as e:
        print("❌ Fehler beim Abrufen:", e)

    print("⏱ Warte 60 Sekunden...\n")
    time.sleep(60)