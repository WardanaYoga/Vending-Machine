import RPi.GPIO as io
import time 

sensorpin = 23

io.setmode(io.BCM)
io.setup(sensorpin, io.IN)

try :
    while True:
        sensor_value = io.input(sensorpin)
        if  sensor_value == io.LOW : 
            print("Objek Terdeteksi")
        else :
            print("Tidak ada objek")
        
        time.sleep(1)
except KeyboardInterrupt:
    print("Program dihentikan")
finally:
    io.cleanup()
