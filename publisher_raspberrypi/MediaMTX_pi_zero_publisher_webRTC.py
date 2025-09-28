#!/usr/bin/env python3
import asyncio
import aiohttp
import cv2
import numpy as np
from av import VideoFrame
from aiortc import (
    RTCPeerConnection, RTCConfiguration, RTCIceServer,
    RTCSessionDescription, VideoStreamTrack
)
import time

# === Static Configuration ===
CAMERA_DEVICE = 0             # OpenCV index or '/dev/video0'
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FRAME_RATE = 15               # keep it low for PI Zero

SERVER_IP = "13.201.69.29"   #  OR Dynamic DNS-> SERVER_IP = "yadiec2.freedynamicdns.net"
SERVER_PORT = "8889"
MediaMTX_ENDPOINT = "cam1"

class V4L2VideoStreamTrack(VideoStreamTrack):
    kind = "video"

    def __init__(self, device=CAMERA_DEVICE):
        super().__init__()  # don't forget this
        print("[INFO] Opening V4L2 device:", device)
        # accept either int index or path
        self.cap = cv2.VideoCapture(device)
        # set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FRAME_RATE)

        # some backoff
        time.sleep(0.5)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera device")

        self._stopped = False
        print(f"[INFO] Camera opened {FRAME_WIDTH}x{FRAME_HEIGHT}@{FRAME_RATE}fps")

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        # read frame from OpenCV (blocking)
        ret, frame = await asyncio.get_event_loop().run_in_executor(None, self.cap.read)
        if not ret or frame is None:
            # fallback - black frame
            print("[WARN] Frame read failed, sending black frame")
            frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
        else:
            # OpenCV returns BGR; convert to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

    def stop(self):
        if not self._stopped:
            self._stopped = True
            try:
                self.cap.release()
            except Exception:
                pass
            print("[INFO] V4L2 capture stopped")

async def publish_stream():
    print("[INFO] Preparing WebRTC connection to MediaMTX...")
    config = RTCConfiguration(iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])])
    pc = RTCPeerConnection(configuration=config)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("[WebRTC] Connection state:", pc.connectionState)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print("[WebRTC] ICE state:", pc.iceConnectionState)

    @pc.on("track")
    def on_track(track):
        print("[WebRTC] Track added:", track.kind)

    video_track = None
    try:
        video_track = V4L2VideoStreamTrack(device=CAMERA_DEVICE)
        pc.addTrack(video_track)

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        print("[INFO] SDP offer created")

        whip_url = f"http://{SERVER_IP}:{SERVER_PORT}/{MediaMTX_ENDPOINT}/whip"
        print("[INFO] Sending offer to", whip_url)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                whip_url,
                data=pc.localDescription.sdp,
                headers={"Content-Type": "application/sdp"}
            ) as resp:
                print("[INFO] WHIP response status:", resp.status)
                if resp.status in (200, 201):
                    answer_sdp = await resp.text()
                    await pc.setRemoteDescription(RTCSessionDescription(sdp=answer_sdp, type="answer"))
                    print("[SUCCESS] WebRTC handshake done. Streaming...")
                    # keep alive
                    while pc.connectionState != "closed":
                        await asyncio.sleep(1)
                else:
                    print("[ERROR] WHIP request failed:", await resp.text())

    except Exception as e:
        print("[FATAL] Exception:", e)
    finally:
        try:
            if video_track:
                video_track.stop()
        except Exception:
            pass
        if pc and pc.connectionState != "closed":
            await pc.close()
        print("[INFO] Stream ended.")

if __name__ == "__main__":
    try:
        asyncio.run(publish_stream())
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user")
    except Exception as e:
        print("[FATAL] Unhandled:", e)
