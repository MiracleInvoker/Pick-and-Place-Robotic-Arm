import cv2 as cv
import numpy as np
import serial
import math


# Configuration
SERIAL_PORT = 'COM5'
BAUD_RATE = 9600
CAMERA_INDEX = 1

# HSV Color Range for a Pink Object
RED_LOWER = np.array([140, 50,  50])
RED_UPPER = np.array([170, 255, 255])

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout = 1)
print("Arduino Connected.")

cap = cv.VideoCapture(CAMERA_INDEX)
frame_height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
frame_width = cap.get(cv.CAP_PROP_FRAME_WIDTH)

base_x = 60
base_y = int(frame_height / 2)

# Kernel used for Morphological Opening...
ke7 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (7, 7))


while True:
    ret, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    cv.imshow('Frame (hsv)', hsv)

    mask = cv.inRange(hsv, RED_LOWER, RED_UPPER)
    cv.imshow('Frame (hsv -> mask)', mask)

    opened = cv.morphologyEx(mask, cv.MORPH_OPEN, ke7, iterations = 3)
    cv.imshow('Frame (hsv -> mask -> open)', opened)

    contours, _ = cv.findContours(opened.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        c = max(contours, key = cv.contourArea)
        ((x, y), radius) = cv.minEnclosingCircle(c)
        
        if radius > 10:
            target_x, target_y = int(x), int(y)
            cv.circle(frame, (target_x, target_y), int(radius), (0, 255, 255), 2)
            cv.circle(frame, (target_x, target_y), 5, (0, 0, 255), -1)
            
            cv.line(frame, (base_x, base_y), (target_x, target_y), (0, 255, 0), 2)

            delta_x = target_x - base_x
            delta_y = target_y - base_y
            
            angle_rad = math.atan2(delta_y, delta_x)
            angle_deg = math.degrees(angle_rad)
            servo_angle = int(90 - angle_deg)

            command = f'{servo_angle}\n'
            arduino.write(command.encode())
            print(f'Servo Angle: {servo_angle}')

    cv.circle(frame, (base_x, base_y), 10, (0, 255, 0), -1)
    cv.imshow('Frame', frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv.destroyAllWindows()
arduino.close()
print("Resources Released.")