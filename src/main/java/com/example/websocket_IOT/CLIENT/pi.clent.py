import websocket
import threading
import json
import time
import cv2
import requests
import RPi.GPIO as GPIO

# Khai báo user/device (gán cố định cho từng Pi)
USER_ID = "u1"
DEVICE_ID = "d1"
SERVER_WS = "ws://your-server-ip:8080/ws"
SERVER_API = f"http://your-server-ip:8080/stream-frames/{USER_ID}/{DEVICE_ID}"

# GPIO setup (LED pin)
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Hàm xử lý các command gửi về từ server
def handle_command(cmd):
    command = cmd.get("command")
    print(f"[Received command]: {command}")

    if command == "TURN_ON_LIGHT":
        GPIO.output(LED_PIN, GPIO.HIGH)
    elif command == "TURN_OFF_LIGHT":
        GPIO.output(LED_PIN, GPIO.LOW)
    elif command == "START_CAMERA":
        start_stream()
    else:
        print(f"[Unknown command]: {command}")

# Hàm gửi MJPEG stream từ camera
def start_stream():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            _, img_encoded = cv2.imencode('.jpg', frame)
            requests.post(SERVER_API, data=img_encoded.tobytes(), headers={
                'Content-Type': 'image/jpeg'
            })

            time.sleep(0.1)  # Throttle frame rate
    except Exception as e:
        print(f"[Streaming error]: {e}")
    finally:
        cap.release()

# Hàm khi nhận được message WebSocket
def on_message(ws, message):
    try:
        data = json.loads(message)
        handle_command(data)
    except Exception as e:
        print(f"[Error handling message]: {e}")

def on_open(ws):
    # Gửi thông tin đăng ký khi kết nối WebSocket thành công
    register = {
        "type": "REGISTER",
        "userId": USER_ID,
        "deviceId": DEVICE_ID
    }
    ws.send(json.dumps(register))
    print("[Registered with server]")

def on_error(ws, error):
    print(f"[WebSocket Error]: {error}")

def on_close(ws, close_status_code, close_msg):
    print("[WebSocket Closed]")

# Khởi chạy WebSocket
def run():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(SERVER_WS,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()
