# 🌦️ Wetterstation_Projekt_12_IBF_LF18

**Schulprojekt der FDS Limburg – Klasse 12IBF**  
**Lernfeld 18 (LF18)**

Dieses Projekt beschreibt den Aufbau einer vernetzten Wetterstation mit Sensordatenerfassung, MQTT-Kommunikation, Datenbankanbindung, Webdarstellung und E-Mail-Versand.

---

## 📌 Projektübersicht

Die Wetterstation besteht aus zwei Hauptkomponenten:

- **Raspberry Pi / Pi 400**  
  Zentrale Server-, Speicher- und Auswertungseinheit
- **Raspberry Pi Pico W (RP2040)**  
  Sensoreinheit zur Datenerfassung und Übertragung

Die Kommunikation zwischen den Komponenten erfolgt über das **MQTT-Protokoll**.

---

## 🧰 Hardware (Testumgebung)

### Sensor
- **BME680**
  - Temperatur
  - Luftfeuchtigkeit
  - Luftdruck
  - Luftqualität (VOC)

### Geräte
- Raspberry Pi 400  
- Raspberry Pi  
- Raspberry Pi Pico W (RP2040 mit WLAN)

---

## 🖥️ Software & Dienste

### Raspberry Pi / Pi 400 (Server)

#### 🔸 MQTT Broker
- **Mosquitto**
  - Zentrale Nachrichtenvermittlung
  - Publisher: Pico W
  - Subscriber: Server-Clients

#### 🔸 LAMP-Server (XAMPP auf Linux)
- **Apache** – Webserver  
- **MariaDB** – Datenbank  
- **PHP** – Backend  
- **phpMyAdmin** – Datenbankverwaltung

#### 🔸 MQTT-Clients (Subscriber)
- 📧 MQTT-Client für **E-Mail-Versand**
- 🗄️ MQTT-Client für **Datenbankanbindung**
- 📊 MQTT-Client für **direkte digitale Darstellung**
- ✉️ **Mail-Empfang mit Datenbankanbindung**

---

### Raspberry Pi Pico W (RP2040)

- 📡 Auslesen des **BME680 Sensors**
- 📤 Senden der Messdaten an den MQTT-Broker (**Publisher**)
- 📧 Versand einer E-Mail mit aktuellen Messwerten (optional)

---

## ⚙️ Konfigurationsdatei

Alle wichtigen Einstellungen werden über eine zentrale Konfigurationsdatei vorgenommen.

### Enthaltene Konfigurationen:
- WLAN-Zugangsdaten
- IP-Adresse des MQTT-Brokers
- MQTT-Port & Topics
- E-Mail-Empfänger
- SMTP-Server-Daten
  - Serveradresse
  - Port
  - Benutzername
  - Passwort

➡️ Sensible Daten müssen **nicht im Code** geändert werden.

---

## 🎯 Projektziele

- Aufbau einer funktionierenden IoT-Wetterstation
- Einsatz von MQTT zur Datenübertragung
- Speicherung von Sensordaten in einer Datenbank
- Webbasierte Anzeige der Messwerte
- Automatischer E-Mail-Versand
- Praxisnahe Anwendung von Linux-Serverdiensten

---

## 📁 Projektstruktur (Beispiel)
