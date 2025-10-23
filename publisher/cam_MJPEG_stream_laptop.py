import cv2
import requests
import base64
import time

# ================================
# CONFIGURATION
# ================================
SERVER_URL = "http://yadiec2.freedynamicdns.net:5000/upload?cam_id=cam2"  # your backend URL
CAM_USER = "cam_1"
CAM_PASS = "cam123"
CAM_ID = "cam1"

CAPTURE_INTERVAL = 0.1  # seconds between frames (~10 FPS)
QUALITY = 10  # JPEG quality (0–100, higher = better quality)

# ================================
# INITIALIZE CAMERA
# ================================
cap = cv2.VideoCapture(0)  # 0 = default webcam
if not cap.isOpened():
    print("❌ Could not open webcam")
    exit()

print("✅ Webcam opened, streaming to server... Press Ctrl+C to stop.")

# ================================
# MAIN LOOP
# ================================
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to capture frame")
        continue

    # Convert to JPEG
    _, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY])
    data = jpeg.tobytes()

    try:
        # HTTP POST like ESP32
        response = requests.post(
            f"{SERVER_URL}",
            headers={
                "Content-Type": "image/jpeg",
                "cam_id": CAM_ID
            },
            auth=(CAM_USER, CAM_PASS),
            data=data,
            timeout=5
        )

        if response.status_code == 200:
            print(f"📸 Uploaded frame ({len(data)} bytes)")
        else:
            print(f"⚠️ Server response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error uploading: {e}")

    time.sleep(CAPTURE_INTERVAL)

# ================================
# CLEANUP
# ================================
cap.release()
