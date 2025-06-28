import cv2 as cv
import math
import serial


# Configuration
SERIAL_PORT = 'COM5'
BAUD_RATE = 9600
CAMERA_INDEX = 1
arm_length = 110

cap = cv.VideoCapture(CAMERA_INDEX)
frame_height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
frame_width = cap.get(cv.CAP_PROP_FRAME_WIDTH)

base_x = int(frame_width / 2)
base_y = int(frame_height)

tx = None
ty = None

stepperAngle = 0

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout = 1)
print("Arduino Connected.")
arduino.write(f'0,0\n'.encode())


def click_event(event, x, y, flags, params):
    global tx, ty
    if event == cv.EVENT_LBUTTONDOWN:
        tx, ty = x, y


while True:
    ret, frame = cap.read()

    if (tx is not None and ty is not None):

        cv.circle(frame, (tx, ty), 10, (0, 0, 255), 1)

        # Coordinate Transformation with Respect to Base
        dx = tx - base_x
        dy = base_y - ty

        r = math.hypot(dx, dy)

        if (r <= 2 * arm_length):

            # 2D Inverse Kinematics
            theta2 = math.acos((r / arm_length) ** 2 * (1 / 2) - 1)
            theta1 = math.atan2(dy, dx) - math.atan2(math.sin(theta2), 1 + math.cos(theta2))

            x1 = int(base_x + math.cos(theta1) * arm_length)
            y1 = int(base_y - math.sin(theta1) * arm_length)
            x2 = int(x1 + math.cos(theta1 + theta2) * arm_length)
            y2 = int(y1 - math.sin(theta1 + theta2) * arm_length)

            cv.line(frame, (base_x, base_y), (x1, y1), (0, 255, 0), 2)
            cv.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            theta1 = int(math.degrees(theta1))
            theta2 = int(math.degrees(theta2))

            del_theta1 = (theta1 - stepperAngle + 180) % 360 - 180
            stepperAngle = theta1

            if (del_theta1):
                steps = -1 * int(del_theta1 * 256 / 45)
                command = f'{steps},{theta2}\n'
                arduino.write(command.encode())

                print(f'x: {tx}, y: {ty} | ang1 = {theta1}, ang2 = {theta2}')

    cv.circle(frame, (base_x, base_y), 10, (0, 255, 0), 1)
    cv.imshow('Frame', frame)
    cv.setMouseCallback('Frame', click_event)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv.destroyAllWindows()
arduino.close()
print("Resources Released.")