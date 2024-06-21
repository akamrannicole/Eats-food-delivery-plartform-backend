from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from mongoengine import Document, StringField, connect
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Use a secure key here

# Initialize JWT Manager
jwt = JWTManager(app)

# Connect to MongoDB
connect(host=os.getenv('MONGODB_CONNECTION_STRING', 'mongodb+srv://akamranshelvin:9JsDmQSkQyXOHPoY@mern-food-delivery-app.3pzi8tj.mongodb.net/?retryWrites=true&w=majority&appName=Mern-food-delivery-app'))

# Models
class User(Document):
    auth0Id = StringField(required=True, unique=True)
    name = StringField()
    addressLine1 = StringField()
    country = StringField()
    city = StringField()

@app.route('/current-user', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        current_user = User.objects(id=user_id).first()
        if not current_user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify(current_user.to_json()), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Something went wrong'}), 500

@app.route('/current-user', methods=['POST'])
def create_current_user():
    try:
        data = request.get_json()
        auth0Id = data.get('auth0Id')
        existing_user = User.objects(auth0Id=auth0Id).first()

        if existing_user:
            return '', 200

        new_user = User(**data)
        new_user.save()

        return jsonify(new_user.to_json()), 201
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error creating user'}), 500

@app.route('/current-user', methods=['PUT'])
@jwt_required()
def update_current_user():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        name = data.get('name')
        addressLine1 = data.get('addressLine1')
        country = data.get('country')
        city = data.get('city')

        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        user.name = name
        user.addressLine1 = addressLine1
        user.city = city
        user.country = country

        user.save()

        return jsonify(user.to_json()), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error updating user'}), 500

if __name__ == '__main__':
    app.run(debug=True)
