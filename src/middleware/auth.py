from flask import Flask, request, jsonify
from functools import wraps
from flask_jwt_extended import JWTManager
from flask_mongoengine import MongoEngine
from authlib.jose import jwt, jwk
import os
import requests

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Use a secure key here
app.config['MONGODB_SETTINGS'] = {
    'host': os.getenv('MONGODB_CONNECTION_STRING', 'mongodb+srv://akamranshelvin:9JsDmQSkQyXOHPoY@mern-food-delivery-app.3pzi8tj.mongodb.net/?retryWrites=true&w=majority&appName=Mern-food-delivery-app')
}

# Initialize JWT Manager and MongoEngine
jwt_manager = JWTManager(app)
db = MongoEngine(app)

# Models
class User(db.Document):
    auth0Id = db.StringField(required=True)
    # other fields...

# Helper function to get the JWKS keys from Auth0
def get_jwks():
    jwks_url = f"{os.getenv('AUTH0_ISSUER_BASE_URL')}.well-known/jwks.json"
    response = requests.get(jwks_url)
    return response.json()

# Decorator to check JWT and parse user information
def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get('Authorization', None)

        if not authorization or not authorization.startswith('Bearer '):
            return jsonify({"msg": "Missing Authorization Header"}), 401

        token = authorization.split(' ')[1]

        try:
            # Get JWKS keys
            jwks = get_jwks()
            public_keys = {k['kid']: jwk.loads(k) for k in jwks['keys']}

            # Decode token header to get the kid
            header = jwt.decode_header(token)
            kid = header.get('kid')

            if kid not in public_keys:
                return jsonify({"msg": "Invalid token"}), 401

            key = public_keys[kid]
            decoded = jwt.decode(token, key)

            auth0_id = decoded['sub']
            user = User.objects(auth0Id=auth0_id).first()

            if not user:
                return jsonify({"msg": "User not found"}), 401

            # Set user details in request context
            request.user = user
            request.auth0_id = auth0_id

            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"msg": "Invalid token"}), 401

    return wrapper

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify(logged_in_as=request.user.auth0Id), 200

if __name__ == '__main__':
    app.run(debug=True)
