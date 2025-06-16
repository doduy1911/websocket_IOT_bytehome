import websocket
import threading
import json
import time
import cv2
import requests
from gpio_helper import GPIO  # <-- dùng module mới

# --- Config ---
USER_ID = "u1"
DEVICE_ID = "d1"
SERVER_WS = "ws://42.116.105.110:3000/ws"
SERVER_API = f"http://42.116.105.110:3000/stream-frames/{USER_ID}/{DEVICE_ID}"

LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# --- Globals ---
streaming = False
stream_thread = None

# --- Streaming Function ---
def stream_loop():
    global streaming
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        streaming = False
        return

    try:
        while streaming:
            ret, frame = cap.read()
            if not ret:
                break

            _, img_encoded = cv2.imencode('.jpg', frame)
            requests.post(SERVER_API, data=img_encoded.tobytes(), headers={
                'Content-Type': 'image/jpeg'
            })

            time.sleep(0.1)
    except Exception as e:
        print(f"[Streaming error]: {e}")
    finally:
        cap.release()

# --- Start / Stop streaming ---
def start_stream():
    global streaming, stream_thread
    if not streaming:
        print("[Camera] Starting stream...")
        streaming = True
        stream_thread = threading.Thread(target=stream_loop)
        stream_thread.start()

def stop_stream():
    global streaming, stream_thread
    if streaming:
        print("[Camera] Stopping stream...")
        streaming = False
        if stream_thread:
            stream_thread.join()
            print("[Camera] Stream stopped.")

# --- Handle command ---
def handle_command(cmd):
    command = cmd.get("command")
    print(f"[Received command]: {command}")

    if command == "TURN_ON_LIGHT":
        GPIO.output(LED_PIN, GPIO.HIGH)
    elif command == "TURN_OFF_LIGHT":
        GPIO.output(LED_PIN, GPIO.LOW)
    elif command == "START_CAMERA":
        start_stream()
    elif command == "STOP_CAMERA":
        stop_stream()
    else:
        print(f"[Unknown command]: {command}")

# --- WebSocket callbacks ---
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
    stop_stream()  # đảm bảo dừng stream nếu WS bị đóng

# --- Main ---
def run():
    websocket.enableTrace(False)
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
        stop_stream()
        GPIO.cleanup()
