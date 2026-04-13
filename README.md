# 🎥 Internet-Based Camera Streamer

Stream live video over the internet from anywhere in the world using Raspberry Pi(as a Publisher) and AWS ec2(as a webRTC server).

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-None-lightgrey)
![Stars](https://img.shields.io/github/stars/Priyanshu-choudhary/Internet_based_camera?style=social)
![Forks](https://img.shields.io/github/forks/Priyanshu-choudhary/Internet_based_camera?style=social)
![Language](https://img.shields.io/badge/language-Python-blue)


<!-- ## ✨ Features

*   🌍 **Global Access:** Stream live video from your camera to any internet-connected device, anywhere in the world.
*   🚀 **Lightweight Publisher:** Designed for Raspberry Pi, the publisher is optimized for low-resource environments.
*   ☁️ **Cloud-Powered Server:** Utilizes AWS to provide a robust and scalable video streaming server.
*   🔒 **Secure Streaming (Planned):** Future enhancements will include secure authentication and encrypted streams.
*   🔧 **Modular Architecture:** Clear separation between publisher (Raspberry Pi) and server (AWS) components for easy deployment and maintenance. -->


## ⚙️ Installation Guide

This project consists of two main components: the `publisher` and the `server`. Both require Python and specific dependencies.

### Prerequisites

*   Raspberry pi  with camera and working AWS ec2 server.

### 1. Clone the Repository

First, clone the repository to both your Raspberry Pi and your AWS server instance:

```bash
sudo apt-get install git
git clone https://github.com/Priyanshu-choudhary/Internet_based_camera.git
cd Internet_based_camera/publisher_raspberrypi
sudo install_requirments_pi_zero.sh

```

### 2. setup Publisher (Raspberry Pi Zero) Setup

Navigate to the `publisher_raspberrypi` directory and install the required Python packages.

```bash
cd publisher_raspberrypi
sudo bash insatll_requirments_pi_zero.sh
```

#### Environment Configuration

You will need to configure the IP address or hostname of your AWS server. Inside the MediaMTX_pi_zero_publisher_webRTC.py file.

```python
# Example: In publisher_script.py or a config file
SERVER_HOST = "your_aws_server_ip_or_hostname"
SERVER_PORT = "8889"
```

### 3. Server (AWS) Setup

Navigate to the `server_AWS` directory on your AWS instance and install the MediaMTX server and copy past the mediaMTX config as given.

```bash
cd server_AWS
./mediaMTX


```

#### AWS Security Group Configuration

Ensure your AWS EC2 instance's security group allows inbound traffic on the port your server will be listening on from the IP address of your Raspberry Pi, or from `0.0.0.0/0`. as given in the image.

![AWS security inbound rules](/server_AWS/security_group_inbound_port.jpeg)

#### (OPTIONAL) run MediaMTX automatic
 
we can also run the mediaMTX server as a system runtime service. 
```bash
# Add the file mediamtx.service given in the server_AWS folder 
sudo nano /etc/systemd/system/mediamtx.service
sudo systemctl daemon-reload
sudo systemctl enable runDockerImg.service
sudo systemctl restart runDockerImg.service
sudo systemctl status runDockerImg.service
```

## 🚀 Usage Examples

### 1. Start the Server (AWS) FIRST

On your AWS server instance, run the MediaMTX server as describe above and config the inbound security ports in aws:


### 2. Start the Publisher (Raspberry Pi)

On your Raspberry Pi, run the publisher python code:

```bash
cd publisher_raspberrypi
#Remember to add the AWS ip/hostname in this python code.
python MediaMTX_pi_zero_publisher_webRTC.py
```

The Raspberry Pi camera will start capturing video and sending it to the configured AWS server.
### 2. Run this code as systemd services

✅ start this Python script at boot
✅ restart it automatically on crash or error
✅ log output to journald (so you can check logs anytime)
✅ run it with high CPU scheduling priority (-20)

🧰 Step 1: Create a systemd service file
```bash
sudo nano /etc/systemd/system/mediastream.service
```
past this.
```bash
[Unit]
Description=Raspberry Pi Media Stream Publisher (WebRTC)
After=network.target

[Service]
# Full path to Python and script
ExecStart=/usr/bin/python3 /home/zero1/Internet_based_camera/publisher/MediaMTX_pi_3_publisher_webRTC.py

# Working directory
WorkingDirectory=/home/zero1/Internet_based_camera/publisher

# Restart automatically if crashes
Restart=always
RestartSec=5

# Redirect stdout/stderr to systemd journal
StandardOutput=append:/var/log/mediastream.log
StandardError=append:/var/log/mediastream_error.log

# Run as the 'pi' user
User=zero1
Group=zero1

# Highest CPU priority (nice value -20 = highest)
Nice=-20

# Optional: limit restarts to prevent loops
#StartLimitIntervalSec=60
#StartLimitBurst=5

# Optional: environment variables (uncomment if needed)
# Environment="PYTHONUNBUFFERED=1"

#logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

🔄 Step 3: Reload, enable, and start the service

```bash
#Then create the log files manually first:
sudo touch /var/log/mediastream.log /var/log/mediastream_error.log
sudo chown zero1:zero1 /var/log/mediastream*.log

sudo systemctl daemon-reload
sudo systemctl enable mediastream.service
sudo systemctl start mediastream.service

```

🧾 Step 4: Check your logs
```bash
sudo systemctl status mediastream.service
cat /var/log/mediastream.log
cat /var/log/mediastream_error.log
tail -f /var/log/mediastream.log
sudo journalctl -u mediastream.service -f
```

### 3. Consume the Stream (Client)

open this url in any browser.
```python
http://<AWS-IP/Hostname>:8889/cam1/

```

## 📄 License Information

This project currently has **no explicit license**.

This means that, by default, standard copyright law applies, and you do not have explicit permission to use, copy, distribute, or modify this software. If you wish to use this project, please contact the main contributor, Priyanshu-choudhary, to request permission.

**Main Contributor:** Priyanshu-choudhary
