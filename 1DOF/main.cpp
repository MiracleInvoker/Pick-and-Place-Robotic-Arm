#include <Arduino.h>
#include <Servo.h>


Servo myServo;

const int SERVO_PIN = 9;
const int HOME_POSITION = 0;


void setup() {
	Serial.begin(9600);
	myServo.attach(SERVO_PIN);
	myServo.write(HOME_POSITION);
}

void loop() {
	if (Serial.available() > 0) {
    	int angle = Serial.parseInt();
    	myServo.write(angle);
	}
}