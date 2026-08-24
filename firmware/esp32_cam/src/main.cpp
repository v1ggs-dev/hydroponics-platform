/**
 * =============================================================================
 * Hydroponics Platform — ESP32-CAM Wired Ingestion Firmware
 * Board: AI-Thinker ESP32-CAM (OV2640) with USB Shield
 * =============================================================================
 */

#include "esp_camera.h"
#include <Arduino.h>

// AI-Thinker ESP32-CAM Pin Definitions
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Onboard Flash LED (GPIO 4) & Status LED (GPIO 33 - Inverted)
#define FLASH_LED_PIN      4
#define STATUS_LED_PIN    33

void initCamera() {
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

  // PSRAM optimization
  if (psramFound()) {
    config.frame_size = FRAMESIZE_SVGA; // 800x600 (High detail & fast transfer)
    config.jpeg_quality = 12;           // 0-63 (lower = higher quality)
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_VGA;  // 640x480
    config.jpeg_quality = 15;
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("ERR: Camera init failed with error 0x%x\n", err);
    return;
  }

  // Sensor adjustments for plant canopy observation
  sensor_t *s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_brightness(s, 1);     // -2 to 2
    s->set_contrast(s, 1);       // -2 to 2
    s->set_saturation(s, 1);     // -2 to 2 (enhance green hues)
    s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
    s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
    s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
  }

  Serial.println("STATUS: Camera initialized successfully.");
}

void captureAndSendFrame() {
  digitalWrite(STATUS_LED_PIN, LOW); // Turn on red status LED during capture

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("ERR: Frame capture failed");
    digitalWrite(STATUS_LED_PIN, HIGH);
    return;
  }

  // Send framing envelope
  Serial.printf("\n---FRAME_START:%u---\n", fb->len);
  Serial.write(fb->buf, fb->len);
  Serial.print("\n---FRAME_END---\n");

  esp_camera_fb_return(fb);
  digitalWrite(STATUS_LED_PIN, HIGH); // Turn off status LED
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(FLASH_LED_PIN, OUTPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(FLASH_LED_PIN, LOW);
  digitalWrite(STATUS_LED_PIN, HIGH);

  Serial.println("\n[Hydroponics ESP32-CAM Node] Initializing...");
  initCamera();
  Serial.println("READY: Send 'c' or 'CAPTURE' to take photo.");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "c" || cmd == "CAPTURE") {
      captureAndSendFrame();
    } else if (cmd == "FLASH_ON") {
      digitalWrite(FLASH_LED_PIN, HIGH);
      Serial.println("STATUS: Flash ON");
    } else if (cmd == "FLASH_OFF") {
      digitalWrite(FLASH_LED_PIN, LOW);
      Serial.println("STATUS: Flash OFF");
    } else if (cmd == "PING") {
      Serial.println("PONG: ESP32-CAM ONLINE");
    }
  }
  delay(10);
}
