import RPi.GPIO as io
import time 

io.setwarnings(False)
io.setmode (io.BCM)

sensorIR_1 = 14
sensorIR_2 = 15
sensorIR_3 = 18
pushbutton = 23
servo_pin = 12

io.setmode(io.BCM)
io.setup(sensorIR_1, io.IN)
io.setup(sensorIR_2, io.IN)
io.setup(sensorIR_3, io.IN)
io.setup(pushbutton, io.IN, pull_up_down = io.PUD_UP)
io.setup(servo_pin, io.OUT)

pwm = io.PWM(servo_pin, 50)
pwm.start(0)

def set_servo_angle(angle):
    duty = angle / 18 + 2
    io.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    io.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)


try :
    while True:
        pushbutton_value = io.input(pushbutton)
        
        if pushbutton_value == io.HIGH:
            print("Memutar Servo ke 180 derajat")
            set_servo_angle(180)
            print("========")
            time.sleep(7)
         
            print("Memutar Servo ke 0 Derjat")
            set_servo_angle(0)
            print("========")
            time.sleep(2)
            
        else:
            print("Servo Pada Posisi 0 Derajat")
            print("==============")
            set_servo_angle(0)
            time.sleep(0.5)
            
        sensor_value_1 = io.input(sensorIR_1)
        sensor_value_2 = io.input(sensorIR_2)
        sensor_value_3 = io.input(sensorIR_3) 
        
        if  sensor_value_1 == io.LOW and sensor_value_2 == io.LOW and sensor_value_3 == io.LOW:
            print("Terbaca Tiga Sensor")
        elif sensor_value_1 == io.LOW and sensor_value_2 == io.LOW and sensor_value_3 == io.HIGH:
            print("Terbaca Dua Sensor")
        elif sensor_value_1 == io.LOW and sensor_value_2 == io.HIGH and sensor_value_3 == io.HIGH:
            print("Terbaca Satu Sensor")
        else :
            print("Objek Tidak Terdeteksi")
            time.sleep(1)
        
        
except KeyboardInterrupt:
    print("Program dihentikan")
finally:
    io.cleanup()
