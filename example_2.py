import time
from adafruit_servokit import ServoKit

# Inisialisasi PCA9685 dengan jumlah channel 16 (sesuai modul PCA9685)
kit = ServoKit(channels=16)

# Atur sudut awal servo (0 derajat)
kit.servo[0].angle = 0
kit.servo[1].angle = 0
kit.servo[2].angle = 0
kit.servo[3].angle = 0

try:
    while True:
        # Gerakkan servo 0 dari 0 hingga 180 derajat
        for angle in range(0, 181, 1):
            kit.servo[0].angle = angle
            time.sleep(0.01)
        # Gerakkan servo 0 dari 180 hingga 0 derajat
        for angle in range(180, -1, -1):
            kit.servo[0].angle = angle
            time.sleep(0.01)

        # Gerakkan servo 1 dari 0 hingga 180 derajat
        for angle in range(0, 181, 1):
            kit.servo[1].angle = angle
            time.sleep(0.01)
        # Gerakkan servo 1 dari 180 hingga 0 derajat
        for angle in range(180, -1, -1):
            kit.servo[1].angle = angle
            time.sleep(0.01)

        # Gerakkan servo 2 dari 0 hingga 180 derajat
        for angle in range(0, 181, 1):
            kit.servo[2].angle = angle
            time.sleep(0.01)
        # Gerakkan servo 2 dari 180 hingga 0 derajat
        for angle in range(180, -1, -1):
            kit.servo[2].angle = angle
            time.sleep(0.01)

        # Gerakkan servo 3 dari 0 hingga 180 derajat
        for angle in range(0, 181, 1):
            kit.servo[3].angle = angle
            time.sleep(0.01)
        # Gerakkan servo 3 dari 180 hingga 0 derajat
        for angle in range(180, -1, -1):
            kit.servo[3].angle = angle
            time.sleep(0.01)

except KeyboardInterrupt:
    print("Program dihentikan")

finally:
    # Atur sudut servo ke posisi awal (0 derajat) saat program dihentikan
    kit.servo[0].angle = 0
    kit.servo[1].angle = 0
    kit.servo[2].angle = 0
    kit.servo[3].angle = 0
    print("Servo kembali ke posisi awal")

