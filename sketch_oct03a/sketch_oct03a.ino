#define LED_PIN 13
#define UP_PIN 3
#define DOWN_PIN 2
#define CLICK_DURATION 70
#define CLOCK_DURATION 400
#define X1 0x30
#define X2 0x78
#define CH_COUNT 16
#define CH_COUNT_DIV2 CH_COUNT >> 1

int CH = 0;

void Click_chanel(int NEW_CH) {
  byte WORK_PIN = 0;
  int Step_Count = 0;

  if (NEW_CH > CH) {
    Step_Count = NEW_CH - CH;
    if (Step_Count < CH_COUNT_DIV2) {WORK_PIN = UP_PIN;} else {WORK_PIN = DOWN_PIN; Step_Count = CH_COUNT - Step_Count;};
  } else {
    Step_Count = CH - NEW_CH;
    if (Step_Count < CH_COUNT_DIV2) {WORK_PIN = DOWN_PIN;} else {WORK_PIN = UP_PIN; Step_Count = CH_COUNT - Step_Count;};
  };

  for (int i = 0; i < Step_Count; i++)  {
    digitalWrite(LED_PIN, HIGH);
    pinMode(WORK_PIN, OUTPUT);    
    delay(CLICK_DURATION);
    pinMode(WORK_PIN, INPUT);    
    digitalWrite(LED_PIN, LOW);
    delay(CLOCK_DURATION);
  }
}

void setup() {
  Serial.begin(57600);
  Serial.println("VideoRecorderSwitcher - Ok");
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  pinMode(UP_PIN, INPUT);
  digitalWrite(UP_PIN, LOW);
  pinMode(DOWN_PIN, INPUT);
  digitalWrite(DOWN_PIN, LOW);
  Click_chanel(CH);
  Serial.flush();
}

void loop() {
  int x1, x2, x3, x4; 
  if (Serial.available() == 4)
  {
      x1 = Serial.read();
      x2 = Serial.read();
      x3 = Serial.read();
      x4 = Serial.read();
      //Serial.println(x1, HEX);
      //Serial.println(x2, HEX);
      //Serial.println(x3, DEC);
      //Serial.println(x4, DEC);
      //Serial.println(" Ok");
      if ((x1 == X1)&&(x2 == X2))
        {
          //Serial.println(x3 - 48, DEC);
          //Serial.println(x4 - 48, DEC);
          int NEW_CH = (x3 - 48)*10 + (x4 - 48);
          //Serial.println(NEW_CH, DEC);
          if ((NEW_CH != CH)&&(NEW_CH < CH_COUNT))
            {
              Serial.println("Ok");
              Click_chanel(NEW_CH);
              CH = NEW_CH;
              Serial.println(CH, DEC);   
           } else Serial.println("Error");
           
        }
      //    
      //    if ((NEW_CH != CH)&&(NEW_CH < CH_COUNT)) 
      //      {
      //        Serial.println("Ok");
      //        Click_chanel(NEW_CH);
      //        CH = NEW_CH;
      //        Serial.write(CH);
      //      } else Serial.println("Error");
      //  }
    }
    Serial.flush();
}
