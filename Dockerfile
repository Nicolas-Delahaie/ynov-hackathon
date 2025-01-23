# Utiliser une image Python comme base
FROM python:3.10-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    git \
    wget \
    build-essential \
    python3-pip \
    python3-venv \
    mosquitto \
    && apt-get clean

# Installer les outils Python pour ESP32/MicroPython
RUN pip install --no-cache-dir esptool adafruit-ampy

# Créer un dossier de travail dans le conteneur
WORKDIR /app

# Copier les fichiers du projet dans le conteneur
COPY . /app

# Définit la commande par défaut
CMD ["bash"]
