"""
Module pour la rÃ©cupÃ©ration des donnÃ©es de cryptomonnaies
"""
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from .config import CMC_API_KEY, ETHERSCAN_API_KEY, API_KEYS, MY_WALLET, XRP_WALLET, USE_MOCK_DATA
from .utils import format_number
from coinmarketcapapi import CoinMarketCapAPI

# Delai entre les appels API Etherscan (plan FREE: 5 appels/seconde)
ETHERSCAN_API_DELAY = 0.25
HTTP_TIMEOUT = 8

# Fonction utilitaire pour crÃ©er une session sans vÃ©rification SSL
def create_ssl_unverified_session():
    session = requests.Session()
    session.verify = False
    return session

# Configuration Etherscan V2
ETHERSCAN_V2_URL = "https://api.etherscan.io/v2/api"
ETHERSCAN_CHAIN_ID = "1"

# Initialisation des clients API
cmc = CoinMarketCapAPI(CMC_API_KEY)

# Variables globales
TOTAL = 0
token_balance_dict = {}
token_price_dict = {}
token_mc_dict = {}
goldPrice = 0
zakat = 0
current_time = None
IS_MOCK_DATA = False
list_balance_token_usd = []
list_all_token = []
list_all_token_mc = []

def fetch_data(api_function, *args):
    """ExÃ©cute une fonction API de maniÃ¨re asynchrone"""
    with ThreadPoolExecutor() as executor:
        result = executor.submit(api_function, *args)
        return result.result()

