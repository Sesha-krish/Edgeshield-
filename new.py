import streamlit as st
import cv2
from ultralytics import YOLO
import numpy as np
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
import os
from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
email_password = os.getenv("EMAIL_PASSWORD")

def draw_text_with_background(frame, text, position, font_scale=0.4, color=(255, 255, 255), thickness=1, bg_color=(0, 0, 0), alpha=0.7, padding=5):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_width, text_height = text_size

    overlay = frame.copy()
    x, y = position
    cv2.rectangle(overlay, (x - padding, y - text_height - padding), (x + text_width + padding, y + padding), bg_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)

def send_email_alert(image_path):
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Alert: Hardhat Missing!"

    body = "A hardhat was not detected for the past 10 seconds, but a person was detected. Please find the attached frame showing the situation."
    message.attach(MIMEText(body, "plain"))
    
   
    with open(image_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={image_path}")
        message.attach(part)
    
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email alert sent with attachment.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_email_in_background(image_path):
    email_thread = threading.Thread(target=send_email_alert, args=(image_path,))
    email_thread.start()

def expand_box(box, margin=50):
    x1, y1, x2, y2 = box
    return max(0, x1 - margin), max(0, y1 - margin), x2 + margin, y2 + margin

def is_in_danger(box1, box2):
    x1a, y1a, x2a, y2a = box1
    x1b, y1b, x2b, y2b = box2
    return not (x2a < x1b or x1a > x2b or y2a < y1b or y1a > y2b)

def ppe_detection():
    model = YOLO("ppe.pt")  
    cap = cv2.VideoCapture(0) 
    
    if not cap.isOpened():
        st.error("Error: Unable to access the webcam.")
        return

    st.info("Press 'q' to exit.")

    colors = [
        (255, 0, 0),  
        (0, 255, 0),  
        (0, 0, 255), 
        (255, 255, 0), 
        (255, 0, 255),  
        (0, 255, 255),  
        (128, 0, 128),  
        (128, 128, 0),  
        (0, 128, 128),  
        (128, 128, 128)  
    ]

   
    last_hardhat_time = time.time()
    hardhat_missing = False
    last_email_time = time.time()  
    email_sent_flag = False
    email_sent_time = 0  
    video_placeholder = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Error: Unable to read from the webcam.")
            break

       
        hardhat_count = 0
        vest_count = 0
        person_count = 0
        hardhat_detected = False
        person_detected = False

       
        results = model(frame)

        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  
                    confidence = box.conf[0] 
                    cls = int(box.cls[0])  
                    label = f"{model.names[cls]} ({confidence:.2f})"

                    color = colors[cls % len(colors)]

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    draw_text_with_background(frame, label, (x1, y1 - 10), font_scale=0.4, color=(255, 255, 255), bg_color=color, alpha=0.8, padding=4)

                    if model.names[cls] == "Hardhat":
                        hardhat_count += 1
                        hardhat_detected = True
                    elif model.names[cls] == "Safety Vest":
                        vest_count += 1
                    elif model.names[cls] == "Person":
                        person_count += 1
                        person_detected = True

        if person_detected and not hardhat_detected and (time.time() - last_email_time) >= 100:  
            image_path = "no_hardhat_frame.jpg"
            cv2.imwrite(image_path, frame) 
            send_email_in_background(image_path)  
            email_sent_flag = True
            email_sent_time = time.time() 
            last_email_time = time.time()  

        if hardhat_detected:
            last_hardhat_time = time.time()

        sideboard_text = [
            f"Hardhats: {hardhat_count}",
            f"Safety Vests: {vest_count}",
            f"People: {person_count}"
        ]

        y_position = 30
        for text in sideboard_text:
            draw_text_with_background(frame, text, (10, y_position), font_scale=0.5, color=(255, 255, 255), bg_color=(0, 0, 0), alpha=0.7, padding=5)
            y_position += 30

        if email_sent_flag and (time.time() - email_sent_time) < 3:
            draw_text_with_background(frame, "Email Sent", (frame.shape[1] - 100, 30), font_scale=0.5, color=(0, 255, 0), bg_color=(0, 0, 0), alpha=0.8, padding=5)

        video_placeholder.image(frame, channels="BGR")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def proximity_detection():
    model = YOLO('yolo11s.pt')  

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Error: Unable to access webcam.")
        return

    st.info("Press 'q' to quit.")


    video_placeholder = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Error: Unable to fetch frame from webcam.")
            break

        results = model(frame)
        detections = results[0].boxes.data.cpu().numpy() 

        objects = []
        for detection in detections:
            x1, y1, x2, y2, confidence, cls = detection
            x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
            label = model.names[int(cls)]
            objects.append({"type": label, "box": (x1, y1, x2, y2)})

        for obj in objects:
            x1, y1, x2, y2 = obj["box"]
            color = (0, 255, 0) if obj["type"] == "person" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, obj["type"], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        for obj1 in objects:
            if obj1["type"] == "person":
                for obj2 in objects:
                    if obj2["type"] == "cell phone" or obj2["type"] == "ledge":
                        danger_zone = expand_box(obj2["box"])
                        if is_in_danger(obj1["box"], danger_zone):
                            cv2.putText(frame, "ALERT!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            print(f"Alert: Person close to {obj2['type']}!")

    
        video_placeholder.image(frame, channels="BGR")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    st.title("Construction Worker Safety Application")

    selected_tab = st.sidebar.selectbox("Select Tab", ["PPE Detection", "Proximity Detection"])

    if selected_tab == "PPE Detection":
        ppe_detection()
    elif selected_tab == "Proximity Detection":
        proximity_detection()

if __name__ == "__main__":
    main()