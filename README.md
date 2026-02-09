# Mon Portefeuille Crypto

Application Streamlit pour suivre un portefeuille crypto, visualiser l'evolution des soldes et estimer la zakat.

L'application est maintenant en mode **backend integre**:
- pas d'API Flask externe necessaire
- Streamlit appelle directement les modules Python du dossier `backend/`

## Stack
- Streamlit
- Pandas / Plotly / Matplotlib
- Requests
- APIs externes (Etherscan v2, CoinMarketCap, XRPSCAN, Hyperliquid)

## Structure
```text
mysite/
|- backend/
|  |- config.py
|  |- crypto_data.py
|  |- utils.py
|  |- visualization.py
|  |- zakat.py
|- frontend/
|  |- config.py
|  |- api.py              # appelle directement backend/* (sans HTTP)
|  |- ui.py
|  |- streamlit_app.py    # point d'entree Streamlit
|- static/
|  |- data_crypto.csv
|  |- plot_evol.png
|- template/
|- requirements.txt
|- README.md
```

## Installation locale
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

## Lancer l'application
```bash
streamlit run frontend/streamlit_app.py
```

Puis ouvrir l'URL affichee par Streamlit (souvent `http://localhost:8501`).

## Deploiement Streamlit Community Cloud
1. Pousser le repo sur GitHub.
2. Aller sur https://share.streamlit.io
3. New app -> choisir le repo `Hakai44s/mysite`
4. Branch: `main`
5. Main file path: `frontend/streamlit_app.py`
6. Deploy

## Notes
- Les donnees mock ne sont plus ecrites dans `static/data_crypto.csv`.
- Le calcul peut prendre quelques dizaines de secondes selon la latence des APIs externes.
- Si une API externe est lente/indisponible, certaines lignes peuvent revenir a 0 temporairement.

## Secrets et configuration

### Local (.env)
1. Copier `.env.example` en `.env`
2. Remplir les valeurs:
```env
ETHERSCAN_API_KEY=...
CMC_API_KEY=...
MY_WALLET=0x...
```

Le fichier `.env` est ignore par git.

### Streamlit Community Cloud
Pour le runtime Streamlit, utilise **App settings > Secrets** (pas GitHub Secrets):
```toml
ETHERSCAN_API_KEY = "..."
CMC_API_KEY = "..."
MY_WALLET = "0x..."
```

### GitHub Secrets
Les GitHub Secrets sont utilises pour GitHub Actions CI/CD, pas directement par l'application Streamlit en execution.
