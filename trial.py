from tkinter import *
from PIL import Image, ImageTk
import RPi.GPIO as io
from adafruit_pca9685 import PCA9685
from adafruit_servokit import Servokit
from adafruit_vl53l0x import VL53L0X   
from adafruit_bus_device.i2c_device import I2CDevice
import os
import requests
import board
import busio


io.setwarnings(False)
io.setmode(io.BCM)

sampah_terkumpul = 0 
total_poin = 0
kondisi_sampah = "Sampah Penuh"
label_kondisi_sampah = "None"

# Pendeklarasian PushButton
pushbutton_merah = 15
pushbutton_hijau = 23
pushbutton_kuning = 8

# Pendeklarasian Sensor pin
proximity_sensor1 = 14
proximity_sensor2 = 18

# Pendeklarasian Servo
servo1_pin = 12
servo2_pin = 13

io.setup(servo1_pin, io.OUT)
io.setup(servo2_pin, io.OUT)
io.setup(pushbutton_merah, io.IN, pull_up_down=io.PUD_DOWN)
io.setup(pushbutton_hijau, io.IN, pull_up_down=io.PUD_DOWN)
io.setup(pushbutton_kuning, io.IN, pull_up_down=io.PUD_DOWN)
io.setup(proximity_sensor1, io.IN)
io.setup(proximity_sensor2, io.IN)

# Inisiasi PWM Servo pada pin GPIO dengan frekuensi 50Hz
gpio_pwm1 = io.PWM(servo1_pin, 50)
gpio_pwm2 = io.PWM(servo2_pin, 50)
gpio_pwm1.start(0)
gpio_pwm2.start(0)

# Inisiasi multiplexer dengan alamat I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Alamat multiplexer
multiplexer_address = 0x70
multiplexer = I2CDevice(i2c, multiplexer_address)

def select_channel (channel):
    if channel < 0 or channel > 7:
        raise ValueError("Channel harus antara 0 hingga 7")
    with multiplexer:
        multiplexer.write(bytes([1 << channel]))

# Memilih Channel 0 pada Multiplexer untuk servo
select_channel(0)

#  Inisiasi PWM Driver dan Servokit
pwm_driver = PCA9685(i2c)
pwm_driver.frequency = 50
kit = Servokit(channels=16, i2c = i2c)

# Fungsi untuk menggerakkan PWM Drivdr to servo
def move_servo(servo_num, angle):
    if servo_num not in [0,1,2,4]:
        raise ValueError("Servo number harus antara 0, 1, 2, atau 4")
    kit.servo[servo_num].angle = angle

# Kondisi Dimana Identifikasi Sampah Benar
def kondisi1():
    move_servo(0, 40)
    print("Servo berada dititik netral yaitu 40 derajat")
    time.sleep(2)
    move_servo(0, 0)
    print("Servo pada posisi 0 derajat")
    move_servo(0, 40)
    print("Servo pada kondisi Netral")

def kondisi2():
    move_servo(0, 40)
    print("Servo pada kondisi Netral")

    move_servo(1, 0)
    time.sleep(1)
    move_servo(1, 70)
    print("Mengeluarkan Kembali Botol")
    time.sleep(1)
    move_servo(1, 0)
    print("Servo dalam kondisi Netral")

# Fungsi untuk menggerakkan Servo pada GPIO
def set_servo_angle(gpio_pwm, angle):
    duty = angle / 18 + 2
    gpio_pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    gpio_pwm.ChangeDutyCycle(0)

# Fungsi untuk membaca jarak dari sensor VL53L0X
def read_sensor(sensor_num):
    select_channel(sensor_num)
    sensor = VL53L0X(i2c)
    return sensor.range

# Fungsi untuk menjalankan Sensor
def sensor_vlx():
    for i in range(2, 5):  # Sensor di channel 2, 3, 4
        distance = read_sensor(i)
        print(f"Sensor VLX di channel {i} mendeteksi jarak: {distance} mm")
    time.sleep(2)

stop_event = threading.Event()

def stop_threads():
    stop_event.set()

