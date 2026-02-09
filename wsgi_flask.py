# Ce fichier est utilisé par PythonAnywhere pour démarrer votre application Flask
import sys
import os

# Ajoutez le chemin vers votre application
path = '/home/Saad44/mysite'
if path not in sys.path:
    sys.path.append(path)

# Importez votre application Flask
from backend.app import create_app

# Créez l'application Flask
application = create_app()

# Alias pour compatibilité avec certaines configurations WSGI
app = application
