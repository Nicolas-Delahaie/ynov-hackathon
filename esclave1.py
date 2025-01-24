from math import sqrt
from machine import Pin, SoftI2C
from time import sleep_ms, sleep
import network
import espnow

# ---- Initialisation ESP-NOW ----
# Activer le Wi-Fi en mode station
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Initialiser ESP-NOW
espnow = espnow.ESPNow()
espnow.active(True)

# Adresse MAC du maître
master_mac = b'\xa0\xb7e\xdd\x1e\xa4'  # Remplace par l'adresse MAC réelle
espnow.add_peer(master_mac)

# ---- Initialisation du capteur MPU6050 ----
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)  # SCL sur GPIO22 et SDA sur GPIO21

# Fonction pour convertir un entier signé
def signed_int_from_bytes(x, endian="big"):
    y = int.from_bytes(x, endian)
    if y >= 0x8000:
        return -((65535 - y) + 1)
    else:
        return y

# Identifiant de l'esclave pour les messages
slave_id = "esclave"

# ---- Boucle principale ----
print("L'esclave est prêt et commence à envoyer des données...")

while True:
    try:
        # Lecture des données du capteur MPU6050
        try:
            # Réveiller le MPU-6050 (il démarre en mode veille)
            i2c.writeto_mem(0x68, 0x6B, bytes([0x00]))
            sleep_ms(5)

            # Lecture des données brutes des axes X, Y, Z (6 octets à partir de 0x3B)
            data = i2c.readfrom_mem(0x68, 0x3B, 6)
            x = signed_int_from_bytes(data[0:2]) / 16384.0
            y = signed_int_from_bytes(data[2:4]) / 16384.0
            z = signed_int_from_bytes(data[4:6]) / 16384.0

            # Calcul de la magnitude (normalisée entre 0 et 1)
            magnitude = (sqrt(x**2 + y**2 + z**2) - 1) / 1.24
            magnitude = max(0, min(magnitude, 1))  # Limiter entre 0 et 1

            # Créer un message formaté
            message = f"{slave_id},Séismes,{magnitude:.2f}"

            # Envoi des données au maître via ESP-NOW
            print(f"Envoi au maître : {message}")
            try:
                espnow.send(master_mac, message.encode('utf-8'))
                print("Données envoyées avec succès.")
            except Exception as e:
                print(f"Erreur lors de l'envoi au maître : {e}")

        except Exception as e:
            print(f"Erreur MPU6050 : {e}")

        # Pause avant la prochaine lecture
        sleep(5)

    except Exception as e:
        print(f"Erreur générale : {e}")
        break
 
 