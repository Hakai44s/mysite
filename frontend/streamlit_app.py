"""
Application Streamlit principale pour le front-end
"""
import hmac
import os
import sys
import streamlit as st

# Ajout du chemin parent pour l'importation des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.config import UI_CONFIG
from frontend.api import get_portfolio_data
from frontend.ui import (
    setup_page_config,
    apply_custom_style,
    display_portfolio_summary,
    display_crypto_table,
    display_charts,
    display_error_message,
)


def _read_dotenv_value(key):
    """Lit une cle simple dans .env pour les executions locales."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(project_root, ".env")
    if not os.path.exists(dotenv_path):
        return ""

    with open(dotenv_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            env_key, env_value = line.split("=", 1)
            if env_key.strip() != key:
                continue
            return env_value.strip().strip('"').strip("'")
    return ""


def _get_app_password():
    """Priorite: st.secrets -> variable d'environnement -> .env local."""
    secret_value = ""
    try:
        secret_value = st.secrets.get("APP_PASSWORD", "")
    except Exception:
        pass
    if secret_value:
        return str(secret_value)

    env_value = os.getenv("APP_PASSWORD", "")
    if env_value:
        return env_value

    return _read_dotenv_value("APP_PASSWORD")


def require_password():
    """Bloque l'application tant que l'authentification n'est pas valide."""
    app_password = _get_app_password()
    if not app_password:
        st.error(
            "APP_PASSWORD non configure. Ajoute APP_PASSWORD dans Streamlit Secrets (cloud) "
            "ou dans .env (local)."
        )
        st.stop()

    if st.session_state.get("auth_ok", False):
        return

    st.markdown("## Acces protege")
    with st.form("password_form", clear_on_submit=False):
        entered_password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Entrer")
    if submitted:
        if hmac.compare_digest(entered_password, app_password):
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()


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

    st.subheader("A propos")
    st.markdown(
        """
    Cette application suit votre portefeuille de cryptomonnaies.

    Elle affiche:
    - Le total du portefeuille
    - Les details de chaque cryptomonnaie
    - L'evolution des valeurs
    - Le calcul de la zakat
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
