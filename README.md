# 🏥 Smart ICU Patient Monitoring System (IoT)

An IoT-based real-time patient monitoring system built using **ESP32**, **Wokwi simulation**, and **TagoIO cloud**, designed to assist in continuous monitoring of ICU patients and provide **risk-based alerts**.

---

## 📌 Overview

This project simulates an ICU monitoring system that continuously tracks vital parameters and classifies patient condition into:

🟢 **NORMAL**  
🟡 **WARNING**  
🔴 **CRITICAL**  
🚨 **EMERGENCY**

---

## 🎯 Features

- 📊 Real-time monitoring of:
  - Heart Rate  
  - SpO₂  
  - Temperature  
  - Respiratory Rate  

- ⚠️ Dynamic Risk Score Calculation  
- 🧠 Intelligent State Classification  
- ☁️ Cloud integration using **TagoIO**  
- 🔔 Alert system:
  - LEDs (Green / Yellow / Red)
  - Buzzer (Critical / Emergency)
- 🕒 Data updates every **5 seconds**

---

## 🧠 Risk Scoring Model

| Parameter | Condition | Score |
|----------|----------|-------|
| SpO₂ | < 85% | +40 |
| Heart Rate | >130 or <45 bpm | +25 |
| Temperature | >39°C | +20 |
| Respiratory Rate | >25 | +15 |
| Motion (PIR) | Detected | +25 |

---

## 🚦 Patient State Classification

| Risk Score | State |
|-----------|------|
| 0–25 | NORMAL |
| 26–50 | WARNING |
| 51–80 | CRITICAL |
| >80 | EMERGENCY |

---

## 🛠️ Tech Stack

### 🔧 Hardware (Simulated)
- ESP32  
- DHT22 Temperature Sensor  
- PIR Motion Sensor  
- Potentiometers (for HR, SpO₂, RR simulation)  
- LEDs & Buzzer  

### 💻 Software
- MicroPython  
- Wokwi Simulator  
- TagoIO Cloud Platform  

---

## 🧩 System Architecture

- **Input Layer:** Sensors (DHT22, PIR, ADC inputs)  
- **Processing Layer:** ESP32 (MicroPython logic)  
- **Communication Layer:** WiFi (HTTP API)  
- **Cloud Layer:** TagoIO  
- **Output Layer:** LEDs + Buzzer  

---

## 🔗 Project Links

### ▶️ Wokwi Simulation
👉 https://wokwi.com/projects/460291139147332609  

### ☁️ TagoIO Dashboard
👉 https://admin.eu-w1.tago.io/dashboards/info/69cd3216f2ba72000bb749b4  

> ⚠️ *Note: Dashboard access permission may be required.*

---

## ▶️ How It Works

1. Sensors (or potentiometers) generate physiological data  
2. ESP32 reads and processes the data  
3. Risk score is calculated based on predefined thresholds  
4. Patient state is determined  
5. Data is:
   - Sent to **TagoIO (cloud dashboard)**  
   - Used to trigger **LEDs and buzzer**  
6. The system repeats every **5 seconds**

---

## 🧪 Simulation Details

- Potentiometers simulate:
  - Heart Rate  
  - SpO₂  
  - Respiratory Rate  

- PIR Sensor:
  - Detects motion  
  - Uses latch logic to avoid missed events  

- DHT22:
  - Provides temperature readings  

---

## 📷 Output

- 📟 Serial Monitor:
  - Displays real-time values  

- ☁️ TagoIO Dashboard:
  - Visualizes vitals  
  - Displays risk score  
  - Shows patient state  

- 💡 Hardware Output:
  - LEDs indicate condition  
  - Buzzer alerts for critical/emergency states  

---

## ⚠️ Limitations

- Simulation-based (not real medical sensors)  
- Not clinically accurate  
- Requires internet connectivity  
- Basic security (no encryption/authentication layers)  

---

## 🚀 Future Scope

- Integration with real medical sensors (MAX30102, ECG)  
- AI-based predictive analytics  
- Multi-patient monitoring  
- Mobile app alerts (SMS / Email)  
- Enhanced data security  

---

## 👨‍💻 Author

**Krishna Singh**  
22DCS011  
CSE (Dual Degree)  
National Institute of Technology, Hamirpur  

---

## 📄 License

This project is intended for **academic and educational purposes only**.
