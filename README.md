# byteNinja-Hacks-smart-helmet# 🪖 Smart Army Helmet - Live Monitoring System

A Flask-based dashboard integrated with **LoRa** and **PIR sensor** to monitor soldier activity and send emergency (SOS) alerts automatically when no motion is detected.

## 🚀 Features

- 🔄 Live web dashboard with auto-refresh
- 🛰️ Sends SOS alerts over LoRa when soldier is inactive
- 🌐 Sends SOS to a backend server via HTTP POST
- 🎯 Real-time status monitoring: motion, battery, health, mission mode
- 📍 GPS and Thermal Camera simulation (via iframe)
- 📡 Runs on Raspberry Pi with GPIO and SPI (LoRa)

---

## 🧰 Tech Stack

- Python 3
- Flask (for dashboard/web server)
- RPi.GPIO (for PIR motion detection)
- spidev (for LoRa SPI communication)
- requests (to send POST request to dashboard)
- HTML + CSS (embedded in Flask for frontend

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rajputaki/byteNinja-Hacks-smart-helmet.git
c

