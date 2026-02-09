"""
Module pour la visualisation des données
"""
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from .config import DATA_FILE, PLOT_FILE

def makePlot():
    """
    Crée un graphique d'évolution des cryptomonnaies
    """
    # S'assurer que le répertoire existe
    os.makedirs(os.path.dirname(PLOT_FILE), exist_ok=True)
    
    # Lire les données CSV
    df = pd.read_csv(DATA_FILE)
    
    # Pivoter la table pour avoir les dates en index et les cryptomonnaies en colonnes
    df_pivot = df.pivot_table(index='Date', columns='Crypto', values='Valeur')
    
    # Ajuster la taille de la figure
    plt.figure(figsize=(15, 10))
    
    # Changer le style du graphique en mode sombre
    plt.style.use('dark_background')
    
    # Créer le graphique d'évolution
    plt.figure(figsize=(15, 7))
    plt.plot(df_pivot, marker='', linewidth=1.5)
    plt.title('Evolution of Cryptocurrency Values Over Time')
    plt.xlabel('Date')
    plt.ylabel('Valeur $')
    plt.legend(df_pivot.columns, loc='upper left')
    
    # Personnaliser les étiquettes de l'axe X
    x_ticks = df_pivot.index
    step = max(len(x_ticks) // 5, 1)  # Afficher une étiquette tous les 5 dates ou ajuster selon les besoins
    plt.xticks(range(0, len(x_ticks), step), x_ticks[::step], rotation=-90)
    plt.xticks(rotation=-90)
    
    # Supprimer le quadrillage
    plt.grid(False)
    
    # Utiliser tight_layout pour ajuster les paramètres du subplot
    plt.tight_layout()
    
    # Sauvegarder la figure
    plt.savefig(PLOT_FILE, bbox_inches='tight', pad_inches=0.5)
    
    # Fermer la figure pour libérer la mémoire
    plt.close()

def calculate_evolution():
    """
    Calcule l'évolution en pourcentage des cryptomonnaies sur les dernières 24 heures
    """
    # Lire les données CSV
    df = pd.read_csv(DATA_FILE, parse_dates=['Date'])
    
    # Obtenir l'heure actuelle et l'heure il y a 24 heures
    now = datetime.now()
    day_ago = now - timedelta(days=1)
    
    # Filtrer le DataFrame pour les dernières 24 heures
    df_last_24h = df[(df['Date'] <= now) & (df['Date'] > day_ago)]
    
    # Obtenir la dernière valeur pour chaque crypto
    latest_values = df[df['Date'] <= now].groupby('Crypto')['Valeur'].last()
    
    # Obtenir les valeurs d'il y a 24 heures pour chaque crypto
    values_24h_ago = df_last_24h.groupby('Crypto')['Valeur'].first()
    
    # Calculer l'évolution en pourcentage
    evolution = ((latest_values - values_24h_ago) / values_24h_ago) * 100
    
    # Retourner le résultat sous forme de dictionnaire
    return evolution.dropna().to_dict()

def find_date_threshold(threshold):
    """
    Trouve la date à laquelle le total du portefeuille était inférieur à un certain seuil
    """
    # Lire les données CSV
    df = pd.read_csv(DATA_FILE, parse_dates=['Date'])
    
    # Calculer le total par date
    total_per_date = df.groupby('Date')['Valeur'].sum()
    
    # Trier le DataFrame par index (dates)
    df_sorted = total_per_date.sort_index(ascending=False)
    date_find = None
    
    # Trouver la première date où la valeur est inférieure au seuil
    for date, value in df_sorted.items():
        if value < (threshold * 89):
            date_str = date.strftime("%Y-%m-%d %H:%M:%S")
            date_find = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            break  # Arrêter la boucle dès que la condition est vérifiée
    
    return date_find
