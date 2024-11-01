void setup() {
  for (int i = 0; i < 48; i++) {
    pinMode(i+6, INPUT_PULLUP);
  }
  Serial.begin(9600);
}

void loop() {
  String toSend = "";

  for (int i = 6; i < 54; i++) {
    int pinState = digitalRead(i);
    if (pinState == LOW) {
      toSend += "1";
    } else {
      toSend += "0";
    }
  }

  Serial.println(toSend);
  delay(10);
}
