
#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// ===================
// Select camera model
// ===================
#define CAMERA_MODEL_AI_THINKER  // Has PSRAM
#include "camera_pins.h"

// WiFi
const char* ssid = "Airtel_Ahalawat";
const char* password = "Yadi1234";

// Server URL
const char* serverUrl = "http://yadiec2.freedynamicdns.net:5000/upload?cam_id=cam1";


// Camera login credentials (Basic Auth)
const char* camUser = "cam_1";
const char* camPass = "cam123";

// Capture rate
#define CAPTURE_INTERVAL 1  // ~10 FPS

unsigned long lastCapture = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi connected! IP: ");
  Serial.println(WiFi.localIP());

  // ---- Camera config ----
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;  // 320x240 for good speed
  config.jpeg_quality = 10;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;

  esp_camera_init(&config);
}

void loop() {
  if (millis() - lastCapture < CAPTURE_INTERVAL) return;
  lastCapture = millis();


  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) return;


  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(serverUrl);

    // Add Basic Auth header
    http.setAuthorization(camUser, camPass);

    // JPEG content
    http.addHeader("cam_id", "cam1");
    http.addHeader("Content-Type", "image/jpeg");

    int code = http.POST(fb->buf, fb->len);
    if (code > 0) {
      String response = http.getString();  // read control commands
      Serial.printf("Response: %s\n", response.c_str());

      // Check for control commands
      if (response.indexOf("STOP") >= 0) {
        Serial.println("Stopping stream...");
        while (true) delay(1000);  // stop forever or until reset
      }

      if (response.indexOf("QUALITY:") >= 0) {
        int q = response.substring(response.indexOf("QUALITY:") + 8).toInt();
        sensor_t* s = esp_camera_sensor_get();
        s->set_quality(s, q);
        Serial.printf("Quality changed to %d\n", q);
      }

      if (response.indexOf("RESOLUTION:") >= 0) {
        String res = response.substring(response.indexOf("RESOLUTION:") + 11);
        res.trim();
        sensor_t* s = esp_camera_sensor_get();
        if (res == "QVGA") s->set_framesize(s, FRAMESIZE_QVGA);
        else if (res == "VGA") s->set_framesize(s, FRAMESIZE_VGA);
        else if (res == "SVGA") s->set_framesize(s, FRAMESIZE_SVGA);
        Serial.printf("Resolution changed to %s\n", res.c_str());
      }
    }

    http.end();
  }

  esp_camera_fb_return(fb);
}
