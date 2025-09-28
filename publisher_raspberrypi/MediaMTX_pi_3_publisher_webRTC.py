import cv2
import asyncio
import aiohttp
from av import VideoFrame
from picamera2 import Picamera2
from libcamera import Transform
import numpy as np
from aiortc import (
    RTCPeerConnection, RTCConfiguration, RTCIceServer,
    RTCSessionDescription, VideoStreamTrack
)

# === Static Configuration ===
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_RATE=20

SERVER_IP = "yadiec2.freedynamicdns.net"
SERVER_PORT = "8889"
MediaMTX_ENDPOINT = "cam1"

# === Improved Webcam Video Stream Track ===
class WebcamVideoStreamTrack(VideoStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()
        print("[INFO] Initializing Picamera2...")

        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(
            main={"size": (FRAME_WIDTH, FRAME_HEIGHT), "format": "YUV420"},
            controls={"FrameRate": FRAME_RATE},
            transform=Transform(hflip=1, vflip=1)
        )


        # Rotate camera 180° if needed
        # config["transform"] = Transform(hflip=1, vflip=1)

        self.picam2.configure(config)
        self.picam2.start()
        print(f"[INFO] Picamera2 initialized at {FRAME_WIDTH}x{FRAME_HEIGHT}")

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        try:
            frame = self.picam2.capture_array()  # numpy array

            frame = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_I420)  # convert to RGB

            video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
            video_frame.pts = pts
            video_frame.time_base = time_base
            return video_frame

        except Exception as e:
            print(f"[ERROR] Frame capture error: {e}")
            # Return black frame fallback
            frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
            video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
            video_frame.pts = pts
            video_frame.time_base = time_base
            return video_frame

    def stop(self):
        if self.picam2:
            self.picam2.stop()
            print("[INFO] Picamera2 stopped")

# === Main function with error handling ===
async def publish_stream():
    print("[INFO] Preparing WebRTC connection to MediaMTX...")

    # WebRTC configuration
    config = RTCConfiguration(
        iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
    )
    pc = RTCPeerConnection(configuration=config)

    # Enhanced event handlers
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        state = pc.connectionState
        print(f"[WebRTC] Connection state: {state}")
        if state == "failed":
            print("[ERROR] WebRTC connection failed")
        elif state == "connected":
            print("[SUCCESS] WebRTC fully connected!")

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        state = pc.iceConnectionState
        print(f"[WebRTC] ICE connection state: {state}")

    @pc.on("track")
    def on_track(track):
        print(f"[WebRTC] Track added: {track.kind}")

    try:
        # Create and attach video track
        video_track = WebcamVideoStreamTrack()
        pc.addTrack(video_track)

        # Create SDP offer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        print("[INFO] SDP offer created successfully")

        # Send to WHIP endpoint
        whip_url = f"http://{SERVER_IP}:{SERVER_PORT}/{MediaMTX_ENDPOINT}/whip"
        print(f"[INFO] Sending offer to: {whip_url}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                whip_url,
                data=pc.localDescription.sdp,
                headers={"Content-Type": "application/sdp"}
            ) as resp:

                print(f"[INFO] WHIP response status: {resp.status}")

                if resp.status == 201:
                    answer_sdp = await resp.text()
                    await pc.setRemoteDescription(
                        RTCSessionDescription(sdp=answer_sdp, type="answer")
                    )
                    print("[SUCCESS] WebRTC handshake completed!")

                    # Keep the connection alive
                    print("[INFO] Streaming started. Press Ctrl+C to stop.")
                    while pc.connectionState != "closed":
                        await asyncio.sleep(1)

                else:
                    error_text = await resp.text()
                    print(f"[ERROR] WHIP failed: {error_text}")
                    return

    except Exception as e:
        print(f"[ERROR] Publishing failed: {e}")
    finally:
        # Cleanup
        if pc.connectionState != "closed":
            await pc.close()
        print("[INFO] Stream ended.")

# === Entry Point ===
if __name__ == "__main__":
    # Add numpy import at the top if using fallback frames
    import numpy as np

    try:
        asyncio.run(publish_stream())
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user")
    except Exception as e:
        print(f"[FATAL] Unhandled exception: {e}")