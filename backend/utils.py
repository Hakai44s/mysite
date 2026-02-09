"""
Fonctions utilitaires pour le back-end
"""
import json
import os
import csv
from datetime import datetime
from .config import DATA_FILE

def format_number(number):
    """
    Formate un nombre pour l'affichage
    """
    if isinstance(number, (int, float)):
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.2f}B"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.2f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.2f}K"
        else:
            return f"{number:.2f}"
    return str(number)

def save_crypto_balance(token_balance_dict):
    """
    Sauvegarde les soldes de cryptomonnaies dans un fichier CSV
    """
    # Récupère la date et l'heure actuelles
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # S'assurer que le répertoire existe
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    # Ajouter les données à un fichier CSV
    with open(DATA_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Si le fichier est vide, on ajoute les en-têtes
        if csvfile.tell() == 0:
            writer.writerow(["Date", "Crypto", "Valeur"])

        # Écrire les données pour chaque crypto-monnaie
        for crypto, value in token_balance_dict.items():
            writer.writerow([current_time, crypto, value])

    return current_time

def load_counter():
    """
    Charge le compteur depuis le fichier counter.json
    """
    counter_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "counter.json")
    
    if os.path.exists(counter_file):
        try:
            with open(counter_file, 'r') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    else:
        # Créer un nouveau fichier counter.json si non existant
        data = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        with open(counter_file, 'w') as f:
            json.dump(data, f)
        return data

def save_counter(data):
    """
    Sauvegarde le compteur dans le fichier counter.json
    """
    counter_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "counter.json")
    
    with open(counter_file, 'w') as f:
        json.dump(data, f)
