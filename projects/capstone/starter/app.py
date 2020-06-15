import os
import sys
import subprocess
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db, Price, Stock, db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    setup_db(app)
    migrate = Migrate(app, db)

    return app

app = create_app()

@app.route('/')
def get_price():
    return jsonify({
      "price":db.session.query(Price.price).order_by(Price.id.desc()).first()[0]
    })



if __name__ == '__main__':
    p = subprocess.Popen([sys.executable, 'price_generator.py'])
    app.run(host='0.0.0.0', port=8080)