# Fungsi untuk Lanjut dan Kembali 
def check_button():
    global current_page

    # Detect green button (next)
    if io.input(pushbutton_hijau) == io.LOW:
        if not hasattr(check_button, "last_hijau_press") or time.time() - check_button.last_hijau_press > 0.5:  # debounce
            check_button.last_hijau_press = time.time()
            if current_page < len(pages) - 1:
                current_page += 1
                show_page(pages[current_page])
    
    # Detect red button (back)
    if io.input(pushbutton_merah) == io.LOW:
        if not hasattr(check_button, "last_merah_press") or time.time() - check_button.last_merah_press > 0.5:  # debounce
            check_button.last_merah_press = time.time()
            if current_page > 0:
                current_page -= 1
                show_page(pages[current_page])
    window.after(100, check_button)  # Check button state every 100ms

# Fungsi untuk membuka pintu utama
def pintu():
    print("Membuka Pintu")
    set_servo_angle(gpio_pwm1, 180)
    print("Menahan Botol 5 selama detik")
    set_servo_angle(gpio_pwm2, 40)        
    time.sleep(1)
    set_servo_angle(gpio_pwm2, 0)
    start_time = time.time()
    timeout = 5  # waktu maksimal untuk menunggu tombol hijau (dalam detik)

    while time.time() - start_time < timeout:
        if stop_event.is_set():
            return
        if io.input(pushbutton_hijau) == io.LOW:
            print("Menutup Pintu")
            set_servo_angle(gpio_pwm2, 40)
            set_servo_angle(gpio_pwm1, 0)
            return
        time.sleep(0.1)  # mengurangi penggunaan CPU dengan menambahkan delay kecil

    print("Menutup Pintu Otomatis")
    set_servo_angle(gpio_pwm1, 0)
    move_servo(0, 40)

# Fungsi Pengidentifikasian Botol Plastik
def identifikasi_sampah():
    while current_page == 3:
        if stop_event.is_set():
            return
        # Menempatkan nilai variabel sensor berupa input/output
        sensor1 = io.input(proximity_sensor1)
        sensor2 = io.input(proximity_sensor2)
        move_servo(0, 40)

        if sensor1 == io.LOW:
            print("Objek Terdeteksi Oleh 1 Sensor")
            kondisi1()
            time.sleep(2)

        elif sensor1 == io.LOW and sensor2 == io.LOW:
            print("Objek Terdeteksi Oleh 2 Sensor")
            kondisi2()
            time.sleep(2)
        else:
            print("Objek Tidak Terdeteksi")
        time.sleep(5)

def menambah():
    if io.input(pushbutton_kuning) == io.LOW:
        pintu()

def show_page(page_func):
    global page_frame
    page_frame.grid_forget()
    page_frame = Frame(window)
    page_frame.grid(columnspan=10)
    stop_event = threading.Event()
    page_func()
    
    # Logic to control servo on specific page
    if current_page == 2:  # Assuming langkah_2 is at index 2
        servo_thread = threading.Thread(target=pintu)
        servo_thread.start()
    if current_page == 3:
        sensor_thread = threading.Thread(target = identifikasi_sampah)
        sensor_thread.start()
        #timbang_thread = threading.Thread(target = menimbang)
        #timbang_thread.start()
    if current_page.start == 4:
        sensor_thread = threading.Thread(target = menambah)


# Inisialisasi jendela utama
window = Tk()
window.geometry("1000x500+600+400")
window.resizable(0, 0)  # Agar ukuran window tidak bisa diubah
window.title('Reverse Vending Machine')

# Inisiasi untuk lebar dan tinggi window
lebar = 1350
tinggi = 700

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
    global page_frame
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid(columnspan=5)

    label1 = Label(page_frame, text="SELAMAT DATANG DI\n REVERSE VENDING MACHINE", bd=2, bg="#88BC59", fg="black", font=("Tahoma", 20, "bold"), justify="center")
    label1.grid(column=1, row=0, columnspan=3, ipadx=100, pady=20)

    label2 = Label(page_frame, text="Anda dimohon untuk mengikuti dan membaca prosedur\n yang tertera dibawah ini!", fg="black", font=("Tahoma", 14))
    label2.grid(column=1, row=1, columnspan=3, pady=10)

    langkah1 = Label(page_frame, text=(
        "1. Tekan tombol Hijau untuk Next dan tekan tombol merah untuk Kembali\n"
        "2. Anda akan dipersilahkan untuk melakukan scan kode QR\n"
        "3. Masukkan sampah botol plastik ke dalam mesin melalui lubang yang tersedia\n"
        "4. Tunggu proses pengidentifikasian sampah anda\n"
        "5. Setelah teridentifikasi, Anda juga dapat memasukkan sampah lagi ke dalam mesin\n"
        "6. Lakukan scan kode QR yang tersedia untuk menukarkan semua sampah yang telah anda masukkan\n"
        "7. Ikuti langkah - langkah dengan seksama\n"
        "8. Tekan tombol berwarna Hijau (Next) untuk ke tahap langkah - langkah berikutnya"
    ), fg="black", font=("Tahoma", 16), wraplength=950, pady=10, justify="left")
    langkah1.grid(column=1, row=2, columnspan=3, pady=50)
    
    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="black", font=("Tahoma", 12, "bold"), bd=3, bg="#50C878", justify="right", command=langkah_1)
    tombol_next.grid(column=0, row=10, columnspan = 5, pady=5, ipadx=50)

