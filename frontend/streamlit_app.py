"""
Application Streamlit principale pour le front-end
"""
import os
import sys
import streamlit as st

# Ajout du chemin parent pour l'importation des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.config import UI_CONFIG
from frontend.auth import require_password
from frontend.api import get_portfolio_data
from frontend.ui import (
    setup_page_config,
    apply_custom_style,
    display_portfolio_summary,
    display_crypto_table,
    display_charts,
    display_error_message,
)

setup_page_config(UI_CONFIG)
apply_custom_style()
require_password()

with st.sidebar:
    st.header("Options")
    if st.button("Se deconnecter"):
        st.session_state["auth_ok"] = False
        st.rerun()

    if st.button("Rafraichir les donnees"):
        st.cache_data.clear()
        st.rerun()

    st.subheader("Navigation")
    st.info("Page actuelle: Dashboard")

    st.subheader("A propos")
    st.markdown(
        """
    Cette application suit votre portefeuille de cryptomonnaies.

    Elle affiche:
    - Le total du portefeuille
    - Les details de chaque cryptomonnaie
    - L'evolution des valeurs
    - Le calcul de la zakat
    - Une page Trading Binance
    """
    )

data = get_portfolio_data()

if data:
    display_portfolio_summary(data)
    display_crypto_table(data)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(project_root, "static", "data_crypto.csv")
    plot_file = os.path.join(project_root, "static", "plot_evol.png")
    display_charts(data_file, plot_file)
else:
    display_error_message()
