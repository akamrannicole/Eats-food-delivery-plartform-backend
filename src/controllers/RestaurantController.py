from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_mongoengine import MongoEngine
import os
import re

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Use a secure key here
app.config['MONGODB_SETTINGS'] = {
    'host': os.getenv('MONGODB_CONNECTION_STRING', 'mongodb+srv://akamranshelvin:9JsDmQSkQyXOHPoY@mern-food-delivery-app.3pzi8tj.mongodb.net/?retryWrites=true&w=majority&appName=Mern-food-delivery-app')
}

# Initialize JWT Manager and MongoEngine
jwt = JWTManager(app)
db = MongoEngine(app)

# Models
class Restaurant(db.Document):
    restaurantName = db.StringField()
    city = db.StringField()
    country = db.StringField()
    deliveryPrice = db.FloatField()
    estimatedDeliveryTime = db.StringField()
    cuisines = db.ListField(db.StringField())
    menuItems = db.ListField(db.DictField())
    imageUrl = db.StringField()
    lastUpdated = db.DateTimeField()

@app.route('/restaurant/<restaurantId>', methods=['GET'])
def get_restaurant(restaurantId):
    try:
        restaurant = Restaurant.objects(id=restaurantId).first()
        if not restaurant:
            return jsonify({'message': 'restaurant not found'}), 404
        return jsonify(restaurant.to_json()), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'something went wrong'}), 500

@app.route('/restaurants/<city>', methods=['GET'])
def search_restaurant(city):
    try:
        search_query = request.args.get('searchQuery', '')
        selected_cuisines = request.args.get('selectedCuisines', '')
        sort_option = request.args.get('sortOption', 'lastUpdated')
        page = int(request.args.get('page', 1))

        query = {}

        query['city'] = re.compile(city, re.IGNORECASE)
        city_check = Restaurant.objects(**query).count()
        if city_check == 0:
            return jsonify({
                'data': [],
                'pagination': {
                    'total': 0,
                    'page': 1,
                    'pages': 1,
                },
            }), 404

        if selected_cuisines:
            cuisines_array = [re.compile(cuisine, re.IGNORECASE) for cuisine in selected_cuisines.split(',')]
            query['cuisines'] = {'$all': cuisines_array}

        if search_query:
            search_regex = re.compile(search_query, re.IGNORECASE)
            query['$or'] = [
                {'restaurantName': search_regex},
                {'cuisines': {'$in': [search_regex]}},
            ]

        page_size = 10
        skip = (page - 1) * page_size

        restaurants = Restaurant.objects(**query).order_by(sort_option).skip(skip).limit(page_size)
        total = Restaurant.objects(**query).count()

        response = {
            'data': [restaurant.to_json() for restaurant in restaurants],
            'pagination': {
                'total': total,
                'page': page,
                'pages': (total + page_size - 1) // page_size,
            },
        }

        return jsonify(response), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True)
