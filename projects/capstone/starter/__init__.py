import subprocess
import sys
from app import app


if __name__ == '__main__':
    p = subprocess.Popen([sys.executable, 'price_generator.py'])
    app.run(host='0.0.0.0', port=8080)