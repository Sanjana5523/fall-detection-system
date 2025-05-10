# fall-detection-system
Elderly individuals are at a higher risk of falls and health complications due to age-related factors such as reduced mobility, weaker cardiovascular function, and chronic illnesses. Falls and abnormal vital signs, such as fluctuations in heart rate, temperature and oxygen (O₂) levels, can lead to severe injuries or even life-threatening situations. Traditional monitoring systems often require manual intervention or periodic checkups, leading to delayed response times. Therefore, an automated, real-time system that uses wearable sensors and machine learning models to detect falls and analyze vital signs is necessary for enhancing elderly care. The system utilizes a combination of OpenCV and YOLOv8 for fall detection through video stream analysis, along with wearable sensors to continuously track vital parameters such as heart rate, temperature and oxygen saturation (O₂ levels).If a fall is detected or abnormal vitals are recorded, an emergency alert is immediately sent to caregivers or medical personnel, ensuring rapid response. Simultaneously, wearable sensor measure heart rate, temperature, and oxygen levels using an ESP8266 module, along with MAX30100 (heart rate & SpO2 sensor) and LM35 (temperature sensor). If a fall or an unusual health condition is detected, an alert is  sent to caregivers. This system provides periodic health monitoring and fall detection with high accuracy, improving elderly safety and care. 




code for Aurdino IDE
#define BLYNK_TEMPLATE_ID "TMPL3URLgcp7J"
#define BLYNK_TEMPLATE_NAME "Elderly Monitoring System"
#define BLYNK_AUTH_TOKEN "ZLmBFkEVORQ7O4T5zDmPa6xT4sbUJmNo"
// 🔹 Include Libraries
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <Wire.h>
#include "MAX30100_PulseOximeter.h"

// 🔹 Define I2C Pins for MAX30100 (ESP8266)
#define SDA_PIN 4  // D2 = GPIO4
#define SCL_PIN 5  // D1 = GPIO5

// 🔹 Wi-Fi Credentials (Replace with your details)
char ssid[] = "OnePlus Nord CE 2";
char pass[] = "12341234";

// 🔹 Initialize Blynk & MAX30100
PulseOximeter pox;
BlynkTimer timer;
uint32_t lastReportTime = 0;

// 🔹 Callback function for heartbeats
void onBeatDetected() {
    Serial.println("💓 Heartbeat detected!");
}

// 🔹 Blynk Function to Send Sensor Data
void sendSensorData() {
    // Read Temperature (LM35)
    int sensorValue = analogRead(A0);
    float voltage = sensorValue * (3.3 / 1023.0);  // Convert ADC value to voltage
    float temperature = voltage * 100;  // LM35: 10mV per °C

    // Update MAX30100 (Heart Rate & SpO2)
    pox.update();
    float heartRate = pox.getHeartRate();
    float spo2 = pox.getSpO2();

    // Send Data to Blynk Dashboard
    Blynk.virtualWrite(V0, temperature);
    Blynk.virtualWrite(V3, heartRate);
    Blynk.virtualWrite(V4, spo2);

    // Display Data in Serial Monitor
    Serial.println("---------------------------");
    Serial.print("🌡 Temperature: "); Serial.print(temperature); Serial.println(" °C");
    Serial.print("💓 Heart Rate: "); Serial.print(heartRate); Serial.println(" BPM");
    Serial.print("🩸 SpO2: "); Serial.print(spo2); Serial.println(" %");
    Serial.println("---------------------------");

    // 🔹 Send Alerts if Conditions Met
    if (temperature > 38.0) {
        Blynk.logEvent("high_fever_alert", "🚨 High Fever Alert! Temp: " + String(temperature) + "°C");
    }
    if (heartRate < 50 || heartRate > 120) {
        Blynk.logEvent("heart_rate_alert", "⚠ Abnormal Heart Rate! BPM: " + String(heartRate));
    }
}

// 🔹 Setup Function
void setup() {
    Serial.begin(115200);
    
    // Initialize I2C Communication
    Wire.begin(SDA_PIN, SCL_PIN);  // SDA = D2, SCL = D1
    Serial.println("I2C Initialized ✅");

    // Connect to Wi-Fi & Blynk
    Serial.println("Connecting to Blynk...");
    Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
    Serial.println("Blynk Connected ✅");

    // Initialize MAX30100
    Serial.println("Initializing MAX30100...");
    if (!pox.begin()) {
        Serial.println("❌ MAX30100 INIT FAILED. Check connections!");
        while (1);
    } else {
        Serial.println("MAX30100 READY ✅");
    }
    pox.setOnBeatDetectedCallback(onBeatDetected);  // Detect heartbeat
    
    // Call sendSensorData() every 1 second
    timer.setInterval(1000L, sendSensorData);
}

// 🔹 Loop Function
void loop() {
    Blynk.run();   // Run Blynk
    timer.run();   // Run timer for periodic updates
    pox.update();  // Update Pulse Oximeter readings
}
