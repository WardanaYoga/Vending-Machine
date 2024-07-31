from tkinter import * #Digunakan untuk membuat gui
import RPi.GPIO as io   #Digunakan untuk kontrol GPIO di Raspberry Pi
from adafruit_servokit import ServoKit  # Digunakan untuk mengontrol Servo
from hx711 import HX711 #Digunakan untuk mengontrol Servo
import smbus #Digunakan untuk membaca data dari loadcell
from board import SCL, SDA #Digunakan untuk mengakses pin GPIO
import busio #Digunakan untuk inisialisasi komunikasi I2C
import adafruit_vl53l0x          #Digunakan untuk sensor jarak VL53L0X
from PIL import Image, ImageTk  #Digunakan untuk memanipulasi gambar
import os                       #Digunakan untuk berinteraksi dengan sistem operasi
import threading                #Digunakan untuk multithreadiing
import requests                 #Digunakan untuk HTTP Requests
import json  #Digunakan untuk memanipulasi data JSON
import time  #Digunakan unutuk operasi waktu

io.setwarnings(False)
io.setmode(io.BCM)  # BCM mode memiliki ruang lingkup luas

# Pendeklarasian Push Button
kit = ServoKit(channels = 16) #channel sesuai dengan yang ada pada PWM

# Alamat I2C PCA9548A (biasanya 0x70)
PCA9548A_ADDRESS = 0x70

# Inisialisasi bus I2C
bus = smbus.SMBus(1)  # 1 adalah bus I2C pada Raspberry Pi

# Inisialisasi bus I2C untuk sensor VL53L0X
i2c = busio.I2C(SCL, SDA)

#led = 14
pushbutton_merah = 23
pushbutton_hijau = 24
pushbutton_putih = 8

sampah_terkumpul = 0
total_poin = 0
kondisi_sampah = "Sampah Penuh"
label_kondisi_sampah = None
poinku

# Pendeklarasian sensor pin
proximity_sensor1 = 14 
proximity_sensor2 = 15
proximity_sensor3 = 18

# Pendeklarasian servo
servo1_pin = 12
servo2_pin = 13

#pendeklarasian loadcell hx711
dout_pin = 5
pd_sck_pin = 6

# Pendefinisian kategori sensor dan aktuator IN/OUT
#io.setup(led, io.OUT)
io.setup(servo1_pin, io.OUT)
io.setup(servo2_pin, io.OUT)
io.setup(pushbutton_merah, io.IN, pull_up_down=io.PUD_DOWN)
io.setup(pushbutton_hijau, io.IN, pull_up_down=io.PUD_DOWN)
io.setup(pushbutton_putih, io.IN, pull_up_down=io.PUD_DOWN)
io.setup(proximity_sensor1, io.IN)
io.setup(proximity_sensor2, io.IN)
io.setup(proximity_sensor3, io.IN)
#def led_on():
    #io.output(led, True)
    #print("Led Hidup")

#def led_off():
    #io.output(led, False)
    #print("Led Mati")

# Atur Frekuensi PWM untuk servo (biasanya 50Hz)
pwmservo1 = io.PWM(servo1_pin, 50)
pwmservo2 = io.PWM(servo2_pin, 50)

# Mulai PWM dengan duty cycle(siklus)
pwmservo1.start(0)
pwmservo2.start(0)


#Atur sudut awal servo pada PWM menajdi 0 derajat
kit.servo[0].angle = 0
kit.servo[1].angle = 0
kit.servo[2].angle = 0
kit.servo[3].angle = 0

# Pendefinisian Loadcell hx711
hx = HX711(dout_pin, pd_sck_pin)

stop_event = threading.Event()

def stop_threads():
    stop_event.set()

# Fungsi untuk Lanjut dan Kembali 
def check_button():
    global current_page

    # Detect green button (next)
    if io.input(pushbutton_hijau) == io.HIGH:
        if not hasattr(check_button, "last_hijau_press") or time.time() - check_button.last_hijau_press > 0.5:  # debounce
            check_button.last_hijau_press = time.time()
            if current_page < len(pages) - 1:
                current_page += 1
                show_page(pages[current_page])
    
    # Detect red button (back)
    if io.input(pushbutton_merah) == io.HIGH:
        if not hasattr(check_button, "last_merah_press") or time.time() - check_button.last_merah_press > 0.5:  # debounce
            check_button.last_merah_press = time.time()
            if current_page > 0:
                current_page -= 1
                show_page(pages[current_page])
    window.after(100, check_button)  # Check button state every 100ms

