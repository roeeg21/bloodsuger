/*
  sugarpixal — ESP8266 + 4× MAX7219 (8×8) Glucose Display

  Layout (modules left → right):
    Module 0 : units   (ones)
    Module 1 : tens
    Module 2 : hundreds
    Module 3 : trend arrow

  Examples:
    5   → [5] [ ] [ ] [arrow]
    86  → [6] [8] [ ] [arrow]
    145 → [5] [4] [1] [arrow]   (LSD at left)
*/

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <LedControl.h>

// ---------- Wi-Fi ----------
const char* WIFI_SSID     = " ";
const char* WIFI_PASSWORD = " ";

// ---------- API ----------
const char* API_HOST = " ";
const char* API_PATH = "/";

const bool USE_HTTPS = true;
const int  API_PORT  = USE_HTTPS ? 443 : 80;

// ---------- MAX7219 ----------
const int DIN_PIN = D8;
const int CLK_PIN = D6;
const int CS_PIN  = D7;

const int MODULES = 4;
// If the physical order is reversed, you can change this to {3,2,1,0}
// but logically: index 0 = leftmost, index 3 = rightmost.
uint8_t MODULE_ORDER[MODULES] = {0, 1, 2, 3};

LedControl mx = LedControl(DIN_PIN, CLK_PIN, CS_PIN, MODULES);

// ---------- DIGIT FONT (5×7) ----------
const uint8_t DIGITS[10][5] = {
  {0x3E,0x51,0x49,0x45,0x3E}, // 0
  {0x00,0x42,0x7F,0x40,0x00}, // 1
  {0x42,0x61,0x51,0x49,0x46}, // 2
  {0x21,0x41,0x45,0x4B,0x31}, // 3
  {0x18,0x14,0x12,0x7F,0x10}, // 4
  {0x27,0x45,0x45,0x45,0x39}, // 5
  {0x3C,0x4A,0x49,0x49,0x30}, // 6
  {0x01,0x71,0x09,0x05,0x03}, // 7
  {0x36,0x49,0x49,0x49,0x36}, // 8
  {0x06,0x49,0x49,0x29,0x1E}  // 9
};

// ---------- YOUR ARROWS ----------
const uint8_t ARROW_RIGHT[8] = {
  0b00000000,
  0b00000000,
  0b00000100,
  0b00000010,
  0b00111111,
  0b00000010,
  0b00000100,
  0b00000000
};

const uint8_t ARROW_UP[8] = {
  0b00010000,
  0b00111000,
  0b00010000,
  0b00010000,
  0b00010000,
  0b00010000,
  0b00010000,
  0b10010000
};

const uint8_t ARROW_UP_SLOW[8] = {
  0b00000111,
  0b00000011,
  0b00000101,
  0b00001000,
  0b00010000,
  0b00100000,
  0b01000000,
  0b10000000
};

const uint8_t ARROW_DOWN[8] = {
  0b00010000,
  0b00010000,
  0b00010000,
  0b00010000,
  0b00010000,
  0b00010000,
  0b00111000,
  0b10010000
};

const uint8_t ARROW_DOWN_SLOW[8] = {
  0b10000000,
  0b01000000,
  0b00100000,
  0b00010000,
  0b00001000,
  0b00000101,
  0b00000011,
  0b10000111
};

// ---------- HELPERS ----------
void clearModule(int m) {
  for (int r = 0; r < 8; r++) {
    mx.setRow(MODULE_ORDER[m], r, 0x00);
  }
}

void draw8x8OnModule(const uint8_t* bmp, int module) {
  for (int r = 0; r < 8; r++) {
    mx.setRow(MODULE_ORDER[module], r, bmp[r]);
  }
}

void drawDigitOnModule(int digit, int module) {
  clearModule(module);
  if (digit < 0 || digit > 9) return;

  for (int row = 0; row < 8; row++) {
    uint8_t rowBits = 0;

    if (row < 7) {
      for (int col = 0; col < 5; col++) {
        if ((DIGITS[digit][col] >> row) & 1) {
          int x = col + 1;           // center inside 8 columns (1..5)
          rowBits |= (1 << (7 - x)); // MAX7219 bit order: bit7=col0 ... bit0=col7
        }
      }
    }

    mx.setRow(MODULE_ORDER[module], row, rowBits);
  }
}

