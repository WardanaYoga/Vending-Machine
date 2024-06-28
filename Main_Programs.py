import RPi.GPIO as io
import time 

io.setwarnings(False)

sensorIR_1 = 14
sensorIR_2 = 15
sensorIR_3 = 18

io.setmode(io.BCM)
io.setup(sensorIR_1, io.IN)
io.setup(sensorIR_2, io.IN)
io.setup(sensorIR_3, io.IN)

try :
    while True:
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



