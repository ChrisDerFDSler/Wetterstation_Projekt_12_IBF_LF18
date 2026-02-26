![Status](https://img.shields.io/badge/Status-In%20Bearbeitung-yellow)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![IoT](https://img.shields.io/badge/IoT-MQTT-orange)
![Raspberry Pi Pico W](https://img.shields.io/badge/Hardware-Raspberry%20Pi%20Pico%20W-red)
![Raspberry Pi](https://img.shields.io/badge/Hardware-Raspberry%20Pi-red)
![BME680](https://img.shields.io/badge/Hardware-BME680%20Umweltsensor-red)










## 🌦️ **Wetterstation_Projekt_12_IBF_LF18**
### Schulprojekt der FDS Limburg – Klasse 12IBF
Lernfeld 18 (LF18)

Dieses Projekt beschreibt den Aufbau einer vernetzten Wetterstation mit Sensordatenerfassung, E-Mail-Versand, Datenbankanbindung und Log-Files für jede Sensoreinheit.

## 📌 **Projektübersicht**
### Die Wetterstation besteht aus zwei Hauptkomponenten:
- Raspberry Pi / Pi 400
- Zentrale Server-, Speicher- und Auswertungseinheit
- Raspberry Pi Pico W (RP2040)
- Sensoreinheit zur Datenerfassung und Übertragung

Die Kommunikation erfolgt aktuell über E-Mail / DB-Uploads und nicht mehr nur über MQTT, um den Unterrichtszweck einfacher nachvollziehbar zu machen.

## 🧰 **Hardware (Testumgebung)**
### Sensor:
- BME680
  - Temperatur
  - Luftfeuchtigkeit
  - Luftdruck
  - Luftqualität (VOC)
### Geräte:
- Raspberry Pi Pico W (RP2040 mit WLAN)

## 🖥️ **Software & Dienste**
- Raspberry Pi Pico W (RP2040)
- Datenbankanbindung
  -  MariaDB/MySQL
- Speicherung aller Messwerte mit Zeitstempel und Sensor-ID
  - MID
- E-Mail-Empfang & Verarbeitung
- Abrufen von Sensormails
  - Einfügen in die Datenbank
  - Schreiben in individuelle Log-Dateien pro MID
  - Gelöschte E-Mails nach Verarbeitung
- Log-Files
  - Jede Sensoreinheit (MID) hat eine eigene Log-Datei: logs/log_mid_<MID>.txt
- Alle historischen Messwerte nachvollziehbar, auch wenn Sensor offline gelöscht wird
- Auslesen des BME680 Sensors
- Versand der Messwerte per E-Mail an den Server
- Offline-Cache bei fehlender Internetverbindung
- Automatischer Wieder-Versuch beim nächsten Online-Zyklus
- Messintervall Default:
  - alle 5 Minuten
- Jede Sensoreinheit hat eine feste MID zur Identifikation

## ⚙️ **Konfiguration**
### Alle wichtigen Einstellungen befinden sich in den Codes selbst.
- Sensor-to-Mail Konfiguration (Pico W)
- WLAN-Zugang
- Sensor-ID (SENSOR_MID)
- E-Mail-Versand aktiviert/deaktiviert
- SMTP-Server, Port, E-Mail-Adresse und App-Passwort
- Cache-Datei für offline gesicherte Messwerte
- Mail-to-DB Konfiguration (Server)
- IMAP-Server & Zugangsdaten
- MySQL-Datenbank-Zugang
- Log-Ordner für pro-MID Dateien
- Automatisches Löschen der Mails nach Verarbeitung

## 🎯 **Projektzielle**
- Vernetzte IoT-Wetterstation mit zuverlässiger Datenerfassung
- Sicherer Datenversand per E-Mail mit Offline-Cache
- Speicherung und Auswertung in einer zentralen Datenbank
- Historische Daten nachvollziehbar über Log-Dateien
- Praxisnahe Anwendung von Serverdiensten, Python-Skripten und Sensorik

## 📊 **Beispiel-Datensatz**
{
  "mid": 7,
  "temperatur": 21.5,
  "feuchte": 45.3,
  "druck": 1012.4,
  "qualitaet": 300,
  "timestamp": "2026-02-26 14:15:00"
}