// ---------- DIGIT LAYOUT ----------
// Module 0 = units, Module 1 = tens, Module 2 = hundreds, Module 3 = arrow
void drawGlucoseValue(int glucose) {
  if (glucose < 0)   glucose = 0;
  if (glucose > 999) glucose = 999;

  int ones     = glucose % 10;
  int tens     = (glucose / 10) % 10;
  int hundreds = (glucose / 100) % 10;

  // Clear only digit modules (0,1,2) – leave arrow (3) as is
  clearModule(0);
  clearModule(1);
  clearModule(2);

  // Always draw units on module 0
  drawDigitOnModule(ones, 0);

  // Draw tens only if >= 10
  if (glucose >= 10) {
    drawDigitOnModule(tens, 1);
  }

  // Draw hundreds only if >= 100
  if (glucose >= 100) {
    drawDigitOnModule(hundreds, 2);
  }

  // Debug print
  Serial.print("Glucose: ");
  Serial.print(glucose);
  Serial.print("  ->  [U:");
  Serial.print(ones);
  Serial.print(" T:");
  Serial.print(tens);
  Serial.print(" H:");
  Serial.print(hundreds);
  Serial.println("]");
}

// ---------- TREND ARROW ON MODULE 3 ----------
void showTrendArrow(String trend) {
  trend.toLowerCase();

  const uint8_t* art = ARROW_RIGHT;  // default: flat

  bool risingSlight  = trend.indexOf("rising slightly")  >= 0 ||
                       trend.indexOf("slightly rising")  >= 0;

  bool fallingSlight = trend.indexOf("falling slightly") >= 0 ||
                       trend.indexOf("slightly falling") >= 0;

  bool flat  = trend.indexOf("steady") >= 0 || trend.indexOf("flat") >= 0;
  bool up    = trend.indexOf("rise")   >= 0 || trend.indexOf("up")   >= 0;
  bool down  = trend.indexOf("fall")   >= 0 || trend.indexOf("down") >= 0;

  if (flat) {
    art = ARROW_RIGHT;
  }
  else if (risingSlight) {
    art = ARROW_UP_SLOW;
  }
  else if (fallingSlight) {
    art = ARROW_DOWN_SLOW;
  }
  else if (up) {
    art = ARROW_UP;
  }
  else if (down) {
    art = ARROW_DOWN;
  }

  draw8x8OnModule(art, 3);   // arrow on rightmost module
}

// ---------- API FETCH ----------
bool fetchGlucoseAndTrend(int& glucoseOut, String& trendOut) {
  String resp;

  WiFiClientSecure client;
  client.setInsecure();
  if (!client.connect(API_HOST, API_PORT)) return false;

  client.print(String("GET ") + API_PATH +
               " HTTP/1.1\r\nHost: " + API_HOST + "\r\nConnection: close\r\n\r\n");

  while (client.connected() || client.available()) {
    if (client.available()) {
      resp += (char)client.read();
    }
  }

  int s = resp.indexOf('{');
  int e = resp.lastIndexOf('}');
  if (s < 0 || e < 0) return false;

  String json = resp.substring(s, e+1);

  // Glucose
  int gKey = json.indexOf("Glucose");
  if (gKey < 0) return false;

  int gColon = json.indexOf(':', gKey);
  int i = gColon + 1;
  while (json[i] == ' ' || json[i] == '\"') i++;

  String gnum = "";
  while (isdigit(json[i])) gnum += json[i++];
  glucoseOut = gnum.toInt();

  // Trend
  int tKey = json.indexOf("Trend");
  int tq1  = json.indexOf('\"', json.indexOf(':', tKey) + 1);
  int tq2  = json.indexOf('\"', tq1 + 1);
  trendOut = json.substring(tq1 + 1, tq2);

  return true;
}

// ---------- MAIN ----------
unsigned long lastUpdate = 0;
const unsigned long UPDATE_MS = 10000;

void setup() {
  Serial.begin(115200);
  delay(50);

  for (int m = 0; m < MODULES; m++) {
    mx.shutdown(MODULE_ORDER[m], false);
    mx.setIntensity(MODULE_ORDER[m], 10);
    mx.clearDisplay(MODULE_ORDER[m]);
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // Boot: arrow on module 3 + "0" on module 0
  draw8x8OnModule(ARROW_RIGHT, 3);
  drawGlucoseValue(0);
}

void loop() {
  if (millis() - lastUpdate < UPDATE_MS) return;
  lastUpdate = millis();

  int glucose = 0;
  String trend = "steady";

  if (fetchGlucoseAndTrend(glucose, trend)) {
    drawGlucoseValue(glucose);
    showTrendArrow(trend);
  } else {
    drawGlucoseValue(888);
    showTrendArrow("steady");
  }
}
