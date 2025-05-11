from flask import Flask, render_template_string
import threading
import RPi.GPIO as GPIO
import time
import spidev
import requests  # Importing requests to send HTTP requests

# === Setup LoRa ===
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000000

def writeRegister(address, value):
    spi.xfer2([address | 0x80, value])

def sendPacket(payload):
    print("Sending SOS packet...")
    writeRegister(0x01, 0x01)
    writeRegister(0x0D, 0x00)
    for b in payload:
        writeRegister(0x00, b)
    writeRegister(0x22, len(payload))
    writeRegister(0x01, 0x83)
    time.sleep(1)
    print(" SOS packet sent over LoRa!")


# === Setup PIR ===
PIR_PIN = 17
NO_MOTION_THRESHOLD = 10 # seconds
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

last_motion_time = time.time()
sos_triggered = False

# === Setup Flask ===
app = Flask(__name__)
html_page = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Smart Army Helmet - Live Dashboard</title>
    <meta http-equiv="refresh" content="5" />
    <!-- Auto-refresh every 30 seconds -->
    <style>
      body {
        margin: 0;
        padding: 0;
        font-family: "Poppins", sans-serif;
        /* background-image: url("https://think360studio-media.s3.ap-south-1.amazonaws.com/download/india-flag-2021-wallpaper-1.png");
            filter: blur(10px);
            -webkit-filter: blur(10px); */
        color: #00ff00; 
      }
      .headerimg {
        text-align: center;
        padding: 20px;
        background: #1f1f1f;
        background-position: center;
        background-repeat: no-repeat;
        background-size: cover;
   background-image: url("https://think360studio-media.s3.ap-south-1.amazonaws.com/download/india-flag-2021-wallpaper-1.png");
        font-size: 2em;
        font-weight: bold;
        letter-spacing: 1px;
        /* filter: blur(10px); */
        -webkit-filter: blur(5px);
        color: black;
        height: 90px;
      }
      .headertext {
        /* background-color: rgb(0,0,0);
  background-color: rgba(0,0,0, 0.4);  */
        color: black;
        font-size: 40px;
        font-weight: bold;
        /* border: 3px solid #f1f1f1; */
        position: absolute;
        /* top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2; */
        top: 0;
        margin-top: 20px;
        margin-left: 80px;
        width: 80%;
        padding: 20px;
        text-align: center;
      }
      .container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        margin: 2px 20px;
        /* color: white; */
      }
      .card {
        /* background:rgb(151, 147, 147); */
        background: linear-gradient(to bottom, white, #e0ffff);
        margin: 15px;
        padding: 20px;
        border-radius: 15px;
        width: 300px;
        height: 220px;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.4);
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: 0.3s;
      }
      .card:hover {
        box-shadow: 0 0 25px rgba(8, 81, 108, 0.8);
      }
      .title {
        font-size: 1.5em;
        margin-bottom: 15px;
        color: black;
      }
      .value {
        font-size: 1.5em;
        font-weight: bold;
        margin-top: 10px;
        /* color: rgb(215, 162, 39); */
        color: rgb(34, 177, 34);
      }
      .sos {
        color: #ff4c4c;
        animation: blink 1s infinite;
      }
      @keyframes blink {
        50% {
          opacity: 0.5;
        }
      }
      iframe {
        border: none;
        border-radius: 15px;
        width: 100%;
        height: 130px;
      }
    </style>
  </head>
  <body>
    <header>
      <div class="headerimg"></div>
      <div class="headertext">
        Smart Army Helmet - Live Monitoring Dashboard
      </div>
    </header>

    <div class="container">
      <div class="card">
        <div class="title">Soldier ID</div>
        <div class="value">#IND-0457</div>
      </div>

      <div class="card">
        <div class="title"> Helmet Status</div>
        <div class="value">Connected</div>
      </div>

      <div class="card">
        <div class="title">Battery Status</div>
        <div class="value">85%</div>
      </div>

      <div class="card">
        <div class="title">Health Monitoring</div>
        <div class="value">Heart: 76 bpm<br />BP: 120/80</div>
      </div>

      <div class="card">
        <div class="title">Movement Status</div>
        <div class="value">Active ?</div>
      </div>
      <div class="card">
        <div class="title">SOS Alert</div>
        <div class="value">Safe ?</div>
         {% if sos %} 
         <div class="value sos">Soldier_need_help  ??</div> 
         {% endif %} 
      </div>

      <div class="card">
        <div class="title">Mission Mode</div>
        <div class="value">Patrolling</div>
      </div>

      <div class="card">
        <div class="title">GPS Location</div>
        <iframe
          src="https://maps.google.com/maps?q=India&t=&z=4&ie=UTF8&iwloc=&output=embed"
        ></iframe>
      </div>

      <div class="card">
        <div class="title">Thermal Camera</div>
        <iframe
          src="https://media.giphy.com/media/10FwycrnAkpshW/giphy.gif"
          title="Thermal Feed"
        ></iframe>
      </div>
    </div>
  </body>
</html>


"""

@app.route('/')
def home():
    global sos_triggered
    return render_template_string(html_page, sos=sos_triggered,)

# === Send SOS to Dashboard Endpoint ===
DASHBOARD_ENDPOINT = "http://192.168.19.246:5000/api/sos"  # Replace with your real endpoint

def sendSOSToDashboard():
    payload = {"alert": "SOS - Soldier needs Help!"}  # You can customize this payload
    try:
        response = requests.post(DASHBOARD_ENDPOINT, json=payload)  # Sending a POST request with JSON payload
        if response.status_code == 200:
            print("SOS sent to dashboard successfully!")
        else:
            print(f"Failed to send SOS to dashboard: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"? Error sending SOS: {e}")
# === Background Thread for PIR Monitoring ===
def monitor_motion():
    global last_motion_time, sos_triggered
    print("Starting Smart Army Helmet Monitoring with Dashboard...")
    time.sleep(30)  # PIR warm-up
    print("System Ready!")

    while True:
        if GPIO.input(PIR_PIN):
            print("Motion Detected ?")
            last_motion_time = time.time()
            sos_triggered = False
        else:
            print("No Motion Detected...")

        if time.time() - last_motion_time > NO_MOTION_THRESHOLD:
            if not sos_triggered:
                print(f"? No motion detected for {NO_MOTION_THRESHOLD} seconds!")
                message = "SOS - Soldier needs Help!"
                payload = [ord(c) for c in message]
                sendPacket(payload)  # Send SOS over LoRa
                sos_triggered = True

                # Send SOS to dashboard
                sendSOSToDashboard()  # New function to send SOS to the endpoint

        time.sleep(1)

if __name__ == '__main__':
    t = threading.Thread(target=monitor_motion)
    t.start()
    app.run(host='0.0.0.0', port=5000)