def set_servo_angle(pwm, angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

def select_channel():
    global channel
    if channel < 0 or channel > 7:
        raise ValueError("Channel harus berada dalam rentang 0-7")
    bus.write_byte(PCA9548A_ADDRESS, 1 << channel)

def read_sensor(channel):
    global kondisi_sampah, label_kondisi_sampah
    # Pilih saluran yang sesuai
    select_channel(channel)
    # Inisialisasi sensor VL53L0X
    sensor = adafruit_vl53l0x.VL53L0X(i2c)
    # Ambil pembacaan jarak dari sensor
    distance = sensor.range
    print(f"Channel {channel} Distance: {distance} mm")

    distance=[]
    distance0 = read_sensor(0)
    distances.append(distance0)
    
    # Baca sensor di saluran 1
    distance1 = read_sensor(1)
    distances.append(distance1)
    
    # Baca sensor di saluran 2
    distance2 = read_sensor(2)
    distances.append(distance2)
    
    # Hitung nilai minimum, maksimum, dan rentang
    min_distance = min(distances)
    max_distance = max(distances)
    range_distance = max_distance - min_distance
    
    print(f"Minimum Distance: {min_distance} mm")
    print(f"Maximum Distance: {max_distance} mm")
    print(f"Range: {range_distance} mm")

    if range_distance <= 200:
        print("Sampah Penuhh!!!")
        label_kondisi_sampah.config(text = f"Sampah dalam kondisi: {kondisi_sampah}")
    else:
        kondisi_sampah = "Belum Penuh"
        if label_kondisi_sampah:
            label_kondisi_sampah.config(text = f"Sampah dalam Kondisi {kondisi_sampah}") 
    time.sleep(2)


def pintu():
    print("Membuka Pintu")
    set_servo_angle(pwmservo1, 180) 

    start_time = time.time()
    timeout = 5  # waktu maksimal untuk menunggu tombol hijau (dalam detik)

    while time.time() - start_time < timeout:
        if stop_event.is_set():
            return
        if io.input(pushbutton_hijau) == io.HIGH:
            print("Menutup Pintu")
            set_servo_angle(pwmservo1, 0)
            return
        time.sleep(0.1)  # mengurangi penggunaan CPU dengan menambahkan delay kecil

    print("Menutup Pintu Otomatis")
    set_servo_angle(pwmservo1, 0)
    
def identifikasi_sampah():
    while current_page == 3:
        if stop_event.is_set():
            return
        # Menempatkan nilai variabel sensor berupa input/output
        sensor1 = io.input(proximity_sensor1)
        sensor2 = io.input(proximity_sensor2)
        sensor3 = io.input(proximity_sensor3)
        
        if sensor1 == io.LOW:
            print("Objek Terdeteksi Oleh 1 Sensor")
            print("Membuka Pintu")
            set_servo_angle(pwmservo2, 180)
            time.sleep(0.01)
            
            time.sleep(1)
            
            print("Menutup Pintu")
            set_servo_angle(pwmservo2, 0)
            time.sleep(0.01)
            
        elif sensor1 == io.LOW and sensor2 == io.LOW:
            print("Objek Terdeteksi Oleh 2 Sensor")
            print("Membuka Pintu")
            set_servo_angle(pwmservo2, 180)
            time.sleep(0.01)
            
            time.sleep(1)
            
            print("Menutup Pintu")
            set_servo_angle(pwmservo2, 0)
            time.sleep(0.01)
            
        elif sensor1 == io.LOW and sensor2 == io.LOW and sensor3 == io.LOW:
            print("Objek Terdeteksi Oleh 3 Sensor")
            print("Membuka Pintu Keluar")
            for angle in range (0, 181, 1):
                kit.servo[0].angle = angle
                time.sleep(0.01)
                
            time.sleep(1)
            
            print("Menutup Pintu Keluar")
            for angle in range (180, -1, -1):
                kit.servo[0].angle = angle
                time.sleep(0.01)
        
        # waktu maksimal untuk menunggu tombol hijau (dalam detik)
        else:
            print("Objek Tidak Terdeteksi")
        time.sleep(5)
    
def menimbang():
    global sampah_terkumpul, label_sampah_terkumpul  # Pastikan variabel global dideklarasikan
    
    #======= Settings Loadcell Sesuai Dengan Berat yang telah diketahui ===== #
    
    # Setting tare untuk menetapkan nilai nol
    hx.tare()
    
    # Mengambil rata-rata dari beberapa pembacaan untuk akurasi
    num_readings = 1000  # mengambil rata-rata dari 1000 pembacaan
    reading = 157365.06666666668  # referensi rata-rata yang telah didapat dari kalibrasi
    print(f"Nilai rata - rata dari {num_readings} pembacaan : {reading}")
    value = 100
    
    # Menghitung rasio kalibrasi dan menetapkan unit referensi
    ratio = reading / value
    hx.set_reference_unit(ratio)
    print("Kalibrasi selesai, Mulai pembacaan berat...")
    
    while current_page == 3:
        berat = hx.get_weight(5)  # Ambil rata-rata dari 5 pembacaan
        print(f"Berat: {berat:.2f} gram")
        time.sleep(5)
        
        # Mendeteksi berat botol yang tidak terdapat air
        if 18 <= berat <= 21:
            print("Botol Terdeteksi Benar")
            for angle in range(0, 181, 1):
                kit.servo[1].angle = angle
                time.sleep(0.01)
                
            time.sleep(1)
            sampah_terkumpul += 1  # Memperbarui variabel global
            label_sampah_terkumpul.config(text=f"Sampah Anda terkumpul: {sampah_terkumpul}")
            kirim_data_ke_api(100)
            print("Botol Telah Terverifikasi")
            for angle in range(180, -1, -1):
                kit.servo[1].angle = angle
                time.sleep(0.01)
                
        elif berat > 21:
            print("Botol Terdeteksi Air")
            for angle in range(0, 181, 1):
                kit.servo[2].angle = angle
                time.sleep(0.01)
                
            time.sleep(1)
            
            print("Botol Telah Dikeluarkan")
            for angle in range(180, -1, -1):
                kit.servo[2].angle = angle
                time.sleep(0.01)
                
        hx.power_down()
        hx.power_up()
        time.sleep(0.5)
    #======#
def menambah():        
    if io.input(pushbutton_putih) == io.HIGH:
        print("Membuka Pintu")
        set_servo_angle(pwmservo1, 180)
        
        start_time = time.time()
        timeout = 5
            
    while time.time() - start_time < timeout:
        if stop_event.is_set():
            print("Stop event terdeteksi, keluar dari fungsi")
            return
        if io.input(pushbutton_hijau) == io.HIGH:
            print("Menutup Pintu Utama")
            set_servo_angle(pwmservo1, 0)
            return
        time.sleep(0.01)
    print("Timeout! Menutup Pintu Utama")
    set_servo_angle(pwmservo1, 0)

def show_page(page_func):
    global page_frame, stop_event
    page_frame.grid_forget()
    page_frame = Frame(window)
    page_frame.grid(columnspan=10)
    stop_event = threading.Event()
    page_func()
    
    # Logic to control servo on specific page
    if current_page == 2:  # Assuming langkah_2 pada index 2
        servo_thread = threading.Thread(target=pintu)
        servo_thread.start()
    if current_page == 3:
        sensor_thread = threading.Thread(target = identifikasi_sampah)
        sensor_thread.start()
        timbang_thread = threading.Thread(target = menimbang)
        timbang_thread.start()
        tambah_thread = threading.Thread(target  = menambah)
        timbang_thread.start()
            
# Inisialisasi jendela utama
window = Tk()
window.geometry("1000x500+600+400")
window.resizable(0, 0)  # Agar ukuran window tidak bisa diubah
window.title('Reverse Vending Machine')

# Inisiasi untuk lebar dan tinggi window
lebar = 1000
tinggi = 500

# Mendapatkan ukuran layar
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()

# Menghitung posisi baru untuk menempatkan window di tengah layar
newx = int((screenwidth / 2) - (lebar / 2))
newy = int((screenheight / 2) - (tinggi / 2))

# Menetapkan ukuran dan posisi baru untuk window
window.geometry(f"{lebar}x{tinggi}+{newx}+{newy}")

# Konfigurasi kolom
for i in range(5):
    window.columnconfigure(i, weight=1)

def landing_page():
    global page_frame, label_kondisi_sampah
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid(columnspan=10)

    label1 = Label(page_frame, text="SELAMAT DATANG DI\n REVERSE VENDING MACHINE", bd=2, bg="#d1d1d1", fg="black", font=("Tahoma", 16, "bold"), justify="center")
    label1.grid(column=1, row=0, columnspan=3, ipadx=100, pady=20)

    label2 = Label(page_frame, text="Anda dimohon untuk mengikuti dan membaca prosedur\n yang tertera dibawah ini!", fg="black", font=("Tahoma", 14))
    label2.grid(column=1, row=1, columnspan=3, pady=10)

    label_kondisi_sampah = Label(page_frame, text=(
        "1. Tekan tombol Hijau untuk Next dan tekan tombol merah untuk Kembali\n"
        "2. Anda akan dipersilahkan untuk melakukan scan kode QR\n"
        "3. Masukkan sampah botol plastik ke dalam mesin melalui lubang yang tersedia\n"
        "4. Tunggu proses pengidentifikasian sampah anda\n"
        "5. Setelah teridentifikasi, Anda juga dapat memasukkan sampah lagi ke dalam mesin\n"
        "6. Lakukan scan kode QR yang tersedia untuk menukarkan semua sampah yang telah anda masukkan\n"
        "7. Ikuti langkah - langkah dengan seksama\n"
        "8. Tekan tombol berwarna Hijau (Next) untuk ke tahap langkah - langkah berikutnya"
        f"Sampah dalam Kondisi = {kondisi_sampah}"
    ), fg="black", font=("Tahoma", 12), wraplength=950, pady=10, justify="left")
    label_kondisi_sampah.grid(column=1, row=2, columnspan=3, pady=20)
    
    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="black", font=("Tahoma", 12, "bold"), bd=3, bg="#50C878", justify="right", command=langkah_1)
    tombol_next.grid(column=0, row=10, columnspan = 5, pady=5, ipadx=50)

