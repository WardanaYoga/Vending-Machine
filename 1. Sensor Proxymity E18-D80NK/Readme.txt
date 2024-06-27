Sensor proximity umumnya tidak memerlukan pin PWM atau pin khusus lainnya pada Raspberry Pi. Sebagian besar sensor proximity menggunakan pin GPIO biasa untuk mengirim sinyal digital (HIGH atau LOW) ke Raspberry Pi. Berikut adalah beberapa poin penting:

Sensor Digital:
Jika sensor proximity Anda adalah sensor digital (biasanya mengeluarkan sinyal HIGH atau LOW), Anda hanya perlu menggunakan pin GPIO biasa untuk menerima sinyal tersebut. Pin GPIO dapat dikonfigurasi sebagai input untuk membaca sinyal dari sensor.

Sensor Analog:
Jika sensor proximity Anda adalah sensor analog (mengeluarkan sinyal tegangan yang bervariasi), Raspberry Pi tidak memiliki pin ADC (Analog-to-Digital Converter) bawaan. Anda memerlukan modul eksternal seperti MCP3008 untuk mengubah sinyal analog menjadi sinyal digital yang dapat dibaca oleh Raspberry Pi.

Sensor dengan Output PWM:
Beberapa sensor proximity mungkin memiliki output PWM. Dalam kasus ini, Anda perlu membaca sinyal PWM, yang juga dapat dilakukan dengan pin GPIO biasa, tetapi membutuhkan pemrosesan sinyal PWM di perangkat lunak.

VCC : 5v
