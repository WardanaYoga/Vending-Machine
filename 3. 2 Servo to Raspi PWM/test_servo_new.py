import RPi.GPIO as GPIO
import time

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Definisikan pin servo
servo_pin = 12

# Atur pin servo sebagai output
GPIO.setup(servo_pin, GPIO.OUT)

# Buat instance PWM di pin servo dengan frekuensi 50Hz
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        print("Memutar Servo ke 0 derajat")
        set_servo_angle(0)
        time.sleep(2)
         
        print("Memutar Servo ke 90 Derjat")
        set_servo_angle(90)
        time.sleep(2)
        
        print("Memutar Servo ke 180 Derajat")
        set_servo_angle(180)
        
except KeyboardInterrupt:
    print("Program Dihentikan")
finally:
    pwm.stop()
    GPIO.cleanup()


