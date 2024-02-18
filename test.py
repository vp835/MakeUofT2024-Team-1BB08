import cv2
import mediapipe as mp
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time
import serial

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize hand detector and classifier
detector = HandDetector(maxHands=1)
classifier = Classifier("Model\\keras_model.h5", "Model\\labels.txt")

# Initialize serial communication with Arduino
arduino_port = 'COM4'  # Update with the correct port name
arduino_baudrate = 9600
arduino = serial.Serial(arduino_port, arduino_baudrate)
time.sleep(2)  # Allow time for Arduino to initialize

labels = ["1", "2", "3"]

# Set the correct password
correct_password = "11111"

# String to store the password
password = ""

# Flag to indicate if the password is correct
password_correct = False

# Delay (in seconds) between appending each digit
delay = 2  # Adjust this value as needed

# Time at which the last digit was appended
last_digit_time = time.time()

# Main loop for hand gesture recognition
while True:
    success, img = cap.read()
    if not success:
        continue

    # Find hands in the frame
    hands, img = detector.findHands(img)

    # If hands are found, classify hand gesture
    if hands and len(password) < 5:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        # Crop and resize hand region
        imgWhite = np.ones((300, 300, 3), np.uint8) * 255
        imgCrop = img[y - 20:y + h + 20, x - 20:x + w + 20]

        aspectRatio = h / w
        if aspectRatio > 1:
            k = 300 / h
            wCal = math.ceil(k * w)
            imgResize = cv2.resize(imgCrop, (wCal, 300))
            wGap = math.ceil((300 - wCal) / 2)
            imgWhite[:, wGap:wCal + wGap] = imgResize
            prediction, index = classifier.getPrediction(imgWhite)
        else:
            k = 300 / w
            hCal = math.ceil(k * h)
            imgResize = cv2.resize(imgCrop, (300, hCal))
            hGap = math.ceil((300 - hCal) / 2)
            imgWhite[hGap:hCal + hGap:, :] = imgResize
            prediction, index = classifier.getPrediction(imgWhite)

        # Append predicted number to password string
        if labels[index].isdigit():
            # Check if enough time has passed since last digit appended
            if time.time() - last_digit_time >= delay:
                password += labels[index]
                last_digit_time = time.time()

        # Display hand gesture and password string
        cv2.putText(img, f"Gesture: {labels[index]}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1,
                    cv2.LINE_AA)
        cv2.putText(img, f"Password: {password}", (10, 65), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1,
                    cv2.LINE_AA)

        # Check if the password is correct
        if len(password) >= 5:
            if password == correct_password:
                password_correct = True
                cv2.putText(img, "Passcode Correct!", (10, 100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1,
                            cv2.LINE_AA)
                print("Password Correct!")
            else:
                cv2.putText(img, "Passcode Incorrect!", (10, 100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1,
                            cv2.LINE_AA)
                print("Password Incorrect!")

    # Send commands to Arduino based on password correctness
    if password_correct:
        arduino.write(b'1')  # Turn motor clockwise
    else:
        arduino.write(b'0')  # Turn motor off

    # Display frame
    cv2.imshow('Image', img)
    key = cv2.waitKey(1)

    # Exit loop if 'q' is pressed
    if key == ord('q'):
        break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()