def langkah_1():
    global page_frame, gambar_tk
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid()

    label1 = Label(page_frame, text= "LANGKAH 1\n SCAN KODE QR ", fg="black", bg ="#88BC59",bd =2,font=("Tahoma", 20, "bold"), justify="center")
    label1.grid(column=0, row=0, columnspan=5, ipadx = 10, padx =500, pady = 20)

    label2 = Label(page_frame, text = (
        "1. Silahkan melakukan scan kode QR dibawah ini\n"
        "2. Siapkan sampah Anda terlebih dahulu\n"
        "3. Setelah menekan tombol next, Anda diberi waktu 5 detik untuk memasukkan sampah"),fg = "black", font=("Tahoma", 16),bg ="#9DC183", wraplength=1000, pady = 10, justify="left")
    label2.grid(column =0, row= 1, columnspan=5, padx =100 ,ipadx =100 ,pady = 15)
    
    # Memuat Gambar menggunakan Barcode
    gambar_alamat = "/home/pi/vending_machine/barcode.jpeg"
    
    if not os.path.exists(gambar_alamat):
        print(f"File not found: {gambar_alamat}")
    else:
        gambar = Image.open(gambar_alamat) 
    
        # Resize gambar sesuai ukuran yang diinginkan (misal 50x50)
        desired_width = 200
        desired_height = 200
        gambar = gambar.resize((desired_width, desired_height), Image.ANTIALIAS)

        gambar_tk = ImageTk.PhotoImage(gambar)

        label_gambar = Label(page_frame, image=gambar_tk)
        label_gambar.grid(column = 0, row= 2, pady=30, ipadx=150, columnspan=5)

    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, bg = "#50C878",command = proses_scan_qr, justify = "right")
    tombol_next.grid(column = 1, row = 3, columnspan = 4, padx= 15, pady = 100, ipadx = 50)
    tombol_back = Button(page_frame, text="Kembali", activebackground="#C0392B", activeforeground="White", font=("Tahoma", 12, "bold"), fg = "white",bd=3, bg="#800000", command=landing_page, justify="left")
    tombol_back.grid(column=0, row=3,  columnspan = 1, padx = 100, pady= 100, ipadx=50)

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
    label1 = Label(page_frame, text = "Langkah 2\n Memasukkan Sampah Botol Plastik", fg = "black", bg="#88BC59", font= ("Tahoma", 20, "bold"),bd = 2,justify="center")
    label1.grid(column = 0, row = 0, columnspan = 5, padx =400, pady= 20)
    label2 = Label(page_frame, text = "HALLO "+ username +" SELAMAT DATANG!", fg = "black", font=("Tahoma", 16), bd= 2, wraplength=500, pady = 5, justify="left")
    label2.grid(column = 0, row = 1, columnspan = 5, padx =400 ,ipadx = 10, pady= 5)
    label3 = Label(page_frame, text = (
        "1. Silahkan masukkan satu sampah botol plastik\n\n"
        "2. Anda hanya diberi waktu 15 detik setelah pintu terbuka\n\n"
        "3. Setelah memasukkan botol tekanlah tombol Next\n\n"
        "4. Jika telah lewat 15 detik, maka pintu akan tertutup secara otomatis"), wraplength=950, fg= "black", font = ("Tahoma", 16), bd = 2, bg = "#9DC183",justify="left" )
    label3.grid(column=0, row = 2, columnspan=5, pady = 50)

    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, bg = "#50C878",command = langkah_3, justify = "right")
    tombol_next.grid(column =1, row = 4, columnspan=5, padx= 20, pady = 100, ipadx = 50)
    tombol_back = Button(page_frame, text="Kembali", activebackground="#C0392B", activeforeground="White", font=("Tahoma", 12, "bold"), fg = "white",bd=3, bg="#800000", command = langkah_1, justify="left")
    tombol_back.grid(column=0, row=4,  columnspan = 1, padx = 100, pady=100, ipadx=50)

