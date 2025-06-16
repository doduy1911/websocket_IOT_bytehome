import websocket
import threading
import json
import time
import cv2
import requests
from gpio_helper import GPIO as GPIO

# --- Config ---
USER_ID = "u2s"
DEVICE_ID = "d1"
SERVER_WS = "ws://42.116.105.110:3000/ws"
SERVER_API = f"http://42.116.105.110:3000/api/stream-frames/{USER_ID}/{DEVICE_ID}"

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
        print("[Camera] ❌ Cannot open camera")
        streaming = False
        return

    print("[Camera] ✅ Started streaming")

    try:
        while streaming:
            ret, frame = cap.read()
            if not ret:
                print("[Camera] ❌ Failed to read frame")
                break

            _, img_encoded = cv2.imencode('.jpg', frame)
            try:
                resp = requests.post(SERVER_API, data=img_encoded.tobytes(), headers={
                    'Content-Type': 'image/jpeg'
                })
                print(f"[Camera] ✅ Frame sent: {resp.status_code}")
            except Exception as e:
                print(f"[Camera] ❌ Error sending frame: {e}")

            time.sleep(0.1)  # throttle frame rate
    finally:
        cap.release()
        print("[Camera] 📷 Stream stopped (camera released)")

# --- Start / Stop streaming ---
def start_stream():
    global streaming, stream_thread
    if not streaming:
        print("[Camera] ▶️ Starting stream...")
        streaming = True
        stream_thread = threading.Thread(target=stream_loop)
        stream_thread.start()

def stop_stream():
    global streaming, stream_thread
    if streaming:
        print("[Camera] ⏹ Stopping stream...")
        streaming = False
        if stream_thread:
            stream_thread.join()
            print("[Camera] ✅ Stream fully stopped")

# --- Handle command ---
def handle_command(cmd):
    command = cmd.get("command")
    print(f"[WebSocket] 📥 Received command: {command}")

    if command == "TURN_ON_LIGHT":
        GPIO.output(LED_PIN, GPIO.HIGH)
        print("[GPIO] 💡 Light ON")
    elif command == "TURN_OFF_LIGHT":
        GPIO.output(LED_PIN, GPIO.LOW)
        print("[GPIO] 💡 Light OFF")
    elif command == "START_CAMERA":
        start_stream()
    elif command == "STOP_CAMERA":
        stop_stream()
    else:
        print(f"[WebSocket] ⚠️ Unknown command: {command}")

# --- WebSocket Callbacks ---
def on_message(ws, message):
    try:
        data = json.loads(message)
        handle_command(data)
    except Exception as e:
        print(f"[WebSocket] ❌ Error handling message: {e}")

def on_open(ws):
    register = {
        "type": "REGISTER",
        "userId": USER_ID,
        "deviceId": DEVICE_ID
    }
    ws.send(json.dumps(register))
    print("[WebSocket] ✅ Registered with server")

def on_error(ws, error):
    print(f"[WebSocket] ❌ Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("[WebSocket] 🔌 Connection closed")
    stop_stream()  # stop camera if running

# --- Main Entry ---
def run():
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        SERVER_WS,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("❗ Exiting...")
    finally:
        stop_stream()
        GPIO.cleanup()
