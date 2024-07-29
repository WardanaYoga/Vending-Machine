from tkinter import *
from PIL import Image, ImageTk
import os
import requests
import json

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
    global page_frame
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid(columnspan=10)

    label1 = Label(page_frame, text="SELAMAT DATANG DI\n REVERSE VENDING MACHINE", bd=2, bg="#d1d1d1", fg="black", font=("Tahoma", 16, "bold"), justify="center")
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
    ), fg="black", font=("Tahoma", 12), wraplength=950, pady=10, justify="left")
    langkah1.grid(column=1, row=2, columnspan=3, pady=20)
    
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
    global page_frame
    page_frame.grid_forget()

    page_frame = Frame(window)
    page_frame.grid()

    label1 = Label(page_frame, text = "Langkah 3\n PROSES IDENTIFIKASI SAMPAH", fg = "black", bg="#F0E68C", font= ("Tahoma", 16, "bold"), justify="center")
    label1.grid(column = 0, row = 0, columnspan = 5, ipadx=20, padx =300, pady= 20)
    label2 = Label(page_frame, text = (
        "1. Tunggu proses identifikasi hingga terbaca!\n\n"
        "2. Tombol putih untuk menambah sampah\n\n"
        "3. Tombol Hijau untuk melanjutkan ke proses penukaran sampah"), fg= "black", font = ("Tahoma", 12),justify="left" )
    label2.grid(column=0, row = 1, columnspan=3, pady = 15)

    label3 = Label(page_frame, text = "Sampah Anda terkumpul : ", fg = "black", font=("Tahoma", 12, "bold"), bg = "#D3D3D3",justify="center")
    label3.grid(column=1, row=2, columnspan=3, padx = 50, ipadx= 10, pady =20)
    
    tombol_next = Button(page_frame, text="NEXT", activebackground="#0B6623", activeforeground="White", font=("Tahoma", 12, "bold"),fg="black",bd = 3, bg = "#50C878",command = penutup, justify = "right")
    tombol_next.grid(column = 2, row = 3, columnspan=2, padx= 15, pady = 150, ipadx = 50)
    tombol_tambah = Button(page_frame, text="Tambah", activebackground="#FFFAFA", activeforeground="Black", font=("Tahoma", 12, "bold"), fg = "blue",bd=3, bg="#F5f5dc", command=langkah_2, justify="left")
    tombol_tambah.grid(column=1, row=3, columnspan=2, padx = 15, pady=150, ipadx=50)

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
    
# Membuat frame awal untuk halaman
page_frame = Frame(window)
page_frame.grid()

# Memanggil halaman pertama
landing_page()

# Untuk perulangan program
window.mainloop()
