#include <ESP8266WiFi.h>
#include "EEPROM.h"
#include "Servo.h"

//////////////////////
#define STEERING_PIN 4 // D2
//#define STEERING_PIN 15 // D8

//////////////////
#define ESC_PIN 14 // D5

////////////////
#define PWM_L 14 // D5
#define PWM_R 12 // D6

//////////////////////
#define EEPROM_SIZE 64

//////////////////////
#define LED_PIN     16 // In Board
//#define LED_PIN     2 // In Module

/////////////////
#define PORT 8000

//////////////////////////////////
const char* sta_ssid = "CLB NCKH CKD";
const char* sta_password = "clbnckhckda@";

//const char* sta_ssid = "B COFFEE";
//const char* sta_password = "208hoangdieu2";

//////////////////////////////////
IPAddress STA_IP(192, 168, 1, 3);
IPAddress STA_Gateway(192, 168, 1, 1);
IPAddress STA_Subnet(255, 255, 0, 0);
IPAddress STA_primaryDNS(8, 8, 8, 8);
IPAddress STA_secondaryDNS(8, 8, 4, 4);

////////////////////////
WiFiServer server(PORT);
WiFiClient client;

/////////////////////
Servo steering_servo;
Servo throttle_esc;

///////////////////////
bool led_toggle = true,
     client_connected = false;

String server_rx;

uint8_t server_rx_counter,
        server_rx_throttle,
        server_rx_steering;

int8_t steering_control;
uint8_t throttle_control;

int8_t steering_trim;
uint8_t throttle_trim;

uint32_t last_server_ping,
         server_ping;

////////////////////////////////
void H_Br_Control(uint8_t Speed) {
  int16_t speed_run = map(Speed, throttle_trim, 180, 0, 255);
  // Forward Position
  if (throttle_trim < Speed) {
    analogWrite(PWM_L, 0);
    analogWrite(PWM_R, speed_run);
  }
  // Backward / Brake Position
  else if (Speed < throttle_trim) {
    analogWrite(PWM_L, abs(speed_run));
    analogWrite(PWM_R, 0);
  }
  // Neutral Position
  else {
    analogWrite(PWM_L, 0);
    analogWrite(PWM_R, 0);
  }
  Serial.println("Throttle Position: " + String(speed_run));
}

///////////////////////////////
void ESC_Control(uint8_t Speed) {
  throttle_esc.write(Speed);
}

////////////////////////
void Throttle_Init(void) {
  //////////////////////
  analogWrite(PWM_L, 0);
  analogWrite(PWM_R, 0);
  //////////////////////////////////
  //throttle_esc.attach(ESC_PIN);
}

////////////////////////
void Steering_Init(void) {
  steering_servo.attach(STEERING_PIN);
}

////////////////////////////////////
void Throttle_Control(uint8_t Speed) {
  H_Br_Control(Speed);
  //ESC_Control(Speed);
}

///////////////////////////////////
void Steering_Control(int8_t Angle) {
  uint8_t steering_run = map(Angle, -90, 90, 0, 180);
  // Center Position
  if (Angle == steering_trim) {
  }
  // Left Position
  else if (Angle < steering_trim) {
  }
  // Right Position
  else if (steering_trim < Angle) {
  }
  steering_servo.write(steering_run);
  Serial.println("Steering Position: " + String(steering_run));
}

/////////////////////////
void Client_Process(void) {
  if (server_rx.indexOf("C(") >= 0 || server_rx.indexOf("S(") >= 0) {
    server_rx_counter = server_rx.substring(server_rx.indexOf('p') + 1, server_rx.indexOf('t')).toInt();
    server_rx_throttle = server_rx.substring(server_rx.indexOf('t') + 1, server_rx.indexOf('s')).toInt();
    server_rx_steering = server_rx.substring(server_rx.indexOf('s') + 1, server_rx.indexOf(')')).toInt();
    if (server_rx.indexOf("C(") >= 0) {
      steering_control = server_rx_steering;
      throttle_control = server_rx_throttle;
      ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
      Serial.println("Steering Control: " + String(steering_control) + " , " + "Throttle Control: " + String(throttle_control));
      ///////////////////////////////////
      Steering_Control(steering_control);
      Throttle_Control(throttle_control);
    }
    if (server_rx.indexOf("S(") >= 0) {
      steering_trim = server_rx_steering;
      throttle_trim = server_rx_throttle;
      //////////////////////////////////////////////////////////////////////////////////////////////////////////////
      Serial.println("Steering Trim: " + String(steering_trim) + " , " + "Throttle Trim: " + String(throttle_trim));
      ///////////////////////////////
      EEPROM.write(0, throttle_trim);
      EEPROM.write(1, steering_trim);
      EEPROM.commit();
    }
    led_toggle = !led_toggle;
    digitalWrite(LED_PIN, led_toggle);
    server_ping = millis() - last_server_ping;
    last_server_ping = millis();
    Serial.print("Ping:");
    Serial.println(server_ping);
    server_rx = "";
  }
}

////////////////
void setup(void) {

  /////////////////////
  Serial.begin(115200);

  /////////////////////////
  pinMode(LED_PIN, OUTPUT);
  led_toggle = true;
  digitalWrite(LED_PIN, led_toggle);

  //////////////////////////
  EEPROM.begin(EEPROM_SIZE);
  delay(1000);
  if (EEPROM.read(0) == 0xFF) {
    throttle_trim = 90;
    EEPROM.write(0, throttle_trim);
  }
  else throttle_trim = (uint8_t)EEPROM.read(0);
  if (EEPROM.read(1) == 0xFF) {
    steering_trim = 90;
    EEPROM.write(1, steering_trim);
  }
  else steering_trim = (uint8_t)EEPROM.read(1);
  /////////////////////////////////////
  Serial.print("Steering Trim Load: ");
  Serial.print(steering_trim);
  Serial.print(" , ");
  Serial.print("Throttle Trim Load: ");
  Serial.println(throttle_trim);

  ////////////////
  Throttle_Init();
  Throttle_Control(throttle_trim);

  ////////////////
  Steering_Init();
  Steering_Control(steering_trim);

  ////////////////////
  WiFi.mode(WIFI_STA);

  //////////////////////
  WiFi.disconnect(true);

  ///////////////////////////////////
  WiFi.begin(sta_ssid, sta_password);

  /////////////////////////////////////
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WIFI IP Address: ");
  Serial.println(WiFi.localIP());

  ///////////////
  server.begin();
}

///////////////
void loop(void) {

  client = server.available();
  if (client) {
    client_connected = true;
    while (client.connected()) {
      if (client.available() > 0) {
        char inChar = (char)client.read();
        if (inChar == '\n') {
          Client_Process();
          client.write('\n');
        }
        server_rx += inChar;
      }
    }
  }
  else {
    client_connected = false;
    led_toggle = true;
    digitalWrite(LED_PIN, led_toggle);
    throttle_control = throttle_trim;
    steering_control = steering_trim;
    last_server_ping = millis();
    server_ping = 0;
  }

  //////////
  delay(10);
}
