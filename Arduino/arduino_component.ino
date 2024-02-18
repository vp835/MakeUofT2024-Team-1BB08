#include <Servo.h>

Servo motor; // Define motor object

void setup() {
  motor.attach(9); // Attach motor to pin 9
  motor.write(0); // Set initial position
  Serial.begin(9600); // Initialize serial communication
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read incoming command
    if (command == '1') {
      // Rotate motor clockwise to 90 degrees
      motor.write(60);
      delay(5000); // Delay for motor movement
      motor.write(0); // Stop the motor
    } else if (command == '2') {
      // Rotate motor counterclockwise to 90 degrees
      motor.write(120);
      delay(5000); // Delay for motor movement
      motor.write(0); // Stop the motor
    }
  }
}
