import time
from machine import Pin, ADC
import dht
import network
import urequests
import ujson

# ==============================
# WIFI
# ==============================
ssid = "Wokwi-GUEST"
password = ""

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)

    while not wifi.isconnected():
        print("Connecting...")
        time.sleep(1)

    print("Connected:", wifi.ifconfig())

# ==============================
# TAGO CONFIG
# ==============================
DEVICE_TOKEN = "YOUR_DEVICE_TOKEN"
TAGO_URL = "https://api.eu-w1.tago.io/data"

headers = {
    "Content-Type": "application/json",
    "Device-Token": DEVICE_TOKEN
}

def send_to_tago(patient):
    payload = [
        {"variable": "heart_rate", "value": patient.heart_rate},
        {"variable": "spo2", "value": patient.spo2},
        {"variable": "temperature", "value": patient.temperature},
        {"variable": "respiratory_rate", "value": patient.respiratory_rate},
        {"variable": "motion", "value": int(patient.motion_detected)},  # Added
        {"variable": "risk", "value": patient.risk_score},
        {"variable": "state", "value": patient.state}
    ]

    try:
        response = urequests.post(TAGO_URL, headers=headers, data=ujson.dumps(payload))
        response.close()
        print("Sent to Tago")
    except:
        print("Tago error")

# ==============================
# HARDWARE
# ==============================
green_led = Pin(18, Pin.OUT)
yellow_led = Pin(19, Pin.OUT)
red_led = Pin(23, Pin.OUT)
buzzer = Pin(25, Pin.OUT)

dht_sensor = dht.DHT22(Pin(4))
pir = Pin(5, Pin.IN)
button = Pin(15, Pin.IN, Pin.PULL_DOWN)

# Potentiometers
pot_hr = ADC(Pin(34))
pot_hr.atten(ADC.ATTN_11DB)

pot_spo2 = ADC(Pin(35))
pot_spo2.atten(ADC.ATTN_11DB)

pot_rr = ADC(Pin(32))
pot_rr.atten(ADC.ATTN_11DB)

# ==============================
# SENSOR FUNCTIONS
# ==============================
def read_temperature():
    try:
        dht_sensor.measure()
        return dht_sensor.temperature()
    except:
        return 36.8

def read_heart_rate():
    return int(40 + (pot_hr.read() / 4095) * 100)

def read_spo2():
    return int(75 + (pot_spo2.read() / 4095) * 25)

def read_rr():
    return int(10 + (pot_rr.read() / 4095) * 20)

# ==============================
# PATIENT CLASS
# ==============================
class Patient:

    def __init__(self):
        self.heart_rate = 80
        self.spo2 = 98
        self.respiratory_rate = 16
        self.temperature = 36.8

        self.motion_detected = False
        self.motion_timer = 0
        self.startup_ignore = 2   # Ignore initial PIR noise

        self.risk_score = 0
        self.state = "NORMAL"

    def update(self):
        self.heart_rate = read_heart_rate()
        self.spo2 = read_spo2()
        self.respiratory_rate = read_rr()
        self.temperature = read_temperature()

        # ======================
        # PIR HANDLING (FINAL FIX)
        # ======================
        if self.startup_ignore > 0:
            self.startup_ignore -= 1
            self.motion_detected = False
        else:
            if pir.value() == 1:
                self.motion_timer = 2  # latch motion

            if self.motion_timer > 0:
                self.motion_detected = True
                self.motion_timer -= 1
            else:
                self.motion_detected = False

        self.calculate_risk()
        self.evaluate_state()

    def calculate_risk(self):
        score = 0

        if self.spo2 < 85:
            score += 40

        if self.heart_rate > 130 or self.heart_rate < 45:
            score += 25

        if self.temperature > 39:
            score += 20

        if self.respiratory_rate > 25:
            score += 15

        if self.motion_detected:
            score += 25

        self.risk_score = score

    def evaluate_state(self):
        if self.risk_score > 80:
            self.state = "EMERGENCY"
        elif self.risk_score > 50:
            self.state = "CRITICAL"
        elif self.risk_score > 25:
            self.state = "WARNING"
        else:
            self.state = "NORMAL"

# ==============================
# HARDWARE OUTPUT
# ==============================
def update_hardware(state):

    green_led.off()
    yellow_led.off()
    red_led.off()
    buzzer.off()

    if state == "NORMAL":
        green_led.on()

    elif state == "WARNING":
        yellow_led.on()

    elif state == "CRITICAL":
        red_led.on()
        for _ in range(2):
            buzzer.on()
            time.sleep(0.2)
            buzzer.off()
            time.sleep(0.2)

    elif state == "EMERGENCY":
        red_led.on()
        buzzer.on()

# ==============================
# MAIN
# ==============================
connect_wifi()

print("Stabilizing PIR sensor...")
time.sleep(3)  # Prevent startup false trigger

patient = Patient()

while True:
    patient.update()

    print("HR:", patient.heart_rate,
          "SpO2:", patient.spo2,
          "Temp:", patient.temperature,
          "RR:", patient.respiratory_rate,
          "Motion:", int(patient.motion_detected),
          "Risk:", patient.risk_score,
          "State:", patient.state)

    update_hardware(patient.state)
    send_to_tago(patient)

    time.sleep(5)
