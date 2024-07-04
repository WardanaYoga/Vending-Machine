import RPi.GPIO as GPIO
from hx711 import HX711
import time
import sys

GPIO.setmode(GPIO.BCM)

dout_pin = 5
pd_sck_pin = 6

hx = HX711(dout_pin, pd_sck_pin)

def cleanAndExit():
    print("Cleaning up...")
    GPIO.cleanup()
    print("Bye!")
    sys.exit()

# Set tare untuk menetapkan nol tanpa beban
hx.tare()
print("Tare selesai. Tempatkan berat benda yang diketahui pada scale.")

input("Tekan Enter setelah menempatkan berat yang diketahui: ")

# Mengambil rata-rata dari beberapa pembacaan untuk akurasi
num_readings = 100  # Misalkan kita ingin mengambil rata-rata dari 10 pembacaan
reading = hx.read_average(num_readings)
print(f"Nilai rata-rata dari {num_readings} pembacaan: {reading}")

# Meminta berat yang diketahui dari pengguna
berat_diketahui_grams = input("Masukkan berat yang diketahui (dalam gram): ")
value = float(berat_diketahui_grams)

# Menghitung rasio kalibrasi dan menetapkan unit referensi
ratio = reading / value
hx.set_reference_unit(ratio)
print(f"Unit referensi diatur ke: {ratio}")

print("Kalibrasi selesai. Mulai pembacaan berat...")

try:
    while True:
        # Membaca berat dalam gram
        berat = hx.get_weight(5)  # Ambil rata-rata dari 5 pembacaan
        print(f"Berat: {berat:.2f} gram")
        
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

except (KeyboardInterrupt, SystemExit):
    cleanAndExit()

