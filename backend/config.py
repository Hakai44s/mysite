# Configuration du backend
import os


def load_dotenv(dotenv_path=".env"):
    """Charge un fichier .env simple sans dependance externe."""
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


load_dotenv()


def get_secret(key, default=""):
    """Lit un secret depuis l'env puis depuis st.secrets (Streamlit Cloud)."""
    value = os.getenv(key)
    if value:
        return value
    try:
        import streamlit as st

        secret_value = st.secrets.get(key, default)
        return str(secret_value) if secret_value is not None else default
    except Exception:
        return default

# Cles API et autres configurations (depuis variables d'environnement)
API_KEYS = {
    "etherscan": get_secret("ETHERSCAN_API_KEY", ""),
    "coinmarketcap": get_secret("CMC_API_KEY", ""),
}

# Cles API individuelles pour un acces plus facile
ETHERSCAN_API_KEY = API_KEYS["etherscan"]
CMC_API_KEY = API_KEYS["coinmarketcap"]

# Adresse du portefeuille
MY_WALLET = get_secret("MY_WALLET", "")

# Chemins des fichiers
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
DATA_FILE = os.path.join(STATIC_DIR, "data_crypto.csv")
PLOT_FILE = os.path.join(STATIC_DIR, "plot_evol.png")

# Configuration de l'application Flask
FLASK_CONFIG = {
    "DEBUG": False,
    "HOST": "0.0.0.0",
    "PORT": 5000,
}

# Configuration de l'application Streamlit
STREAMLIT_CONFIG = {
    "PORT": 8501,
    "ADDRESS": "0.0.0.0",
    "HEADLESS": True,
}

# Utiliser des donnees simulees en cas de blocage des API par le pare-feu d'entreprise
# Mettre a True pour utiliser les donnees simulees, False pour utiliser les API reelles
USE_MOCK_DATA = False
