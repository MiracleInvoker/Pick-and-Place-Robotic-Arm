#include <Arduino.h>
#include <Servo.h>
#include <Stepper.h>

const int servoPin = 6;
const int stepsPerRevolution = 2048;
const int rpm = 8;

Stepper myStepper(stepsPerRevolution, 8, 10, 9, 11);
Servo myServo;


void setup(){
	Serial.begin(9600);
	myServo.attach(servoPin);
	myServo.write(servoAngle);
	myStepper.setSpeed(rpm);
}

void loop() {
	if (Serial.available()) {

		String line = Serial.readStringUntil('\n');
		line.trim();
		int commaIdx = line.indexOf(',');
		int steps = line.substring(0, commaIdx).toInt();
		int ang = line.substring(commaIdx + 1).toInt();

		myStepper.step(steps);
		myServo.write(ang);
	}
}