def etherscan_v2_call(session, action, **params):
    """Appelle Etherscan V2 et renvoie la valeur de result."""
    query = {
        "chainid": ETHERSCAN_CHAIN_ID,
        "module": "account",
        "action": action,
        "apikey": ETHERSCAN_API_KEY,
    }
    query.update(params)
    response = session.get(ETHERSCAN_V2_URL, params=query, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "1":
        message = payload.get("message", "UNKNOWN")
        result = payload.get("result", "UNKNOWN")
        raise RuntimeError(f"Etherscan V2 error: {message} -- {result}")
    return payload["result"]

def get_token_balance_v2(session, address, contract_address, decimals):
    raw = etherscan_v2_call(
        session,
        "tokenbalance",
        address=address,
        contractaddress=contract_address,
        tag="latest",
    )
    return int(raw) / (10 ** decimals)

def get_eth_balance(wallet, verify_ssl=True):
    """RÃ©cupÃ¨re le solde ETH et sa valeur en USD"""
    try:
        session = requests.Session()
        session.verify = verify_ssl

        custom_cmc = CoinMarketCapAPI(CMC_API_KEY, session=session)
        eth = custom_cmc.cryptocurrency_quotes_latest(symbol="ETH", skip_invalid=False)
        eth_balance = int(
            etherscan_v2_call(session, "balance", address=wallet, tag="latest")
        ) / (10 ** 18)
        eth_price = float(eth.data['ETH'][0]['quote']['USD']['price'])
        eth_mc = format_number(eth.data['ETH'][0]['quote']['USD']['market_cap'])
        return eth_balance * eth_price, eth_price, eth_mc
    except Exception as e:
        print(f"Erreur lors de la rÃ©cupÃ©ration des donnÃ©es ETH: {e}")
        return 0, 0, "N/A"

def get_fet_balance(address, contract_address, verify_ssl=True):
    """RÃ©cupÃ¨re le solde FET et sa valeur en USD"""
    try:
        # Configuration de la session requests pour dÃ©sactiver la vÃ©rification SSL si nÃ©cessaire
        session = requests.Session()
        session.verify = verify_ssl

        # CrÃ©ation d'une nouvelle instance avec notre session personnalisÃ©e
        custom_cmc = CoinMarketCapAPI(CMC_API_KEY, session=session)

        # RÃ©cupÃ©ration du prix FET via CoinMarketCap
        fet = custom_cmc.cryptocurrency_quotes_latest(symbol="FET", skip_invalid=False)
        fet_price = fet.data['FET'][0]['quote']['USD']['price']
        fet_mc = format_number(fet.data['FET'][0]['quote']['USD']['market_cap'])

        fet_balance = get_token_balance_v2(session, address, contract_address, 18)

        return fet_price * fet_balance, fet_price, fet_mc
    except Exception as e:
        print(f"Erreur lors de la rÃ©cupÃ©ration des donnÃ©es FET: {e}")
        return 0, 0, "N/A"

def get_gala_balance(address, contract_address, verify_ssl=True):
    """RÃ©cupÃ¨re le solde GALA et sa valeur en USD"""
    try:
        # Configuration de la session requests pour dÃ©sactiver la vÃ©rification SSL si nÃ©cessaire
        session = requests.Session()
        session.verify = verify_ssl

        # CrÃ©ation d'une nouvelle instance avec notre session personnalisÃ©e
        custom_cmc = CoinMarketCapAPI(CMC_API_KEY, session=session)

        # RÃ©cupÃ©ration du prix GALA via CoinMarketCap
        gala = custom_cmc.cryptocurrency_quotes_latest(symbol="GALA", skip_invalid=False)
        gala_price = gala.data['GALA'][0]['quote']['USD']['price']
        gala_mc = format_number(gala.data['GALA'][0]['quote']['USD']['market_cap'])

        gala_balance = get_token_balance_v2(session, address, contract_address, 8)

        return gala_price * gala_balance, gala_price, gala_mc
    except Exception as e:
        print(f"Erreur lors de la rÃ©cupÃ©ration des donnÃ©es GALA: {e}")
        return 0, 0, "N/A"

def get_esx_balance(address, contract_address, verify_ssl=True):
    """RÃ©cupÃ¨re le solde ESX et sa valeur en USD"""
    try:
        # Configuration de la session requests pour dÃ©sactiver la vÃ©rification SSL si nÃ©cessaire
        session = requests.Session()
        session.verify = verify_ssl

        esx_balance = get_token_balance_v2(session, address, contract_address, 18)
        esx = cmc.cryptocurrency_quotes_latest(symbol="ESX", skip_invalid=False)
        esx_price = esx.data['ESX'][0]['quote']['USD']['price']
        esx_mc = format_number(esx.data['ESX'][0]['quote']['USD']['market_cap'])
        return esx_price * esx_balance, esx_price, esx_mc
    except Exception as e:
        print(f"Erreur lors de la rÃ©cupÃ©ration des donnÃ©es ESX: {e}")
        return 0, 0, "N/A"

def get_usd_balance(address, usdc_contract, usdt_contract, verify_ssl=True):
    """RÃ©cupÃ¨re le solde USD (USDC + USDT)"""
    try:
        # Configuration de la session requests pour dÃ©sactiver la vÃ©rification SSL si nÃ©cessaire
        session = requests.Session()
        session.verify = verify_ssl

        usdc_balance = get_token_balance_v2(session, address, usdc_contract, 6)
        usdt_balance = get_token_balance_v2(session, address, usdt_contract, 6)
        return usdc_balance + usdt_balance
    except Exception as e:
        print(f"Erreur lors de la rÃ©cupÃ©ration des donnÃ©es USD: {e}")
        return 0

def get_active_balance(verify_ssl=True):
    """RÃ©cupÃ¨re le solde actif sur Hyperliquid"""
    url = "https://api.hyperliquid.xyz/info"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "type": "clearinghouseState",
        "user": MY_WALLET
    }

    try:
        session = requests.Session()
        session.verify = verify_ssl
        response = session.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Erreur lors de la rÃ©cupÃ©ration des donnÃ©es actives: {e}")
        return 0

    if response.status_code == 200:
        response_data = response.json()
        account_value = response_data['marginSummary']['accountValue']
        account_value = float(account_value)
    else:
        print(f"Failed with status code {response.status_code}:")
        print(response.text)
        account_value = 0

    return account_value

