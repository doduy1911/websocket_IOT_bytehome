import websocket
import threading
import json
import time
import cv2
import requests
from gpio_helper import GPIO  # Dùng mô phỏng hoặc import RPi.GPIO nếu chạy thật

# --- Khởi tạo GPIO ---
gpio = GPIO()
LED_PIN = 18
gpio.setmode(gpio.BCM)
gpio.setup(LED_PIN, gpio.OUT)

# --- Config thiết bị ---
USER_ID = "u1"
DEVICE_ID = "d1"
SERVER_WS = "ws://42.116.105.110:3000/ws"
SERVER_API = f"http://42.116.105.110:3000/api/stream-frames/{USER_ID}/{DEVICE_ID}"

# --- Trạng thái camera ---
streaming = False
stream_thread = None

# --- Hàm stream video ---
def stream_video():
    global streaming
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không mở được camera")
        streaming = False
        return

    print("🎥 Camera đang stream...")
    try:
        while streaming:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Không đọc được frame, thử lại...")
                time.sleep(0.5)
                continue

            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])  # Nén ảnh
            try:
                res = requests.post(
                    SERVER_API,
                    data=buffer.tobytes(),
                    headers={'Content-Type': 'image/jpeg'},
                    timeout=2
                )
                if res.status_code != 200:
                    print(f"[Server trả lỗi]: {res.status_code} - {res.text}")
            except Exception as e:
                print(f"[Lỗi gửi ảnh]: {e}")
                time.sleep(0.5)  # Đợi trước khi thử lại

            time.sleep(0.1)  # Giảm tải CPU

    except Exception as e:
        print(f"[Lỗi vòng lặp stream]: {e}")
    finally:
        cap.release()
        streaming = False
        print("🛑 Camera đã tắt")

# --- Điều khiển stream ---
def start_stream():
    global streaming, stream_thread
    if streaming:
        print("⚠️ Stream đã chạy, bỏ qua...")
        return

    streaming = True
    stream_thread = threading.Thread(target=stream_video)
    stream_thread.daemon = True
    stream_thread.start()
    print("[Camera streaming started]")

def stop_stream():
    global streaming
    streaming = False
    if stream_thread is not None:
        stream_thread.join(timeout=2)
        print("[Camera streaming stopped]")

# --- Xử lý command từ WebSocket ---
def handle_command(cmd):
    command = cmd.get("command")
    print(f"[Lệnh nhận được]: {command}")

    if command == "TURN_ON_LIGHT":
        gpio.output(LED_PIN, gpio.HIGH)
        print("💡 Đèn bật")
    elif command == "TURN_OFF_LIGHT":
        gpio.output(LED_PIN, gpio.LOW)
        print("💡 Đèn tắt")
    elif command == "START_CAMERA":
        start_stream()
    elif command == "STOP_CAMERA":
        stop_stream()
    else:
        print(f"[Lệnh không xác định]: {command}")

# --- WebSocket callback ---
def on_message(ws, message):
    try:
        data = json.loads(message)
        handle_command(data)
    except Exception as e:
        print(f"[Lỗi xử lý message]: {e}")

def on_open(ws):
    ws.send(json.dumps({
        "type": "REGISTER",
        "userId": USER_ID,
        "deviceId": DEVICE_ID
    }))
    print("✅ Đã đăng ký WebSocket")

def on_close(ws, close_status_code, close_msg):
    print(f"🔌 WebSocket đóng: {close_status_code} - {close_msg}")
    stop_stream()

def on_error(ws, error):
    print(f"[WebSocket lỗi]: {error}")

# --- Khởi chạy WebSocket ---
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

# --- Main ---
if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("⏹ Kết thúc chương trình")
    finally:
        stop_stream()
        gpio.cleanup()