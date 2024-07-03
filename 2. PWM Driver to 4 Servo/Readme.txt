Instalasi Library:
sudo apt-get update
sudo apt-get install python3-pip
pip3 install adafruit-circuitpython-pca9685
pip3 install adafruit-circuitpython-servokit

Jika terdapat error pada I2C yang diinformasikan oleh Compiler 
maka solusinya
1. masukan libary import busio
2. masukan libary import board
3. cek apakah terdapat adafruit blinka dengan cara ketikan pip3 install adafruit-blinka
4. setelah itu ketikan pip3 install adafruit-circuitpython-pca9685 adafruit-circuitpython-motor
Penjelasan Inisialisasi I2C: Menggunakan busio.I2C dengan board.SCL dan board.SDA untuk mendefinisikan bus I2C.
Berdasarkan hasil yang Anda peroleh, sepertinya modul board yang Anda miliki tidak memiliki atribut SCL dan SDA. Ini mungkin terjadi karena pustaka board yang diinstal tidak sesuai dengan yang seharusnya digunakan untuk Raspberry Pi. Pustaka yang benar untuk ini adalah adafruit_blinka, yang menyediakan kompatibilitas dengan CircuitPython.
maka jalankan kode diatas jika terdapat error pada i2c

ServoKit diinisialisasi dengan 16 channel, sesuai dengan modul PCA9685.
Empat servo dihubungkan ke channel 0, 1, 2, dan 3 pada modul PCA9685.
Loop while menggerakkan setiap servo dari 0 hingga 180 derajat dan kembali lagi ke 0 derajat dengan penundaan waktu 0.01 detik di antara perubahan sudut.
try dan except digunakan untuk menangani penghentian program menggunakan Ctrl+C. Saat program dihentikan, semua servo dikembalikan ke posisi awal (0 derajat).
Pastikan untuk menyambungkan servo dengan benar ke modul PCA9685 dan modul PCA9685 terhubung ke Raspberry Pi melalui I2C.

Pi 3V3 to breakout VCC
Pi GND to breakout GND
Pi SCL to breakout SCL
Pi SDA to breakout SDA
