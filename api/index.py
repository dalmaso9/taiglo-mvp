import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api-gateway', 'src'))

from vercel_app import app

# Para compatibilidade com Vercel
if __name__ == '__main__':
    app.run()
