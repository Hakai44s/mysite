#!/usr/bin/env python3
# Script pour lancer Streamlit sur PythonAnywhere

import os
import sys
import subprocess
import socket
import time

# Définir le chemin de l'application
app_path = '/home/Saad44/mysite'
streamlit_app = os.path.join('frontend', 'streamlit_app.py')

# Chemin vers l'exécutable Streamlit dans l'environnement virtuel
streamlit_path = '/home/Saad44/.virtualenvs/myenv/bin/streamlit'

# Essayer plusieurs ports qui pourraient être disponibles sur PythonAnywhere
ports_to_try = [8080, 8000, 3000, 5000, 8800, 8888, 9000, 9001, 9090]
port = None

for test_port in ports_to_try:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', test_port))
        port = test_port
        print(f"Port {port} disponible et sera utilisé pour Streamlit")
        break
    except OSError:
        print(f"Port {test_port} déjà utilisé, essai du port suivant...")

if port is None:
    print("Aucun port disponible trouvé parmi les ports testés. Veuillez libérer un port et réessayer.")
    sys.exit(1)


# Ajouter le chemin de l'application au PYTHONPATH
sys.path.append(app_path)

# Chemin complet vers l'application Streamlit
full_path = os.path.join(app_path, streamlit_app)

# Lancer Streamlit avec les options appropriées pour PythonAnywhere
# --server.port doit correspondre au port que vous avez configuré dans PythonAnywhere
# --server.address 0.0.0.0 permet d'accéder à l'application depuis l'extérieur
cmd = [
    streamlit_path, 'run', 
    full_path,
    '--server.port', str(port),
    '--server.address', '0.0.0.0',
    '--server.headless', 'true',
    '--browser.serverAddress', 'Saad44.pythonanywhere.com',  # Remplacez par votre nom d'utilisateur PythonAnywhere
    '--browser.gatherUsageStats', 'false'
]

# Exécuter la commande
subprocess.run(cmd)
