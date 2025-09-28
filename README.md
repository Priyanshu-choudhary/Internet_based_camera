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
git clone https://github.com/Priyanshu-choudhary/Internet_based_camera.git
cd Internet_based_camera
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

### 3. Consume the Stream (Client)

open this url in any browser.
```python
http://<AWS-IP/Hostname>:8889/cam1/

```

## 📄 License Information

This project currently has **no explicit license**.

This means that, by default, standard copyright law applies, and you do not have explicit permission to use, copy, distribute, or modify this software. If you wish to use this project, please contact the main contributor, Priyanshu-choudhary, to request permission.

**Main Contributor:** Priyanshu-choudhary