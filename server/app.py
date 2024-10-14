#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError, DataError
from marshmallow import Schema, fields, ValidationError
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Schemas for validation
class RestaurantPizzaSchema(Schema):
    price = fields.Int(required=True)
    pizza_id = fields.Int(required=True)
    restaurant_id = fields.Int(required=True)

restaurant_pizza_schema = RestaurantPizzaSchema()

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    return jsonify(restaurant.to_dict(include_pizzas=True))

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    json_data = request.get_json()

    try:
        data = restaurant_pizza_schema.load(json_data)
    except ValidationError as err:
        return jsonify(errors=["validation errors"]), 400

    restaurant_pizza = RestaurantPizza(
        price=data['price'],
        pizza_id=data['pizza_id'],
        restaurant_id=data['restaurant_id']
    )

    try:
        db.session.add(restaurant_pizza)
        db.session.commit()
    except (IntegrityError, DataError):
        db.session.rollback()
        return jsonify(errors=["validation errors"]), 400

    return jsonify(restaurant_pizza.to_dict()), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)
