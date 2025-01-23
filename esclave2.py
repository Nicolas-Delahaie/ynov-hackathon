import network
import espnow
import time
from machine import Pin, I2C
from mpu6050 import MPU6050  # Assurez-vous d'avoir la bibliothèque mpu6050

# Activer le Wi-Fi en mode station
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Initialiser ESP-NOW
e = espnow.ESPNow()
e.init()

# Adresse MAC du maître (remplace par l'adresse MAC de ton ESP32 maître)
master_mac = b'\xa0\xb7e\xdd\x1e\xa4'
e.add_peer(master_mac)

# Initialiser le MPU6050
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
mpu = MPU6050(i2c)

# Envoi des données au maître
while True:
    try:
        accel = mpu.acceleration  # Données d'accélération
        message = f"Accel: X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}"
        print(f"Envoi : {message}")
        e.send(master_mac, message.encode('utf-8'))
        time.sleep(5)  # Attendre 5 secondes avant le prochain envoi
    except Exception as e:
        print(f"Erreur : {e}")
