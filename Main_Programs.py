import RPi.GPIO as io
import time 
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

io.setwarnings(False)
io.setmode (io.BCM)

#konfigurasi I2C dan PWM Driver
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

#konfigurasi Servo
servo3 = servo.Servo(pca.channels[0])
servo4 = servo.Servo(pca.channels[1])
servo5 = servo.Servo(pca.channels[2])
servo6 = servo.Servo(pca.channels[3])

#konfigurasi Pembacaan Sensor Proxymity IR
sensorIR_1 = 14
sensorIR_2 = 15
sensorIR_3 = 18
io.setup(sensorIR_1, io.IN)
io.setup(sensorIR_2, io.IN)
io.setup(sensorIR_3, io.IN)

pushbutton = 23
io.setup(pushbutton, io.IN, pull_up_down = io.PUD_UP)

#konfigurasi Pembacaan Servo 1 dan 2
servo_pin = 12
servo2_pin = 13
io.setup(servo_pin, io.OUT)
io.setup(servo2_pin, io.OUT)


pwm = io.PWM(servo_pin, 50)
pwm.start(0)

def set_sudut_servo(servo, sudut):
    servo.angle = sudut
    
def set_servo_angle(angle):
    duty = angle / 18 + 2
    io.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    io.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)
    
def deteksi_sensor():
    sensor_value_1 = io.input(sensorIR_1)
    sensor_value_2 = io.input(sensorIR_2)
    sensor_value_3 = io.input(sensorIR_3) 
        
    if sensor_value_1 == io.LOW and sensor_value_2 == io.LOW and sensor_value_3 == io.LOW:
        print("Terbaca Tiga Sensor")
        time.sleep(3)
    elif sensor_value_1 == io.LOW and sensor_value_2 == io.LOW and sensor_value_3 == io.HIGH:
        print("Terbaca Dua Sensor")
        time.sleep(3)
    elif sensor_value_1 == io.LOW and sensor_value_2 == io.HIGH and sensor_value_3 == io.HIGH:
        print("Terbaca Satu Sensor")
        time.sleep(3)
    else:
        print("Objek Tidak Terdeteksi")
        time.sleep(1)

def servo_1():
    pushbutton_value = io.input(pushbutton)
    if pushbutton_value == io.HIGH:
        print("Memutar Servo ke 180 derajat")
        set_servo_angle(180)
        print("Masukkan Botol!")
        print("========")
        time.sleep(7)
        
        print("Memutar Servo ke 0 Derjat")
        set_servo_angle(0)
        print("========")
        time.sleep(3)
            
    else:
        print("Servo Pada Posisi 0 Derajat")
        print("==============")
        set_servo_angle(0)
        time.sleep(0.5)
    
def servo_2():
    if deteksi_sensor == True:
        print("Botol telah terdeteksi sensor")
        set_servo_angle(180)
    else:
        print("Belum terdeteksi Sensor")
        set_servo_angle(0)

try :
    while True:
        servo_1()
        deteksi_sensor()
        servo_2()
        

        
except KeyboardInterrupt:
    print("Program dihentikan")
finally:
    io.cleanup()




