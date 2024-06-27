Instalasi Library:
sudo apt-get update
sudo apt-get install python3-rpi.gpio

Inisialisasi GPIO dan PWM:
GPIO.setmode(GPIO.BCM) mengatur mode penomoran pin ke BCM.
Pin GPIO 17 dan 27 diatur sebagai output untuk mengendalikan dua servo.
GPIO.PWM(servoPIN1, 50) dan GPIO.PWM(servoPIN2, 50) mengatur PWM dengan frekuensi 50Hz untuk masing-masing servo.
pwm1.start(0) dan pwm2.start(0) memulai PWM dengan duty cycle 0.
Fungsi set_servo_angle(pwm, angle):

Fungsi ini menghitung duty cycle yang sesuai untuk sudut servo yang diinginkan dan mengubah duty cycle PWM.
Duty cycle dihitung dengan rumus duty = 2 + (angle / 18).
pwm.ChangeDutyCycle(duty) mengubah duty cycle ke nilai yang dihitung.
Loop Utama:

Servo digerakkan dari 0 hingga 180 derajat dalam langkah 10 derajat.
Setelah mencapai 180 derajat, servo digerakkan kembali ke 0 derajat dalam langkah 10 derajat.
time.sleep(0.5) memberikan waktu jeda agar servo dapat bergerak ke posisi yang diinginkan.
Exception Handling:

except KeyboardInterrupt digunakan untuk menangani penghentian program dengan Ctrl+C.
finally memastikan bahwa PWM dihentikan dan GPIO dibersihkan saat program dihentikan.


Operating voltage: 4.8 V a 7.2 V