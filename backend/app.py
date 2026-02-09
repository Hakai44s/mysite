"""
Application Flask principale pour le back-end
"""
from flask import Flask, request, render_template, jsonify
import threading
import schedule
import time
from datetime import datetime
import os
import json
import ssl
import urllib3

# Importation des modules du back-end
from .crypto_data import update_data, TOTAL, token_balance_dict, token_price_dict, token_mc_dict, goldPrice, is_mock_data_used
from .utils import save_crypto_balance
from .zakat import calcul_zakat
from .visualization import makePlot, calculate_evolution
from .config import FLASK_CONFIG

# Configuration pour ignorer les erreurs SSL
# ATTENTION: Ã€ utiliser uniquement en dÃ©veloppement
import requests
requests.packages.urllib3.disable_warnings()
old_merge_environment_settings = requests.Session.merge_environment_settings

def merge_environment_settings(self, url, proxies, stream, verify, cert):
    return old_merge_environment_settings(self, url, proxies, stream, False, cert)

requests.Session.merge_environment_settings = merge_environment_settings

# CrÃ©ation de l'application Flask
app = Flask(__name__, 
            template_folder='../template',
            static_folder='../static')
app.config['JSON_SORT_KEYS'] = False  # Pour prÃ©server l'ordre des clÃ©s dans les rÃ©ponses JSON

@app.route('/')
def home():
    """
    Route pour la page d'accueil (template HTML)
    """
    # Mettre Ã  jour les donnÃ©es
    total, token_balance, token_price, token_mc, gold_price = update_data()
    
    # Enregistrer les donnÃ©es dans le fichier CSV    # N'ecrit pas les donnees mock dans le CSV
    if is_mock_data_used():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        current_time = save_crypto_balance(token_balance)
    
    # Calculer la zakat
    gold_price, zakat_amount, msg, counter = calcul_zakat(total, gold_price)
    
    # CrÃ©er une nouvelle variable avec Ã©volution
    token_balance_dict_evol = token_balance.copy()
    evolution_dict = calculate_evolution()
    
    # Fusionner les deux dictionnaires pour le template
    for token, balance in token_balance_dict_evol.items():
        evolution = evolution_dict.get(token)
        if evolution is not None:
            evolution = round(evolution, 2)  # Arrondi Ã  deux chiffres aprÃ¨s la virgule
        token_balance_dict_evol[token] = {
            'balance': balance,
            'evolution': evolution
        }
    
    # CrÃ©er le graphique
    makePlot()
    
    # Rendre le template HTML
    return render_template('index.html', 
                          total=total, 
                          token_balance=token_balance_dict_evol, 
                          token_price=token_price,
                          token_mc=token_mc, 
                          zakat=zakat_amount,
                          counter=counter,
                          msg=msg,
                          goldPrice=gold_price,
                          current_time=current_time)

@app.route('/api/portfolio', methods=['GET'])
def api_portfolio():
    """
    Route API pour rÃ©cupÃ©rer les donnÃ©es du portefeuille (format JSON)
    """
    # Mettre Ã  jour les donnÃ©es
    total, token_balance, token_price, token_mc, gold_price = update_data()
    
    # Enregistrer les donnÃ©es dans le fichier CSV    # N'ecrit pas les donnees mock dans le CSV
    if is_mock_data_used():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        current_time = save_crypto_balance(token_balance)
    
    # Calculer la zakat
    gold_price, zakat_amount, msg, counter = calcul_zakat(total, gold_price)
    
    # Nouvelle variable avec Ã©volution
    token_balance_dict_evol = token_balance.copy()
    evolution_dict = calculate_evolution()
    
    # Fusionner les deux dictionnaires pour l'API
    for token, balance in token_balance_dict_evol.items():
        evolution = evolution_dict.get(token)
        if evolution is not None:
            evolution = round(evolution, 2)  # Arrondi Ã  deux chiffres aprÃ¨s la virgule
        token_balance_dict_evol[token] = {
            'balance': balance,
            'evolution': evolution
        }
    
    # CrÃ©er le graphique
    makePlot()
    
    # CrÃ©er la rÃ©ponse JSON
    response = {
        'total': total,
        'token_balance': token_balance_dict_evol,
        'token_price': token_price,
        'token_mc': token_mc,
        'zakat': zakat_amount,
        'counter': counter,
        'msg': msg,
        'goldPrice': gold_price,
        'current_time': current_time
    }
    
    return jsonify(response)

def run_schedule():
    """
    Fonction pour exÃ©cuter les tÃ¢ches planifiÃ©es
    """
    while True:
        schedule.run_pending()
        time.sleep(36000)  # Attendre une heure entre chaque vÃ©rification

def create_app():
    """
    Fonction pour crÃ©er et configurer l'application Flask
    """
    # DÃ©marrer le thread pour les tÃ¢ches planifiÃ©es
    t = threading.Thread(target=run_schedule)
    t.daemon = True  # Le thread s'arrÃªtera quand le programme principal s'arrÃªte
    t.start()
    
    return app

# Point d'entrÃ©e pour l'exÃ©cution directe
if __name__ == '__main__':
    app = create_app()
    app.run(
        host=FLASK_CONFIG['HOST'],
        port=FLASK_CONFIG['PORT'],
        debug=FLASK_CONFIG['DEBUG']
    )

