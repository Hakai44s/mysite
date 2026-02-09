"""
Module pour le calcul de la zakat
"""
from datetime import datetime
from .visualization import find_date_threshold

def calcul_zakat(total, gold_price):
    """
    Calcule la zakat en fonction du total du portefeuille et du prix de l'or
    
    Args:
        total (float): Total du portefeuille en USD
        gold_price (float): Prix de l'or en USD
        
    Returns:
        tuple: (prix de l'or, montant de la zakat, message, jours écoulés)
    """
    zakat_amount = 0
    
    # Trouver la date à laquelle le seuil a été atteint
    first_time_nissab = find_date_threshold(gold_price)
    
    if first_time_nissab:
        counter = datetime.now() - first_time_nissab
        days_passed = counter.days
    else:
        days_passed = 0
    
    # Calculer le montant de la zakat (2.5% du total)
    zakat_amount = round(0.025 * total, 2)
    
    # Déterminer si c'est le moment de payer la zakat
    if days_passed % 365 == 0 and days_passed > 0:
        msg = "Paye"
    else:
        msg = "Pas encore le moment de payer"
    
    return gold_price, zakat_amount, msg, days_passed
