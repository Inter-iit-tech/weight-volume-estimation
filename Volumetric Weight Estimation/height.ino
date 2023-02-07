#include <Wire.h>
#include <LCD_I2C.h>
#define IR_PIN A7

LCD_I2C lcd(0x27);
double groundHeight = 0;

double getSensorReading(int n){
  int curr = 0;
  double avg = 0;
  while(curr < n){
    avg = (avg*curr) + analogRead(IR_PIN);
    curr++;
    avg /= curr;
  }
  return 26737*pow(avg, -1.241);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin( 9600 ); //Enable the serial comunication
  Wire.begin();
  lcd.begin();
  lcd.backlight();
  lcd.print("Calibrating...");
  groundHeight = getSensorReading(1000);
  lcd.clear();
  lcd.print("Ground Height: ");
  lcd.setCursor(0,1);
  lcd.print(groundHeight);
  delay(3000);
  lcd.clear();
}

void loop() {
  double reading = getSensorReading(1000);
  int height = (groundHeight - reading)*10;
  Serial.println(height); //Print the value to the serial monitor
  lcd.print("Height: ");
  lcd.setCursor(0,1);
  lcd.print("                ");
  lcd.setCursor(0,1);
  lcd.print(height/10.0);
  delay(500);

}
