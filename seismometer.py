# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()
from math import sqrt
from machine import Pin, SoftI2C
from time import sleep_ms, sleep, time
import os

# Nom du fichier CSV
FILENAME = "data.csv"

# Fonction pour vérifier si le fichier existe
def file_exists(filename):
    try:
        with open(filename, 'r'):
            return True
    except OSError:
        return False

# Fonction pour écrire les données dans le fichier CSV
def log_data(data):

    file_exists_flag = file_exists(FILENAME)
    with open(FILENAME, 'a') as f:
        if not file_exists_flag:
            # timestamp type valeur zone
            f.write("Timestamp,Mesure,Valeur,Zone\n")
        f.write(data + "\n")
    
    print("Données enregistrées:", data)

def signedIntFromBytes(x, endian="big"):
    y = int.from_bytes(x, endian)
    if (y >= 0x8000):
        return -((65535 - y) + 1)
    else:
        return y


i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)

scaler = 16384.0

while True:
    try:
        # Wake up the MPU-6050 since it starts in sleep mode
        i2c.writeto_mem(0x68, 0x6B, bytes([0x00]))
        sleep_ms(5)
    except Exception as e:
        print("ESP32 could not communicate with module")
        raise e

    # 0x3B

    data = i2c.readfrom_mem(0x68, 0x3B, 6)

    x = signedIntFromBytes(data[0:2]) / 16384.0
    y = signedIntFromBytes(data[2:4]) / 16384.0
    z = signedIntFromBytes(data[4:6]) / 16384.0
    d = {"x": x, "y": y, "z": z}

    res = (sqrt(d["x"] ** 2 + d["y"] ** 2 + d["z"] ** 2) - 1) / 1.24

    if res < 0:
        res = 0
    if res > 1:
        res = 1

    timestamp = time.gmtime()
    zone = 3
    type = 'séismes'

    # Formatage des données pour l'écriture dans le CSV
    data_line = f"{timestamp},{type},{res},{zone}"

    # Appel de la fonction pour enregistrer les données
    log_data(data_line)

    sleep(5)