def get_xrp_amount(verify_ssl=True):
    """Recupere le montant de XRP et sa valeur en USD"""
    try:
        session = requests.Session()
        session.verify = verify_ssl

        url = f"https://api.xrpscan.com/api/v1/account/{XRP_WALLET}"
        response = session.get(url, timeout=HTTP_TIMEOUT)

        if response.status_code != 200:
            print(f"Erreur lors de la recuperation des donnees XRP: {response.status_code}")
            return 0, 0, "N/A"

        data = response.json()

        # xrpscan expose souvent xrpBalance (XRP), et parfois Balance (drops).
        xrp_balance_raw = data.get('xrpBalance')
        if xrp_balance_raw is not None:
            xrp_balance = float(xrp_balance_raw)
        else:
            xrp_drops = float(data.get('Balance', 0))
            xrp_balance = xrp_drops / 1_000_000

        xrp_price = 0
        xrp_mc = "N/A"
        try:
            custom_cmc = CoinMarketCapAPI(CMC_API_KEY, session=session)
            xrp = custom_cmc.cryptocurrency_quotes_latest(symbol="XRP", skip_invalid=False)
            xrp_price = float(xrp.data['XRP'][0]['quote']['USD']['price'])
            xrp_mc = format_number(xrp.data['XRP'][0]['quote']['USD']['market_cap'])
        except Exception as cmc_error:
            print(f"Erreur CMC pour XRP, tentative fallback CoinGecko: {cmc_error}")
            try:
                cg = session.get(
                    "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd&include_market_cap=true",
                    timeout=HTTP_TIMEOUT,
                )
                if cg.status_code == 200:
                    cg_data = cg.json().get("ripple", {})
                    xrp_price = float(cg_data.get("usd", 0))
                    market_cap = cg_data.get("usd_market_cap")
                    if market_cap is not None:
                        xrp_mc = format_number(market_cap)
            except Exception as cg_error:
                print(f"Fallback CoinGecko XRP en erreur: {cg_error}")

        return xrp_balance * xrp_price, xrp_price, xrp_mc
    except Exception as e:
        print(f"Erreur lors de la recuperation des donnees XRP: {e}")
        return 0, 0, "N/A"

def fetch_data_with_GOLD(api_key, verify_ssl=True):
    """RÃ©cupÃ¨re le prix de l'or"""
    url = f"https://www.goldapi.io/api/XAU/USD"
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Erreur lors de la rÃ©cupÃ©ration des donnÃ©es de l'or: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Exception lors de la rÃ©cupÃ©ration des donnÃ©es de l'or: {e}")
        return None

def calculate_total():
    """Calcule le total du portefeuille et rÃ©cupÃ¨re toutes les donnÃ©es des cryptomonnaies"""
    global list_balance_token_usd, list_all_token, list_all_token_mc

    # RÃ©initialiser les listes
    list_balance_token_usd = []
    list_all_token = []
    list_all_token_mc = []
    list_token_price = []

    # RÃ©cupÃ©ration des donnÃ©es ETH
    eth_balance_usd, eth_price, eth_mc = get_eth_balance(MY_WALLET, verify_ssl=True)
    list_balance_token_usd.append(eth_balance_usd)
    list_all_token.append("ETH")
    list_token_price.append(eth_price)
    list_all_token_mc.append(eth_mc)

    # DÃ©lai pour respecter la limite d'API Etherscan
    time.sleep(ETHERSCAN_API_DELAY)

    # RÃ©cupÃ©ration des donnÃ©es FET
    fet_contract = "0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85"
    fet_balance_usd, fet_price, fet_mc = get_fet_balance(MY_WALLET, fet_contract, verify_ssl=True)
    list_balance_token_usd.append(fet_balance_usd)
    list_all_token.append("FET")
    list_token_price.append(fet_price)
    list_all_token_mc.append(fet_mc)

    # DÃ©lai pour respecter la limite d'API Etherscan
    time.sleep(ETHERSCAN_API_DELAY)

    # RÃ©cupÃ©ration des donnÃ©es GALA
    gala_contract = "0xd1d2Eb1B1e90B638588728b4130137D262C87cae"
    gala_balance_usd, gala_price, gala_mc = get_gala_balance(MY_WALLET, gala_contract, verify_ssl=True)
    list_balance_token_usd.append(gala_balance_usd)
    list_all_token.append("GALA")
    list_token_price.append(gala_price)
    list_all_token_mc.append(gala_mc)

    # DÃ©lai pour respecter la limite d'API Etherscan
    time.sleep(ETHERSCAN_API_DELAY)

    # RÃ©cupÃ©ration des donnÃ©es ESX
    esx_contract = "0xFC05987bd2be489ACCF0f509E44B0145d68240f7"
    esx_balance_usd, esx_price, esx_mc = get_esx_balance(MY_WALLET, esx_contract, verify_ssl=True)
    list_balance_token_usd.append(esx_balance_usd)
    list_all_token.append("ESX")
    list_token_price.append(esx_price)
    list_all_token_mc.append(esx_mc)

    # DÃ©lai pour respecter la limite d'API Etherscan
    time.sleep(ETHERSCAN_API_DELAY)

    # RÃ©cupÃ©ration des donnÃ©es USD
    usdc_contract = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    usdt_contract = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    usd_balance = get_usd_balance(MY_WALLET, usdc_contract, usdt_contract, verify_ssl=True)
    list_balance_token_usd.append(usd_balance)
    list_all_token.append("USD")
    list_token_price.append(1)
    list_all_token_mc.append("N/A")

    # DÃ©lai pour respecter la limite d'API Etherscan
    time.sleep(ETHERSCAN_API_DELAY)

    # RÃ©cupÃ©ration des donnÃ©es XRP
    xrp_balance_usd, xrp_price, xrp_mc = get_xrp_amount(verify_ssl=True)
    list_balance_token_usd.append(xrp_balance_usd)
    list_all_token.append("XRP")
    list_token_price.append(xrp_price)
    list_all_token_mc.append(xrp_mc)

    # DÃ©lai pour respecter la limite d'API
    time.sleep(ETHERSCAN_API_DELAY)

    # RÃ©cupÃ©ration des donnÃ©es de solde actif
    active_balance = get_active_balance(verify_ssl=True)
    list_balance_token_usd.append(active_balance)
    list_all_token.append("ACTIVE")
    list_token_price.append(1)
    list_all_token_mc.append("N/A")

    # Calcul du total
    total = sum(list_balance_token_usd)

    # CrÃ©ation des dictionnaires
    token_balance_dict = dict(zip(list_all_token, list_balance_token_usd))
    token_price_dict = dict(zip(list_all_token, list_token_price))
    token_mc_dict = dict(zip(list_all_token, list_all_token_mc))

    # RÃ©cupÃ©ration du prix de l'or (pas d'utilisation d'API pour test)
    goldPrice = 69.28

    return total, token_balance_dict, token_price_dict, token_mc_dict, goldPrice

