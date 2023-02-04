#include <HX711_ADC.h>
#include <Wire.h>
#include <LCD_I2C.h>

HX711_ADC LoadCell(5, 4);
LCD_I2C lcd(0x27);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  LoadCell.begin(); // start connection to HX711
  LoadCell.start(2000); // load cells gets 2000ms of time to stabilize
  LoadCell.setCalFactor(20); // calibration factor for load cell => dependent on your individual setup
//  pinMode(8, OUTPUT);
//  digitalWrite(8, HIGH);
  Wire.begin();
  lcd.begin();
  lcd.backlight();
  lcd.print("Weight: ");
}

void loop() {
  // put your main code here, to run repeatedly:
  LoadCell.update(); // retrieves data from the load cell
  float i = LoadCell.getData(); // get output value
  Serial.println(i);
  delay(300);
  lcd.setCursor(0,1);
  lcd.print(i);
}
