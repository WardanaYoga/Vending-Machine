from gpiozero import AngularServo
from time import sleep

# Konfigurasi servo dengan pin GPIO 18
servo = AngularServo(18, min_angle=0, max_angle=180)

try:
    while True:
        servo.angle = 0    # Set servo ke 0 derajat
        sleep(2)
        servo.angle = 90   # Set servo ke 90 derajat
        sleep(2)
        servo.angle = 180  # Set servo ke 180 derajat
        sleep(2)
except KeyboardInterrupt:
    pass