def get_mock_data():
    """Retourne des donnees mock pour les tests locaux."""
    token_balance = {
        "ETH": 1240.50,
        "FET": 430.25,
        "GALA": 87.40,
        "ESX": 65.10,
        "USD": 520.00,
        "XRP": 301.75,
        "ACTIVE": 190.00,
    }
    token_price = {
        "ETH": 3100.0,
        "FET": 1.42,
        "GALA": 0.029,
        "ESX": 0.41,
        "USD": 1.0,
        "XRP": 0.62,
        "ACTIVE": 1.0,
    }
    token_mc = {
        "ETH": "N/A",
        "FET": "N/A",
        "GALA": "N/A",
        "ESX": "N/A",
        "USD": "N/A",
        "XRP": "N/A",
        "ACTIVE": "N/A",
    }
    total = sum(token_balance.values())
    gold_price = 69.28
    return total, token_balance, token_price, token_mc, gold_price

def update_data():
    """Met a jour toutes les donnees du portefeuille."""
    global TOTAL, token_balance_dict, token_price_dict, token_mc_dict, goldPrice, IS_MOCK_DATA

    if USE_MOCK_DATA:
        TOTAL, token_balance_dict, token_price_dict, token_mc_dict, goldPrice = get_mock_data()
        IS_MOCK_DATA = True
        print('Donnees mock chargees.')
        return TOTAL, token_balance_dict, token_price_dict, token_mc_dict, goldPrice

    try:
        TOTAL, token_balance_dict, token_price_dict, token_mc_dict, goldPrice = calculate_total()
        IS_MOCK_DATA = False
    except Exception as exc:
        print(f'Erreur API detectee, fallback sur donnees mock: {exc}')
        TOTAL, token_balance_dict, token_price_dict, token_mc_dict, goldPrice = get_mock_data()
        IS_MOCK_DATA = True

    print('Donnees mises a jour!')
    return TOTAL, token_balance_dict, token_price_dict, token_mc_dict, goldPrice

def is_mock_data_used():
    """Indique si le dernier update_data() a utilise des donnees mock."""
    return IS_MOCK_DATA
