import cv2
import requests
import time

# ================================
# CONFIGURATION
# ================================
SERVER_URL = "http://yadiec2.freedynamicdns.net:5000/upload?cam_id=cam2"  # your backend URL
CAM_USER = "cam_1"
CAM_PASS = "cam123"
CAM_ID = "cam1"

CAPTURE_INTERVAL = 0.05  # seconds between frames (~10 FPS)
QUALITY = 50            # JPEG quality (0–100)
FRAME_WIDTH = 320       # desired width (change dynamically)
FRAME_HEIGHT = 240      # desired height (change dynamically)

# ================================
# INITIALIZE CAMERA
# ================================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not open webcam")
    exit()

# Set frame size dynamically
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# Confirm actual size
actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"✅ Webcam opened at resolution: {actual_width}x{actual_height}, streaming to server... (Ctrl+C to stop)")

# ================================
# MAIN LOOP
# ================================
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to capture frame")
        continue

    # Ensure image matches requested size (in case camera ignored cap.set)
    if (frame.shape[1], frame.shape[0]) != (FRAME_WIDTH, FRAME_HEIGHT):
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # Convert to JPEG
    _, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY])
    data = jpeg.tobytes()

    try:
        # HTTP POST like ESP32
        response = requests.post(
            SERVER_URL,
            headers={
                "Content-Type": "image/jpeg",
                "cam_id": CAM_ID
            },
            auth=(CAM_USER, CAM_PASS),
            data=data,
            timeout=5
        )

        if response.status_code == 200:
            print(f"📸 Uploaded frame ({FRAME_WIDTH}x{FRAME_HEIGHT}, {len(data)} bytes)")
        else:
            print(f"⚠️ Server response: {response.status_code}")

    except Exception as e:
        print(f"❌ Error uploading: {e}")

    time.sleep(CAPTURE_INTERVAL)

# ================================
# CLEANUP
# ================================
cap.release()
