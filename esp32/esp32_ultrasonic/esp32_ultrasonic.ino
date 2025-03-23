#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "ESP32_Car";   // Hotspot name
const char* password = "12345678"; // Password (8+ chars required)

IPAddress local_IP(192, 168, 1, 1);   // Fixed IP for ESP32
IPAddress gateway(192, 168, 1, 1);    // Gateway (same as ESP IP)
IPAddress subnet(255, 255, 255, 0);   // Subnet mask


WiFiUDP udp;
const int udpPort = 1234;

const int motorPWM = 5;
const int motorDIR = 4;
const int servo1Pin = 18;
const int servo2Pin = 19;

const int trigPin1 = 32, echoPin1 = 33;
const int trigPin2 = 25, echoPin2 = 26;
const int trigPin3 = 27, echoPin3 = 14;

const int pwmChannel = 0;
const int pwmFreq = 1000;
const int pwmResolution = 8;

int servo1 = 0, servo2 = 0, motorSpeed = 0;
int sensor1 = 0, sensor2 = 0, sensor3 = 0;

void setup() {
    Serial.begin(115200);
    // Configure soft AP with fixed IP
    if (!WiFi.softAPConfig(local_IP, gateway, subnet)) {
        Serial.println("AP Config Failed");
    }
    WiFi.softAP(ssid, password);

    udp.begin(udpPort);

    pinMode(motorDIR, OUTPUT);
    pinMode(trigPin1, OUTPUT);
    pinMode(echoPin1, INPUT);
    pinMode(trigPin2, OUTPUT);
    pinMode(echoPin2, INPUT);
    pinMode(trigPin3, OUTPUT);
    pinMode(echoPin3, INPUT);

    ledcSetup(pwmChannel, pwmFreq, pwmResolution);
    ledcAttachPin(motorPWM, pwmChannel);
    
    // xTaskCreatePinnedToCore parameters:
    // param 1: Task function pointer - sensorTask is the function to run
    // param 2: Task name - "SensorTask" is used for debugging/monitoring
    // param 3: Stack size in bytes - 2000 bytes allocated for task stack
    // param 4: Task parameters - NULL since no parameters needed
    // param 5: Task priority - 1 (low priority, 0-24 range)
    // param 6: Task handle - NULL since we don't need to reference task later
    // param 7: Core ID - 0 means run on core 0 (Arduino core runs on core 1)



    xTaskCreatePinnedToCore(sensorTask, "SensorTask", 2000, NULL, 1, NULL, 0);
}

void sensorTask(void *param) {
    while (1) {
        sensor1 = getDistance(trigPin1, echoPin1);
        sensor2 = getDistance(trigPin2, echoPin2);
        sensor3 = getDistance(trigPin3, echoPin3);
        delay(30);
    }
}

int getDistance(int trig, int echo) {
    digitalWrite(trig, LOW);
    delayMicroseconds(2);
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);
    // Calculate timeout for 1m distance
    // Speed of sound = 343 m/s = 0.343 mm/us
    // Time for 1m round trip = (1000mm * 2) / 0.343 = ~5830 microseconds
    int duration = pulseIn(echo, HIGH, 5830);
    if (duration == 0) {
        return 999; // Return 999 if timeout triggered
    }
    return duration * 0.034 / 2;
}

void setMotorSpeed(int value) {
    int pwm = map(abs(value), 0, 128, 0, 255);
    digitalWrite(motorDIR, value >= 0 ? HIGH : LOW);
    ledcWrite(pwmChannel, pwm);
}

void loop() {
    char packet[13];
    int packetSize = udp.parsePacket();
    if (packetSize) {
        udp.read(packet, 13);
        servo1 = packet[0];
        servo2 = packet[1];
        motorSpeed = packet[2];
        setMotorSpeed(motorSpeed);
    }

    static unsigned long lastSendTime = 0;
    unsigned long currentTime = millis();
    
    if (currentTime - lastSendTime >= 30) {
        char response[16];
        memcpy(response, &servo1, 1);
        memcpy(response + 1, &servo2, 1);
        memcpy(response + 2, &motorSpeed, 1);
        memcpy(response + 3, &sensor1, 2);
        memcpy(response + 5, &sensor2, 2);
        memcpy(response + 7, &sensor3, 2);

        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.write(response, 16);
        udp.endPacket();
        
        lastSendTime = currentTime;
    }
}
