from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

class RestaurantResource(Resource):

    def get(self, restaurant_id):
        
        if not restaurant_id or not isinstance(restaurant_id, str):
            return {'message': 'RestaurantId parameter must be a valid string'}, 400

        # Implement get restaurant logic
        return {'message': f'Get restaurant with id: {restaurant_id}'}

class SearchRestaurantResource(Resource):

    def get(self, city):
        # Validate city (similar to express-validator)
        if not city or not isinstance(city, str):
            return {'message': 'City parameter must be a valid string'}, 400

        # Implement search restaurant logic
        return {'message': f'Search restaurants in city: {city}'}

# Routes definition
api.add_resource(RestaurantResource, '/api/restaurant/<string:restaurant_id>')
api.add_resource(SearchRestaurantResource, '/api/restaurant/search/<string:city>')

if __name__ == '__main__':
    app.run(debug=True)
