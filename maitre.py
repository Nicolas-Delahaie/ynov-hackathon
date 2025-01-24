from math import sqrt
from machine import Pin, SoftI2C, PWM
from time import sleep_ms, sleep, gmtime, time
import dht
import network
import espnow

hp = PWM(Pin(25))

# Configurer le Wi-Fi pour ESP-NOW et MQTT
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Initialiser ESP-NOW
econnect = espnow.ESPNow()
econnect.active(True)

# Ajouter les esclaves
slave1_mac = b'\xc0I\xef\xcd\x8f\x14'  # Remplace par l'adresse MAC de l'esclave 1
slave2_mac = b'@"\xd8_;`'  # Remplace par l'adresse MAC de l'esclave 2
econnect.add_peer(slave1_mac)
econnect.add_peer(slave2_mac)


# Fonction pour jouer une note
def play_tone(frequency, duration):
    if frequency > 0:  # Si une fréquence est définie
        hp.freq(1000)  # Définir la fréquence
        hp.duty(250)  # Activer le son (50% de puissance)
        sleep(0.5)  # Maintenir la note
        hp.duty(0)  # Couper le son après la durée
    else:
        sleep(duration)  # Pause sans son


# Mélodie (fréquence en Hz, durée en secondes)
melody = [
    (440, 0.5),  # La (440 Hz) pendant 0.5 seconde
    (494, 0.5),  # Si (494 Hz)
    (523, 0.5),  # Do (523 Hz)
    (0, 0.2),  # Pause
    (440, 0.5)  # La
]

# Jouer la mélodie
for note in melody:
    play_tone(note[0], note[1])

# Arrêter le PWM après la mélodie
hp.deinit()

# Nom du fichier CSV
FILENAME = "data.csv"

# Variable pour éviter les doublons
last_logged_data = None


# Vérifier si le fichier existe
def file_exists(filename):
    try:
        with open(filename, 'r'):
            return True
    except OSError:
        return False


# Fonction pour enregistrer les données dans un fichier CSV
def log_data(data):
    global last_logged_data
    if data == last_logged_data:
        print("Données déjà enregistrées, saut de l'écriture.")
        return
    try:
        file_exists_flag = file_exists(FILENAME)
        with open(FILENAME, "a") as f:
            if not file_exists_flag:
                print(f"Création du fichier {FILENAME} avec en-tête.")
                f.write("Timestamp,Mesure,Valeur,Zone\n")
            f.write(data + "\n")
        print("Données enregistrées avec succès :", data)
        last_logged_data = data
    except OSError as e:
        print(f"Erreur lors de l'écriture dans le fichier {FILENAME} : {e}")


# Fonction pour convertir un entier signé
def signed_int_from_bytes(x, endian="big"):
    y = int.from_bytes(x, endian)
    if y >= 0x8000:
        return -((65535 - y) + 1)
    else:
        return y


# ---- Initialisation des capteurs ----
# Initialisation I2C pour le MPU6050
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)

# Initialisation du DHT22 (Humidité uniquement) sur GPIO23
sensor_dht = dht.DHT22(Pin(23))  # Connecté au GPIO23

try:
    while True:
        try:
            try:
                # Récupérer les données des esclaves via ESP-NOW
                host, msg = econnect.irecv()
                if msg:
                    msg = msg.decode('utf-8')
                    print(f"Données reçues de {host}: {msg}")

                    # Inclure une donnée locale (par exemple une mesure interne)
                    local_data = "Maître : Température locale = 25.5°C"

                sleep_ms(1)
            except Exception as e:
                print(e)
            # ---- Lecture de l'humidité via le DHT22 ----
            try:
                sensor_dht.measure()
                humidity = sensor_dht.humidity()
                print(f"Humidité : {humidity} %")
            except Exception as e:
                print(f"Erreur DHT22 : {e}")
                humidity = None

            # ---- Lecture des données du MPU6050 ----
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
                magnitude = (sqrt(x ** 2 + y ** 2 + z ** 2) - 1) / 1.24
                magnitude = max(0, min(magnitude, 1))  # Limiter entre 0 et 1
                print(f"Accélération X : {x:.2f}, Y : {y:.2f}, Z : {z:.2f}, Magnitude : {magnitude:.2f}")
            except Exception as e:
                print(f"Erreur MPU6050 : {e}")
                magnitude = None

            # ---- Générer l'horodatage ----
            timestamp = gmtime()  # Obtenir l'heure UTC actuelle
            human_readable_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5]
            )

            # ---- Enregistrer les données dans le fichier CSV ----
            if humidity is not None:
                log_data(f"{human_readable_time},Humidité,{humidity:.2f},2")
                log_data(f"{human_readable_time},Humidité,{humidity:.2f},3")
                log_data(f"{human_readable_time},Humidité,{humidity:.2f},4")
            if magnitude is not None:
                log_data(f"{human_readable_time},Séismes,{magnitude:.2f},3")

            # Pause de 5 secondes avant la prochaine lecture
            sleep(5)

            # ---- Recevoir les données via ESP-NOW ----
            host, msg = econnect.irecv()  # Réception non bloquante
            if msg:
                msg = msg.decode('utf-8')
                print(f"Données reçues de l'esclave : {msg}")
                timestamp = gmtime()
                human_readable_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                    timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5]
                )
                mesure, valeur, zone = msg.split(",")
                log_data(human_readable_time, mesure, valeur, zone)

        except Exception as e:
            print(f"Erreur secondaire : {e}")
except KeyboardInterrupt:
    print("Programme arrêté proprement.")


