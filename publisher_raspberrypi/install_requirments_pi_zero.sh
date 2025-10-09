#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

sudo apt update
sudo apt upgrade -y

# essential build deps
sudo apt install -y build-essential pkg-config git python3-dev python3-pip \
 libssl-dev libffi-dev libasound2-dev libpulse-dev libvpx-dev libopus-dev \
 libsrtp2-dev ffmpeg libavformat-dev libavcodec-dev libavdevice-dev \
 libavfilter-dev libavutil-dev libswscale-dev \
 python3-picamera2 python3-libcamera python3-kms++ python3-pyqt5 python3-prctl

# OpenCV (apt package for ARMv6) 
sudo apt install -y python3-opencv 

python3 -m pip install --upgrade pip setuptools wheel

# Install with --break-system-packages (NOT RECOMMENDED)
python3 -m pip install --break-system-packages av==10.0.0
python3 -m pip install --break-system-packages "aiohttp==3.8.4" "aiortc==1.5.0"
