import os
import sys
import subprocess
import requests
from datetime import datetime
from flask import Flask, request, abort, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import and_

from auth import requires_auth, sign_up, log_in, verify_decode_jwt, auth_and_get_trader
from models import setup_db, Price, Stock, Trader, Possession, db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.secret_key = os.urandom(16)
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
    name = req['name']
    email = req['email']
    password = req['password']
    id = sign_up(email,password)['_id']
    try:
        trader = Trader(id = id, name = name, email = email, cash = 10000)
        trader.insert()
    except:
        abort(422)
    return jsonify({
      "success":True
    })

# Log in with email and password
# Permission required: none
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
        session['token'] = token
        stocks = Possession.query.filter(Possession.trader_id == id)
    except:
        abort(403)
    message = f'''
    Hello {trader.name}!
    You have {trader.cash} dollars in your account.

    '''
    for stock in stocks:
        message = message + f"You have {stock.position} shares of {stock.stock_code}.\n"
    return message

# Log out
# Permission required: none
@app.route('/logout')
def logout():
    session.pop('token', None)
    return "Successfully logged out!"

# Buy a certain stock
# Permission required: trade:stock
@app.route('/buy', methods=['POST'])
@auth_and_get_trader('trade:stock')
def buy_stock(id, jwt):
    req = request.get_json()
    shares = req['shares']
    code = req['code']
    trader = Trader.query.get(id)
    stock = Stock.query.get(code)
    cash = trader.cash
    price = Price.query.filter(Price.code == code)\
      .order_by(Price.id.desc()).first()
    result = cash - shares * price.price
    if result < 0:
        return "Sorry, you have insufficient fund."
    else:
        trader.cash = result
        poss = Possession(position = shares)
        poss.stock = stock
        poss.trader = trader
        poss.insert()
        trader.stocks.append(poss)
    return f"You have successfully acquired {shares} shares of stock {code}."

# Sell a certain stock
# Permission required: trade:stock
@app.route('/sell', methods=['POST'])
@auth_and_get_trader('trade:stock')
def sell_stock(id, jwt):
    req = request.get_json()
    shares = req['shares']
    code = req['code']
    position = db.session.query(Possession).\
      filter(and_(Possession.trader_id == id, Possession.stock_code == code)).first()
    if not position or position.position < shares:
        return "Sorry, you have insufficient stocks."

    trader = Trader.query.get(id)
    stock = Stock.query.get(code)
    price = Price.query.filter(Price.code == code)\
      .order_by(Price.id.desc()).first()
    new_position = position.position - shares

    if new_position == 0:
        position.delete()
    trader.cash = trader.cash + price.price * shares
    position.position = new_position
    db.session.commit()
    return f"You have successfully sold {shares} shares of stock {code}."

# List a new stock
# Permission required: list:stock
@app.route('/list', methods=['POST'])
@requires_auth('list:stock')
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
@requires_auth('unlist:stock')
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
@requires_auth('modify:stock')
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