def langkah_1():
    global page_frame, gambar_tk
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid()

    label1 = Label(page_frame, text= "LANGKAH 1\n SCAN KODE QR ", fg="black", bg ="#ADD8E6",bd =2,font=("Tahoma", 16, "bold"), justify="center")
    label1.grid(column=0, row=0, columnspan=5, ipadx = 10, padx =400, pady = 20)

    label2 = Label(page_frame, text = (
        "1. Silahkan melakukan scan kode QR dibawah ini\n"
        "2. Siapkan sampah Anda terlebih dahulu\n"
        "3. Setelah menekan tombol next, Anda diberi waktu 40 detik untuk memasukkan sampah"),fg = "black", font=("Tahoma", 12),bg ="#D3D3D3", wraplength=950, pady = 10, justify="left")
    label2.grid(column =0, row= 1, columnspan=5, padx =100 ,ipadx =20 ,pady = 5)
    
    # Memuat Gambar menggunakan Barcode
    gambar_alamat = "C:\\Users\\ub\\Latihan\\barcode.jpeg"
    
    if not os.path.exists(gambar_alamat):
        print(f"File not found: {gambar_alamat}")
    else:
        gambar = Image.open(gambar_alamat) 
    
        # Resize gambar sesuai ukuran yang diinginkan (misal 50x50)
        desired_width = 150
        desired_height = 150
        gambar = gambar.resize((desired_width, desired_height), Image.Resampling.LANCZOS)

        gambar_tk = ImageTk.PhotoImage(gambar)

        label_gambar = Label(page_frame, image=gambar_tk)
        label_gambar.grid(column = 0, row= 2, pady=10, ipadx=150, columnspan=5)

    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, bg = "#50C878",command = proses_scan_qr, justify = "right")
    tombol_next.grid(column = 1, row = 3, columnspan = 4, padx= 15, pady = 50, ipadx = 50)
    tombol_back = Button(page_frame, text="Kembali", activebackground="#C0392B", activeforeground="White", font=("Tahoma", 12, "bold"), fg = "white",bd=3, bg="#800000", command=landing_page, justify="left")
    tombol_back.grid(column=0, row=3,  columnspan = 1, padx = 100, pady= 50, ipadx=50)

