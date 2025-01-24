# ynov-hackathon

## Comment faire fonctionner notre projet ?

### 1 - Configurer les ESP32
1. Télécharger le driver **'CP210x Universal Windows Driver'** si vous êtes sur Windows :  
   [Lien de téléchargement](https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads).
2. Télécharger **Thonny** :  
   [Lien de téléchargement](https://thonny.org/).
3. Ouvrir **Thonny**.
4. Configurer l'interpréteur :
   - Aller dans **'Exécuter'** dans la barre d'outils.
   - Cliquer sur **'Configurer l'interpréteur'**.
   - Sélectionner le type d'interpréteur : **'MicroPython (ESP32)'**.
   - Sélectionner le bon port : **'CP2102 US to UART Bridge Controller @ COM3'**.
   - Cliquer sur le lien **'Installer ou mettre à jour MicroPython (esptool) (UF2)'**.
   - Cliquer sur **'OK'**.

### 2 - Injecter le code dans les ESP32
1. Téléchargez ce projet.
2. Ouvrir **Thonny** avec l'ESP32 branché et configuré.
3. Afficher les fichiers sur l'ESP32 :
   - Aller dans **'Affichage'** dans la barre d'outils.
   - Cocher **'Fichiers'**.
   - Vous devriez voir un fichier **'boot.py'** dans votre ESP32.
4. Ajouter les bons fichiers dans les bons ESP32 : 
    - Entrez les adresses mac des ESP esclaves dans le script maitre.
    - Entrez l'adresse mac des ESP maitre dans les scripts esclaves.
    - Mettre le fichier **'esclave1.py'** dans l'ESP32 esclave qui embarque le capteur l'accéléromètre.
    - Mettre le fichier **'esclave2.py'** dans l'ESP32 esclave qui embarque le capteur l'accéléromètre.
    - Mettre le fichier **'maitre.py'** dans l'ESP32 maitre qui embarque un capteur accéléromètre et la capteur d'humidité. 

### 3 - Branchements
![Schéma branchements](./img/Capture%20d'écran%202025-01-24%20112215.png)
### 4 - Lancement
**!!!À compléter!!!**