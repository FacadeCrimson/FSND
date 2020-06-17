import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES
@app.route('/drinks')
def drinks():
    drink=Drink.query.order_by(Drink.id).all()
    drinks=[x.short() for x in drink]
    return jsonify({
        "success": True,
        "drinks": drinks
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    drink=Drink.query.order_by(Drink.id).all()
    drinks=[x.long() for x in drink]
    return jsonify({
        "success": True,
        "drinks": drinks
    })

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    data=request.get_json()
    title,recipe=data['title'],data['recipe']
    drink=Drink(title=title,recipe=json.dumps(recipe))
    try:
        drink.insert()
        db.session.refresh(drink)
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })

@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def drink_change(jwt,drink_id):
    drink=Drink.query.filter(Drink.id==drink_id).one_or_none()
    if not drink:
        abort(404)
    data=request.get_json()
    title,recipe=data['title'],data['recipe']
    drink.title=title
    drink.recipe=json.dumps(recipe)
    temp_drink=drink.long()
    drink.update()
    return jsonify({
        "success": True,
        "drinks": [temp_drink]
    })

@app.route('/drinks/<int:drink_id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt,drink_id):
    drink=Drink.query.filter(Drink.id==drink_id).one_or_none()
    if not drink:
        abort(404)
    drink.delete()
    return jsonify({
        "success": True,
        "delete": drink_id
    })

## Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400

@app.errorhandler(500)
def internal(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
    }), 405

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