def proses_scan_qr():
    global username
    # Ganti URL dan parameter sesuai kebutuhan
    url = "http://156.67.214.154/statusMachine.php"
    params = {"unique_id": "4a90bc46-7e44-4daf-b2b3-92f8ffb2adfe"}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print("Data dari API:", data)  # Debugging print untuk memeriksa struktur data
        
        # Menangani respons list
        if isinstance(data, list) and len(data) > 0:
            if data[0]['status']:
                username = data[0]['usermachine']
                print(username)
                langkah_2()
            else:
                print("Mesin tidak tersedia")
                # Tambahkan pesan kesalahan di UI sesuai kebutuhan
        else:
            print("Respons tidak valid atau format data tidak sesuai")
            # Tambahkan pesan kesalahan di UI sesuai kebutuhan
    else:
        print("Gagal mengambil status mesin")
        # Tambahkan pesan kesalahan di UI sesuai kebutuhan

def langkah_2():
    global page_frame, username
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid()
    label1 = Label(page_frame, text = "Langkah 2\n Memasukkan Sampah Botol Plastik", fg = "black", bg="#D8BFF8", font= ("Tahoma", 16, "bold"),bd = 2,justify="center")
    label1.grid(column = 0, row = 0, columnspan = 3, padx =300, pady= 20)
    label2 = Label(page_frame, text = "HALLO "+ username +" SELAMAT DATANG!", fg = "black", font=("Tahoma", 16), bd= 2, wraplength=500, pady = 5, justify="left")
    label2.grid(column = 0, row = 1, columnspan = 3, padx =300 ,ipadx = 10, pady= 5)
    label3 = Label(page_frame, text = (
        "1. Silahkan masukkan satu sampah botol plastik\n\n"
        "2. Anda hanya diberi waktu 40 detik setelah pintu terbuka\n\n"
        "3. Setelah memasukkan botol tekanlah tombol Next\n\n"
        "4. Jika telah lewat 40 detik, maka pintu akan tertutup secara otomatis"), wraplength=950, fg= "black", font = ("Tahoma", 12), bd = 2, bg = "#997950",justify="left" )
    label3.grid(column=0, row = 2, columnspan=3, pady = 20)

    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, bg = "#50C878",command = langkah_3, justify = "right")
    tombol_next.grid(column =1, row = 4, columnspan=2, padx= 10, pady = 100, ipadx = 50)
    tombol_back = Button(page_frame, text="Kembali", activebackground="#C0392B", activeforeground="White", font=("Tahoma", 12, "bold"), fg = "white",bd=3, bg="#800000", command = langkah_1, justify="left")
    tombol_back.grid(column=0, row=4,  columnspan = 2, padx = 1, pady=100, ipadx=50)

