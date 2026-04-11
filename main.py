import time
from machine import Pin, ADC
import dht
import network
import urequests
import ujson

# ==============================
# WIFI
# ==============================
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if not wifi.isconnected():
        print("Connecting to WiFi...")
        wifi.connect("Wokwi-GUEST", "")

        while not wifi.isconnected():
            time.sleep(0.5)
            print(".", end="")

    print("\nConnected:", wifi.ifconfig())

# ==============================
# TAGO CONFIG
# ==============================
DEVICE_TOKEN = "42ca9790-dbbc-4d36-b1c5-ae84fb18dc69"
TAGO_URL = "https://api.eu-w1.tago.io/data"

headers = {
    "Content-Type": "application/json",
    "Device-Token": DEVICE_TOKEN
}
# ==============================
# SEND FUNCTION
# FIX 2: Removed "time" field from payload so Tago.io assigns
#         server-side timestamps. MicroPython time.time() starts
#         from epoch 2000 (not Unix 1970), which causes Tago to
#         reject or misplace data, showing "No data available".
# ==============================
def send_to_tago(patient):
    payload = [
        {"variable": "heart_rate",       "value": patient.heart_rate},
        {"variable": "spo2",             "value": patient.spo2},
        {"variable": "temperature",      "value": patient.temperature},
        {"variable": "respiratory_rate", "value": patient.respiratory_rate},
        {"variable": "motion",           "value": int(patient.motion_detected)},
        {"variable": "risk",             "value": patient.risk_score},
        {"variable": "state",            "value": patient.state}
    ]

    try:
        response = urequests.post(
            TAGO_URL,
            headers=headers,
            data=ujson.dumps(payload)
        )
        print("Tago Status:", response.status_code)
        print("Tago Response:", response.text)
        response.close()
    except Exception as e:
        print("Tago send error:", e)

# ==============================
# INITIALIZE VARIABLES IN TAGO
# FIX 3: Also removed "time" field here for same reason
# ==============================
def initialize_variables():
    print("Initializing variables in Tago...")

    dummy_payload = [
        {"variable": "heart_rate",       "value": 0},
        {"variable": "spo2",             "value": 0},
        {"variable": "temperature",      "value": 0},
        {"variable": "respiratory_rate", "value": 0},
        {"variable": "motion",           "value": 0},
        {"variable": "risk",             "value": 0},
        {"variable": "state",            "value": "INIT"}
    ]

    try:
        response = urequests.post(
            TAGO_URL,
            headers=headers,
            data=ujson.dumps(dummy_payload)
        )
        print("Init Status:", response.status_code)
        print("Init Response:", response.text)
        response.close()
    except Exception as e:
        print("Init error:", e)

# ==============================
# HARDWARE
# ==============================
green_led  = Pin(18, Pin.OUT)
yellow_led = Pin(19, Pin.OUT)
red_led    = Pin(23, Pin.OUT)
buzzer     = Pin(25, Pin.OUT)

dht_sensor = dht.DHT22(Pin(4))
pir        = Pin(5, Pin.IN)

# Potentiometers
pot_hr = ADC(Pin(34))
pot_hr.atten(ADC.ATTN_11DB)

pot_spo2 = ADC(Pin(35))
pot_spo2.atten(ADC.ATTN_11DB)

pot_rr = ADC(Pin(32))
pot_rr.atten(ADC.ATTN_11DB)

# ==============================
# SENSOR FUNCTIONS
# FIX 4: DHT22 returns Celsius. Tago dashboard was showing °F label
#         but receiving °C values. Kept as Celsius — make sure your
#         Tago widget unit label says °C, not °F.
# ==============================
def read_temperature():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()  # Returns °C
        print("Raw temp from DHT22:", temp)
        return temp
    except Exception as e:
        print("DHT22 read error:", e)
        return 36.8  # Fallback body temperature in °C

def read_heart_rate():
    return int(40 + (pot_hr.read() / 4095) * 100)

def read_spo2():
    return int(75 + (pot_spo2.read() / 4095) * 25)

def read_rr():
    return int(10 + (pot_rr.read() / 4095) * 20)

# ==============================
# LED + BUZZER CONTROL (BONUS FIX)
# These were defined but never used — now tied to patient state
# ==============================
def update_leds(state):
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
    elif state == "EMERGENCY":
        red_led.on()
        buzzer.on()

# ==============================
# PATIENT CLASS
# ==============================
class Patient:

    def __init__(self):
        self.motion_timer   = 0
        self.startup_ignore = 2
        # Safe default values
        self.heart_rate       = 0
        self.spo2             = 0
        self.temperature      = 0
        self.respiratory_rate = 0
        self.motion_detected  = False
        self.risk_score       = 0
        self.state            = "INIT"

    def update(self):
        self.heart_rate       = read_heart_rate()
        self.spo2             = read_spo2()
        self.respiratory_rate = read_rr()
        self.temperature      = read_temperature()

        # Ignore PIR during startup to prevent false triggers
        if self.startup_ignore > 0:
            self.startup_ignore -= 1
            self.motion_detected = False
        else:
            if pir.value() == 1:
                self.motion_timer = 2

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
# MAIN
# ==============================
connect_wifi()
initialize_variables()

print("Stabilizing PIR sensor...")
time.sleep(3)

patient = Patient()

while True:
    patient.update()

    # Update LEDs based on state
    update_leds(patient.state)

    print("---")
    print("HR:    ", patient.heart_rate,       "bpm")
    print("SpO2:  ", patient.spo2,             "%")
    print("Temp:  ", patient.temperature,      "°C")
    print("RR:    ", patient.respiratory_rate, "breaths/min")
    print("Motion:", int(patient.motion_detected))
    print("Risk:  ", patient.risk_score)
    print("State: ", patient.state)

    send_to_tago(patient)

    time.sleep(5)
