# EdgeShield: A Hybrid Hardware-Software System for PPE Compliance Detection

![EdgeShield Logo](images/edgeshield_logo.png)

**Author:** Seshadrinathan K  
**Institution:** SRM Institute of Science and Technology  
**Email:** sk5416@srmist.edu.in  

---

## 📌 Overview

**EdgeShield** is an open-source, hybrid PPE compliance detection system built using computer vision (YOLOv8) and real-time hardware alerts (Arduino). It addresses safety violations on construction sites by detecting missing hardhats or reflective vests from video feeds and issuing immediate alerts via LEDs, buzzers, and LCD messages.

---

## 🔧 System Architecture

EdgeShield consists of three main components:

1. **YOLOv8-based PPE Detection**  
2. **Streamlit Web Interface for Live Monitoring**  
3. **Arduino-Based Hardware Alert System**

---

## 🧠 Software Stack

- **Computer Vision:** YOLOv8 (Ultralytics)
- **Interface:** Streamlit
- **Image Processing:** OpenCV
- **Communication:** smtplib for email alerts

### ⚙️ Software Workflow

1. Capture and analyze video frames with YOLOv8.
2. Stream detection output via Streamlit UI.
3. Trigger email alert when violation is detected.

---

### 🖼️ Software Flow Diagram

![Software Flow Diagram](images/software_flow.png)

---

## 💡 Hardware Stack

- **Microcontroller:** Arduino Uno R3 (or ESP32 for future versions)
- **Alert Mechanisms:**  
  - Red LED (Violation)  
  - Yellow LED (Alert)  
  - Piezo Buzzer  
  - LCD 16x2 Display
- **Simulation:** Tinkercad

> ⚠️ In production, replace email-based signaling with MQTT or ESP-NOW for real-time wireless alerts.

---

### 🖼️ Arduino Circuit Diagram

![Arduino Simulation](images/stark_solutions_iot.png)

---

## 🚀 How to Run

### 🔨 Prerequisites

- Python 3.8+
- Arduino IDE or Tinkercad
- Required Python packages:
  ```bash
  pip install ultralytics opencv-python streamlit
