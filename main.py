import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))

from peoject import create_flask_app
from common.setting.pro import ProConfault

app = create_flask_app(ProConfault)

if __name__ == '__main__':
    app.run()