"""
Module pour la recuperation directe des donnees backend
"""
import streamlit as st
from backend.crypto_data import update_data, is_mock_data_used
from backend.utils import save_crypto_balance
from backend.zakat import calcul_zakat
from backend.visualization import makePlot, calculate_evolution


@st.cache_data(ttl=300)
def get_portfolio_data():
    """Recupere les donnees du portefeuille en appelant directement le backend."""
    try:
        total, token_balance, token_price, token_mc, gold_price = update_data()

        if is_mock_data_used():
            current_time = ""
        else:
            current_time = save_crypto_balance(token_balance)

        gold_price, zakat_amount, msg, counter = calcul_zakat(total, gold_price)

        token_balance_dict_evol = token_balance.copy()
        evolution_dict = calculate_evolution()
        for token, balance in token_balance_dict_evol.items():
            evolution = evolution_dict.get(token)
            if evolution is not None:
                evolution = round(evolution, 2)
            token_balance_dict_evol[token] = {
                "balance": balance,
                "evolution": evolution,
            }

        makePlot()

        return {
            "total": total,
            "token_balance": token_balance_dict_evol,
            "token_price": token_price,
            "token_mc": token_mc,
            "zakat": zakat_amount,
            "counter": counter,
            "msg": msg,
            "goldPrice": gold_price,
            "current_time": current_time,
        }
    except Exception as e:
        st.error(f"Erreur de recuperation des donnees: {e}")
        return None