def langkah_3():
    global page_frame, label_sampah_terkumpul
    page_frame.grid_forget()
    page_frame = Frame(window)
    page_frame.grid()
    
    label1 = Label(page_frame, text = "LANGKAH 3\n IDENTIFIKASI BOTOL", fg = "black", bg="#88bc59", font= ("Tahoma", 16, "bold"), justify="center")
    label1.grid(column = 0, row = 0, columnspan = 5, ipadx=20, padx =300, pady= 20)
    
    label2 = Label(page_frame, text = (
        "1. Tunggu proses identifikasi hingga terbaca!\n\n"
        "2. Tombol putih untuk menambah sampah\n\n"
        "3. Tombol Hijau untuk melanjutkan ke proses penukaran sampah"), bg = "#ffffff",fg= "black", font = ("Tahoma", 12),justify="left" )
    label2.grid(column=0, row = 1, columnspan=3, pady = 15)
    
    label_sampah_terkumpul = Label(page_frame, text = "Sampah Anda terkumpul : 0", fg = "black", font=("Tahoma", 12, "bold"), bg = "#F0E68C",justify="center")
    label_sampah_terkumpul.grid(column=1, row=2, columnspan= 4, padx = 300, ipadx= 50, pady =20)
    
    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, command = penutup, bg = "#50C878",justify = "right")
    tombol_next.grid(column = 2, row = 3, columnspan=6, padx= 15, pady = 150, ipadx = 50)
    
    tombol_tambah = Button(page_frame, text="menambah", activebackground="#FFFAFA", activeforeground="Black", font=("Tahoma", 12, "bold"), fg = "blue",bd=3, bg="#F5f5dc", justify="left")
    tombol_tambah.grid(column=1, row=3, columnspan=3, padx = 15, pady=150, ipadx=50)

