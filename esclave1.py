import network
import espnow
import time
from machine import Pin
import dht

# Activer le Wi-Fi en mode station
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Initialiser ESP-NOW
e = espnow.ESPNow()
e.init()

# Adresse MAC du maître (remplace par l'adresse MAC de ton ESP32 maître)
master_mac = b'\xa0\xb7e\xdd\x1e\xa4'
e.add_peer(master_mac)

# Initialiser le capteur DHT22
sensor = dht.DHT22(Pin(4))  # Connecté au GPIO4

# Envoi des données au maître
while True:
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        message = f"Temp: {temperature}C, Hum: {humidity}%"
        print(f"Envoi : {message}")
        e.send(master_mac, message.encode('utf-8'))
        time.sleep(5)  # Attendre 5 secondes avant le prochain envoi
    except Exception as e:
        print(f"Erreur : {e}")
