#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "RobotControl";
const char* password = "12345678";

WebServer server(80);

const int ENA = 5;
const int IN1 = 18;
const int IN2 = 19;

const int ENB = 21;
const int IN3 = 22;
const int IN4 = 23;

const int LED_PIN = 2;

const int pwmFreq = 5000;   
const int pwmResolution = 8;

// Fixed speeds — right always full power, left always 80% of full power.
// No kick, no ramp, no decay — constant force the whole time.
const int RIGHT_SPEED = 255;
const int LEFT_SPEED  = 168; // 80% of 255

char currentCmd = 'x';

void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  ledcAttach(ENA, pwmFreq, pwmResolution);
  ledcAttach(ENB, pwmFreq, pwmResolution);

  stopMotors();

  WiFi.softAP(ssid, password);
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/cmd", handleCmd);
  server.begin();
}

void loop() {
  server.handleClient();
}

void handleRoot() {
  String html = R"(
    <html><body style="text-align:center;font-family:sans-serif">
    <h2>WASD to drive</h2>
    <p>Click here first, then use W A S D keys</p>
    <script>
    document.addEventListener('keydown', function(e) {
      if (e.repeat) return;
      let k = e.key.toLowerCase();
      if (['w','a','s','d'].includes(k)) fetch('/cmd?k=' + k);
    });
    document.addEventListener('keyup', function(e) {
      let k = e.key.toLowerCase();
      if (['w','a','s','d'].includes(k)) fetch('/cmd?k=x');
    });
    window.addEventListener('blur', function() {
      fetch('/cmd?k=x');
    });
    </script>
    </body></html>
  )";
  server.send(200, "text/html", html);
}

void handleCmd() {
  String k = server.arg("k");
  if (k.length() == 0) { server.send(200, "text/plain", "ok"); return; }
  char c = k[0];

  if (c != currentCmd) {
    currentCmd = c;
    Serial.print("Command: ");
    Serial.println(c);
    digitalWrite(LED_PIN, HIGH);
    applyCommand(c);
    digitalWrite(LED_PIN, LOW);
  }

  server.send(200, "text/plain", "ok");
}

void applyCommand(char c) {
  if (c == 'w') {
    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
    ledcWrite(ENA, LEFT_SPEED);
    ledcWrite(ENB, RIGHT_SPEED);
  } else if (c == 's') {
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
    ledcWrite(ENA, LEFT_SPEED);
    ledcWrite(ENB, RIGHT_SPEED);
  } else if (c == 'a') {
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
    ledcWrite(ENA, LEFT_SPEED);
    ledcWrite(ENB, RIGHT_SPEED);
  } else if (c == 'd') {
    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
    ledcWrite(ENA, LEFT_SPEED);
    ledcWrite(ENB, RIGHT_SPEED);
  } else if (c == 'x') {
    stopMotors();
  }
}

void stopMotors() {
  ledcWrite(ENA, 0);
  ledcWrite(ENB, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}
