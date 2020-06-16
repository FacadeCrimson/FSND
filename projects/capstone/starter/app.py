import os
import sys
import subprocess
import requests
from datetime import datetime
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

from auth import requires_auth, sign_up, log_in, verify_decode_jwt
from models import setup_db, Price, Stock, Trader, db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    setup_db(app)
    migrate = Migrate(app, db)

    return app

app = create_app()

# Get a list of latest prices for all the stocks
# Permission required: none
@app.route('/price')
def get_price():
    query = db.session.query(Price).distinct(Price.code).order_by(Price.code,Price.id.desc()).all()
    values = {x.code:x.price for x in query}
    return jsonify(values)

# Get a list of latest prices for all the stocks on a certain exchange
# Permission required: none
@app.route('/exchange/<exchange_id>/price')
def exchange_get_price(exchange_id):
    query = db.session.query(Price).join(Stock).filter(Stock.market_id==exchange_id)\
      .distinct(Price.code).order_by(Price.code,Price.id.desc()).all()
    values = {x.code:x.price for x in query}
    return jsonify(values)

# Register as trader by providing name, email and password
# Permission required: none
@app.route('/register', methods=['POST'])
def register():
    req = request.get_json()
    email = req['email']
    password = req['password']
    name = req['name']
    id = sign_up(email,password)['_id']
    try:
        trader = Trader(id = id, name = name, email = email, cash = 10000)
        trader.insert()
    except:
        abort(422)
    return jsonify({
      "success":True
    })

@app.route('/login', methods=['POST'])
def login():
    req = request.get_json()
    email = req['email']
    password = req['password']
    try:
        token = log_in(email, password)['access_token']
        payload = verify_decode_jwt(token)
        id = payload["sub"][6:]
        trader = Trader.query.get(id)
    except:
        abort(403)
    return f'''
    Hello {trader.name}!
    You have {trader.cash} dollars in your account.
    '''

# Buy a certain stock
# Permission required: trade:stock
@app.route('/buy', methods=['POST'])
@requires_auth('trade:stock')
def buy_stock(jwt):
    req = request.get_json()
    shares = req['shares']
    code = req['code']
    return jsonify({
      "success":True
    })

# Sell a certain stock
# Permission required: trade:stock
@app.route('/sell', methods=['POST'])
@requires_auth('trade:stock')
def sell_stock():
    return jsonify({
      "success":True
    })

# List a new stock
# Permission required: list:stock
@app.route('/list', methods=['POST'])
def list_stock():
    req = request.get_json()
    try:
        exchange = req['exchange']
        price = req['price']
        name = req['name']
        code = req['code']
        stock = Stock(code = code, name = name, market_id = exchange)
        stock.insert()
        price = Price(code = code, price = price, timestamp = datetime.now())
        price.insert()
    except:
        abort(400)
    return jsonify({
      "success":True
    })

# Unlist a stock
# Permission required: unlist:stock
@app.route('/stock/<stock_code>', methods=['DELETE'])
def unlist_stock(stock_code):
    stock = Stock.query.get(stock_code)
    try:
        stock.delete()
    except:
        abort(422)
    return jsonify({
      "success":True
    })

# Modify a stock's name or exchange
# Permission required: modify:stock
@app.route('/stock/<stock_code>', methods=['PATCH'])
def modify_stock(stock_code):
    stock = Stock.query.get(stock_code)
    req = request.get_json()
    try:
        name = req['name']
        exchange = req['exchange']
        stock.name = name
        stock.market_id = exchange
        stock.update()
    except:
        abort(400)
    return jsonify({
      "success":True
    })

## Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

@app.errorhandler(500)
def internal(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found"
    }), 404

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422

if __name__ == '__main__':
    p = subprocess.Popen([sys.executable, 'price_generator.py'])
    app.run(host='0.0.0.0', port=8080)