def transaksi_machine():
    global username, poinku, sampah_terkumpul, nominal_penukaran_sampah
    pointChange = 100 * sampah_terkumpul
    macAddr = 'dc:a6:32:d1:d3:b5'
    passwordMachine = "topPlayerChou"
    uniqueID = "4a90bc46-7e44-4daf-b2b3-92f8ffb2adfe"
    
    url = "http://156.67.214.154/transactionmc.php"
    data = {
        "username": username,
        "mac_address": macAddr,
        "password": passwordMachine,
        "unique_id": uniqueID,
        "poin_change": pointChange
        }
    response = requests.post(url, data=data)
    poinku = response.text
    nominal_penukaran_sampah = pointChange + int(poinku)
    if (response.status_code == 200):
        print("Transaksi Berhasil Total Poin Anda Sekarang: " + str(nominal_penukaran_sampah))
    else:
        print("Transaction Error: "+ nominal_penukaran_sampah)

def penutup():
    global page_frame, poinku
    page_frame.grid_forget()
    
    page_frame = Frame(window)
    page_frame.grid()

    transaksi_machine()
    label1 = Label(page_frame, text = "SELAMAT, ANDA BERHASIL!",bg ="#ffe14c", fg = "black", font= ("Tahoma", 18, "bold"), justify="center")
    label1.grid(column = 0, row=1, columnspan=5, pady= 20, ipadx =20 ,padx = 300,sticky="nsew")

    label2 = Label(page_frame, text = "ANDA TELAH MENDAPATKAN HADIAH SEBESAR",fg = "black", font= ("Tahoma", 16), justify="center")
    label2.grid(column = 1, row= 2, ipadx = 20, padx= 250, pady = 10, sticky="nsew")

    label3 = Label(page_frame, text = "Rp. "+poinku+"", fg = "black" ,bg="#ffb380",font= ("Tahoma", 16,"bold"), justify="center")
    label3.grid(column = 1, row= 3, ipadx = "20",padx = 250, pady = 10)

    label4 = Label(page_frame, text = (
        "Terima Kasih untuk Anda yang telah\n"
        "membuang sampah botol plastik pada tempatnya dan\n"
        "menggunakan mesin ini sesuai dengan prosedur yang di informasikan\n"
        "Besar harapan kami untuk mengembangkan alat ini untuk menjadi lebih baik\n"
        "Jangan lupa untuk menekan tombol Hijau untuk selesai\n\n"
        "SAMPAI JUMPA LAGI\n"
        "SEMOGA HARI ANDA MENYENANGKAN"), fg = "black" ,bg="#d1d1d1",font= ("Tahoma", 12,"italic"), justify="center")
    label4.grid(column = 1, row= 4, columnspan=5, ipadx = 20 ,padx = 200, pady = 10)

    tombol_next = Button(page_frame, text="SELESAI", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, bg = "#50C878",command = akhir_page, justify = "right")
    tombol_next.grid(column = 1, row = 5, columnspan=5, padx= 200, pady = 50, ipadx = 20)
    user_matikan_mesin()

def user_matikan_mesin():
    global username
    # Panggil API untuk mematikan mesin
    url = "http://156.67.214.154/updateMachine.php"
    unique_id = '4a90bc46-7e44-4daf-b2b3-92f8ffb2adfe'
    status = 'false'
    username = ''
    payload = {
        'unique_id': unique_id,
        'status': status,
        'userMachine': username
        }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Berhasil Logout")
    else:
        print("Gagal Logout")


def akhir_page():
    global page_frame
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid()

    label1 = Label(page_frame, text="Anda Berhasil Logout", fg = "black", bg = "#D8BFD8", font=("Tahoma", 18, "bold"), bd=2, justify="center")
    label1.grid(column=0, row=0, columnspan=3, padx=300, pady=20)
    window.after(3000, landing_page)
    
# Initialize pages list
pages = [landing_page, langkah_1, langkah_2, langkah_3, penutup, akhir_page]
current_page = 0

# Membuat frame awal untuk halaman
page_frame = Frame(window)
page_frame.grid()

# Memanggil halaman pertama
show_page(pages[current_page])
window.after(100, check_button)

# Menambahkan event handling untuk window close
window.protocol("WM_DELETE_WINDOW", stop_threads)

# Untuk perulangan program
window.mainloop()
