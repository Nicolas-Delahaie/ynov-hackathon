import network
import espnow
import time
from umqtt.simple import MQTTClient  # Bibliothèque MQTT pour MicroPython

# Configurer le Wi-Fi pour ESP-NOW et MQTT
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Initialiser ESP-NOW
e = espnow.ESPNow()
e.init()

# Ajouter les esclaves
slave1_mac = b'\xc0I\xef\xcd\x8f\x14'  # Remplace par l'adresse MAC de l'esclave 1
slave2_mac = b'@"\xd8_;`'  # Remplace par l'adresse MAC de l'esclave 2
e.add_peer(slave1_mac)
e.add_peer(slave2_mac)

# Configurer MQTT
BROKER = "10.31.32.151"  # Adresse IP du broker MQTT (modifie selon ton réseau)
TOPIC = "esp32/data"
mqtt_client = MQTTClient("esp32_master", BROKER)

mqtt_client.connect()
print("Connecté au broker MQTT")

# Récupérer et publier les données
print("En attente des données des esclaves...")
while True:
    try:
        # Récupérer les données des esclaves via ESP-NOW
        host, msg = e.irecv()
        if msg:
            msg = msg.decode('utf-8')
            print(f"Données reçues de {host}: {msg}")
            
            print(f"Publication MQTT : {msg}")
            
            # Publier les données sur MQTT
            mqtt_client.publish(TOPIC, msg)
            
        time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt du maître")
        mqtt_client.disconnect()
        break
