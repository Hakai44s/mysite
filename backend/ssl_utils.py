"""
Utilitaires pour gérer les problèmes SSL dans les requêtes HTTP
"""
import os
import requests
import urllib3
import warnings
import ssl

def disable_ssl_warnings():
    """
    Désactive les avertissements liés aux certificats SSL
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def configure_ssl_context():
    """
    Configure un contexte SSL moins strict pour les environnements
    avec des problèmes de certificats
    """
    try:
        # Créer un contexte SSL moins strict
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Appliquer ce contexte à urllib3
        urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        urllib3.util.ssl_.DEFAULT_CIPHERS = urllib3.util.ssl_.DEFAULT_CIPHERS.replace('!3DES:', '')
        
        return ctx
    except Exception as e:
        print(f"Erreur lors de la configuration du contexte SSL: {e}")
        return None

def create_ssl_unverified_session():
    """
    Crée une session requests qui ne vérifie pas les certificats SSL
    """
    session = requests.Session()
    session.verify = False
    return session

def set_ssl_environment():
    """
    Configure les variables d'environnement pour désactiver la vérification SSL
    """
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['SSL_CERT_FILE'] = ''

def setup_insecure_environment():
    """
    Configure l'environnement pour ignorer les problèmes de certificats SSL
    À utiliser uniquement en développement ou dans des environnements contrôlés
    """
    disable_ssl_warnings()
    set_ssl_environment()
    return create_ssl_unverified_session()
