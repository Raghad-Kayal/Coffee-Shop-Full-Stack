import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
import pprint
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def show_drinks():

    drinks = Drink.query.all()

    data = []
    for drink in drinks:
        data.append(drink.short())

    return jsonify({
        "success": True,
        "drinks": data
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_details(payload):
    drinks = Drink.query.all()
    data = []
    for drink in drinks:
        data.append(drink.long())

    return jsonify({
        "success": True,
        "drinks": data
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):

    body = request.get_json()

    try:
        recipe = body["recipe"]
        print(recipe)
        drink = Drink(title=body['title'], recipe=json.dumps(recipe))
        drink.insert()

    except:
        abort(400)

    return jsonify({
        "sucess": True,
        "result": drink.long()
    }), 200


@ app.route('/drinks/<int:id>', methods=['PATCH'])
@ requires_auth('patch:drinks')
def patch_drinks(payload, id):

    body = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    try:
        if 'title' in body:
            drink.title = body.get('title')

        if 'recipe' in body:
            recipe = body["recipe"]
            drink.recipe = json.dumps(recipe)

        drink.update()

    except:
        abort(400)

    return jsonify({
        "success": True,
        "drinks": drink.long()
    }), 200


@ app.route('/drinks/<int:id>', methods=['DELETE'])
@ requires_auth('delete:drinks')
def delete_drinks(payload, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    try:
        drink.delete()

    except:
        abort(400)

    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling


@ app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@ app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@ app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        'error': 400,
        "message": "Bad Request"
    }), 400


@ app.errorhandler(AuthError)
def Auth_Error(error):

    return jsonify({
        "success": False,
        "error": AuthError,
        "message": "authrization error"
    }), AuthError
