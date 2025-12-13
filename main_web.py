import sys
import os
from wsgiref.simple_server import make_server
project_root = os.getcwd()
source_path = os.path.join(project_root, 'src', 'app')
sys.path.append(source_path)
from interface.web import main

if __name__ == '__main__':
    # Configuration du serveur
    app = main({})
    server = make_server('0.0.0.0', 6543, app)
    
    print(" Serveur Pyramid lancé sur http://localhost:6543")
    print(" Dépôt (Bob) : http://localhost:6543/depot")
    print(" Modération (Alice) : http://localhost:6543/moderation?user=alice")
    
    server.serve_forever()