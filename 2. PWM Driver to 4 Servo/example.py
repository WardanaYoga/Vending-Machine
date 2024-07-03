import RPi.GPIO as GPIO
import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# Hentikan peringatan dan atur mode GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Konfigurasi I2C dan PWM Driver
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

# Konfigurasi Servo
servo3 = servo.Servo(pca.channels[0])
servo4 = servo.Servo(pca.channels[1])
servo5 = servo.Servo(pca.channels[2])
servo6 = servo.Servo(pca.channels[3])

# Fungsi untuk menggerakkan servo
def gerak_servo(servo_obj, sudut):
    servo_obj.angle = sudut
    time.sleep(1)

try:
    while True:
        print("Menggerakkan servo ke 180 derajat")
        gerak_servo(servo3, 180)
        
        print("Menggerakkan servo ke 0 derajat")
        gerak_servo(servo3, 0)

except KeyboardInterrupt:
    print("Program dihentikan")
finally:
    # Bersihkan GPIO
    GPIO.cleanup()
