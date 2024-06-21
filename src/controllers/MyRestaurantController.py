from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from mongoengine import Document, StringField, FloatField, ListField, ReferenceField, DateTimeField, connect, ObjectIdField
import cloudinary
import cloudinary.uploader
import datetime
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Use a secure key here

# Initialize JWT Manager
jwt = JWTManager(app)

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dstr9nqte'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '493395658789882'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', 'X-o4eAKjl8pL_WZjFWb9CUWg4-E')
)

# Connect to MongoDB
connect(host=os.getenv('MONGODB_CONNECTION_STRING', 'mongodb+srv://akamranshelvin:9JsDmQSkQyXOHPoY@mern-food-delivery-app.3pzi8tj.mongodb.net/?retryWrites=true&w=majority&appName=Mern-food-delivery-app'))

# Models
class Restaurant(Document):
    user = ObjectIdField(required=True)
    restaurantName = StringField()
    city = StringField()
    country = StringField()
    deliveryPrice = FloatField()
    estimatedDeliveryTime = StringField()
    cuisines = ListField(StringField())
    menuItems = ListField(StringField())
    imageUrl = StringField()
    lastUpdated = DateTimeField(default=datetime.datetime.utcnow)

class Order(Document):
    restaurant = ReferenceField(Restaurant)
    user = ObjectIdField()
    status = StringField()

# Helper function to upload image
def upload_image(file):
    upload_result = cloudinary.uploader.upload(file)
    return upload_result['url']

@app.route('/my-restaurant', methods=['GET'])
@jwt_required()
def get_my_restaurant():
    try:
        user_id = get_jwt_identity()
        restaurant = Restaurant.objects(user=user_id).first()
        if not restaurant:
            return jsonify({'message': 'restaurant not found'}), 404
        return jsonify(restaurant.to_json()), 200
    except Exception as e:
        print("error", e)
        return jsonify({'message': 'Error fetching restaurant'}), 500

@app.route('/my-restaurant', methods=['POST'])
@jwt_required()
def create_my_restaurant():
    try:
        user_id = get_jwt_identity()
        existing_restaurant = Restaurant.objects(user=user_id).first()

        if existing_restaurant:
            return jsonify({'message': 'User restaurant already exists'}), 409

        image_url = upload_image(request.files['file'])
        data = request.form.to_dict()
        data['user'] = user_id
        data['imageUrl'] = image_url
        data['lastUpdated'] = datetime.datetime.utcnow()
        
        restaurant = Restaurant(**data)
        restaurant.save()
        
        return jsonify(restaurant.to_json()), 201
    except Exception as e:
        print(e)
        return jsonify({'message': 'Something went wrong'}), 500

@app.route('/my-restaurant', methods=['PUT'])
@jwt_required()
def update_my_restaurant():
    try:
        user_id = get_jwt_identity()
        restaurant = Restaurant.objects(user=user_id).first()

        if not restaurant:
            return jsonify({'message': 'restaurant not found'}), 404

        data = request.form.to_dict()
        for key, value in data.items():
            setattr(restaurant, key, value)
        restaurant.lastUpdated = datetime.datetime.utcnow()

        if 'file' in request.files:
            image_url = upload_image(request.files['file'])
            restaurant.imageUrl = image_url

        restaurant.save()
        return jsonify(restaurant.to_json()), 200
    except Exception as e:
        print("error", e)
        return jsonify({'message': 'Something went wrong'}), 500

@app.route('/my-restaurant/orders', methods=['GET'])
@jwt_required()
def get_my_restaurant_orders():
    try:
        user_id = get_jwt_identity()
        restaurant = Restaurant.objects(user=user_id).first()
        if not restaurant:
            return jsonify({'message': 'restaurant not found'}), 404

        orders = Order.objects(restaurant=restaurant.id).select_related()
        return jsonify([order.to_json() for order in orders]), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'something went wrong'}), 500

@app.route('/orders/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    try:
        user_id = get_jwt_identity()
        status = request.json.get('status')

        order = Order.objects(id=order_id).first()
        if not order:
            return jsonify({'message': 'order not found'}), 404

        restaurant = Restaurant.objects(id=order.restaurant.id).first()
        if str(restaurant.user.id) != user_id:
            return jsonify({'message': 'Unauthorized'}), 401

        order.status = status
        order.save()

        return jsonify(order.to_json()), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'unable to update order status'}), 500

if __name__ == '__main__':
    app.run(debug=True)
