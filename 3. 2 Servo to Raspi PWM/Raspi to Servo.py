import RPi.GPIO as GPIO
import time

# Atur GPIO mode ke BCM
GPIO.setmode(GPIO.BCM)

# Definisikan pin GPIO yang terhubung ke servo
servoPIN1 = 12
servoPIN2 = 13

# Atur pin GPIO sebagai output
GPIO.setup(servoPIN1, GPIO.OUT)
GPIO.setup(servoPIN2, GPIO.OUT)

# Atur frekuensi PWM untuk servo (biasanya 50Hz)
pwm1 = GPIO.PWM(servoPIN1, 50)
pwm2 = GPIO.PWM(servoPIN2, 50)

# Mulai PWM dengan duty cycle 0 (servo di posisi 0 derajat)
pwm1.start(0)
pwm2.start(0)

def set_servo_angle(pwm, angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        # Gerakkan kedua servo dari 0 hingga 180 derajat
        for angle in range(0, 181, 10):
            set_servo_angle(pwm1, angle)
            set_servo_angle(pwm2, angle)
            time.sleep(0.5)
        
        # Gerakkan kedua servo dari 180 hingga 0 derajat
        for angle in range(180, -1, -10):
            set_servo_angle(pwm1, angle)
            set_servo_angle(pwm2, angle)
            time.sleep(0.5)

except KeyboardInterrupt:
    print("Program dihentikan")

finally:
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