def langkah_3():
    global page_frame
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid()

    label1 = Label(page_frame, text = "Langkah 3\n PROSES IDENTIFIKASI SAMPAH", fg = "black", bg="#88BC59", font= ("Tahoma", 20, "bold"), justify="center")
    label1.grid(column = 0, row = 0, columnspan = 5, ipadx=20, padx =410, pady= 20 )
    label2 = Label(page_frame, text = (
        "1. Tunggu proses identifikasi hingga terbaca!\n\n"
        "2. Tombol Kuning untuk menambah sampah\n\n"
        "3. Tombol Hijau untuk melanjutkan ke proses penukaran sampah"), fg= "black", font = ("Tahoma", 16),justify="left" )
    label2.grid(column=0, row = 1, columnspan=3, pady = 15)

    label3 = Label(page_frame, text = "Sampah Anda terkumpul : ", fg = "black", font=("Tahoma", 18, "bold"), bg = "#9DC183",justify="center")
    label3.grid(column=1, row=2, columnspan=3, padx = 50, ipadx= 10, pady =20)
    
    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, bg = "#50C878",command = penutup, justify = "right")
    tombol_next.grid(column = 2, row = 3, columnspan=2, padx= 15, pady = 300, ipadx = 50)
    tombol_tambah = Button(page_frame, text="Tambah", activebackground="#FFFAFA", activeforeground="Black", font=("Tahoma", 12, "bold"), fg = "blue",bd=3, bg="#F5f5dc", command=langkah_2, justify="left")
    tombol_tambah.grid(column=1, row=3, columnspan=2, padx = 15, pady=300, ipadx=50)

def transaksi_machine():
    global username, poinku
    pointChange = 100
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
    
    if (response.status_code == 200):
        print("Transaksi Berhasil Total Poin Anda Sekarang: " + poinku)
    else:
        print("Transaction Error: "+ poinku)

def penutup():
    global page_frame, poinku
    page_frame.grid_forget()
    
    page_frame = Frame(window)
    page_frame.grid()

    transaksi_machine()
    label1 = Label(page_frame, text = "SELAMAT, ANDA BERHASIL!",bg ="#88BC59", fg = "black", font= ("Tahoma", 20, "bold"), justify="center")
    label1.grid(column = 0, row=1, columnspan=5, pady= 20, ipadx =20 ,padx = 470,sticky="nsew")

    label2 = Label(page_frame, text = "ANDA TELAH MENDAPATKAN HADIAH SEBESAR",fg = "black", font= ("Tahoma", 16), justify="center")
    label2.grid(column = 1, row= 2, ipadx = 20, padx= 400, pady = 10, sticky="nsew")

    label3 = Label(page_frame, text = "Rp. "+poinku+"", fg = "black" ,bg="#ffe14c",font= ("Tahoma", 20,"bold"), justify="center")
    label3.grid(column = 1, row= 3, ipadx = "20",padx = 250, pady = 5)

    label4 = Label(page_frame, text = (
        "Terima Kasih untuk Anda yang telah\n"
        "membuang sampah botol plastik pada tempatnya dan\n"
        "menggunakan mesin ini sesuai dengan prosedur yang di informasikan\n"
        "Besar harapan kami untuk mengembangkan alat ini untuk menjadi lebih baik\n"
        "Jangan lupa untuk menekan tombol Hijau untuk selesai\n\n"
        "SAMPAI JUMPA LAGI\n"
        "SEMOGA HARI ANDA MENYENANGKAN"), fg = "black" ,bg="#9DC183",font= ("Tahoma", 16,"italic"), justify="center")
    label4.grid(column = 1, row= 4, columnspan=5, ipadx = 20 ,padx = 200, pady = 10)

    tombol_next = Button(page_frame, text="SELESAI", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, bg = "#50C878",command = akhir_page, justify = "right")
    tombol_next.grid(column = 1, row = 5, columnspan=5, padx= 200, pady = 200, ipadx = 20)
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

    label1 = Label(page_frame, text="Anda Berhasil Logout", fg = "black", bg = "#9DC183", font=("Tahoma", 18, "bold"), bd=2, justify="center")
    label1.grid(column=0, row=0, columnspan = 5,padx=550, pady=200)
    window.after(3000, landing_page)

# Inisiasi Daftar Pages
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
