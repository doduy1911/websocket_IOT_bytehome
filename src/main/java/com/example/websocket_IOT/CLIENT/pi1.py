import websocket
import threading
import json
import time
import cv2
import requests
from gpio_helper import GPIO  # <-- dùng module mới

# Tạo đối tượng GPIO (dù là thật hay giả lập)
gpio = GPIO()

# Khai báo user/device (gán cố định cho từng Pi)
USER_ID = "u1"
DEVICE_ID = "d1"
SERVER_WS = "ws://42.116.105.110:3000/ws"
SERVER_API = f"http://42.116.105.110:3000/stream-frames/{USER_ID}/{DEVICE_ID}"

# GPIO setup (LED pin)
LED_PIN = 18
gpio.setmode(gpio.BCM)
gpio.setup(LED_PIN, gpio.OUT)

# Hàm xử lý các command gửi về từ server
def handle_command(cmd):
    command = cmd.get("command")
    print(f"[Received command]: {command}")

    if command == "TURN_ON_LIGHT":
        gpio.output(LED_PIN, gpio.HIGH)
    elif command == "TURN_OFF_LIGHT":
        gpio.output(LED_PIN, gpio.LOW)
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
        gpio.cleanup()
