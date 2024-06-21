from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_mongoengine import MongoEngine
import stripe
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Use a secure key here
app.config['MONGODB_SETTINGS'] = {
    'host': os.getenv('MONGODB_CONNECTION_STRING', 'mongodb+srv://akamranshelvin:9JsDmQSkQyXOHPoY@mern-food-delivery-app.3pzi8tj.mongodb.net/?retryWrites=true&w=majority&appName=Mern-food-delivery-app')
}

# Initialize JWT Manager and MongoEngine
jwt = JWTManager(app)
db = MongoEngine(app)

# Stripe configuration
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', 'sk_test_51PSyfKFQpmwDMxbNY99dDObf8CfPcWkt5aaHBN51skNPi1aAj9MT1Y59pPBJCMrWwcaSrOOa49VmLAPXwU2SUo8L002o7T6lqj')
stripe.api_key = STRIPE_API_KEY
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
STRIPE_ENDPOINT_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_9244c1a3251cffca855858ccf588fb82d72b32ab20e1b253dd3b3c32c4e943fb')

# Models
class Restaurant(db.Document):
    user = db.ObjectIdField(required=True)
    restaurantName = db.StringField()
    city = db.StringField()
    country = db.StringField()
    deliveryPrice = db.FloatField()
    estimatedDeliveryTime = db.StringField()
    cuisines = db.ListField(db.StringField())
    menuItems = db.ListField(db.DictField())
    imageUrl = db.StringField()
    lastUpdated = db.DateTimeField()

class Order(db.Document):
    restaurant = db.ReferenceField(Restaurant)
    user = db.ObjectIdField()
    status = db.StringField()
    deliveryDetails = db.DictField()
    cartItems = db.ListField(db.DictField())
    createdAt = db.DateTimeField()
    totalAmount = db.FloatField()

@app.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    try:
        user_id = get_jwt_identity()
        orders = Order.objects(user=user_id).select_related()
        return jsonify([order.to_json() for order in orders]), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'something went wrong'}), 500

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook_handler():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        return jsonify({'message': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'message': 'Invalid signature'}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order = Order.objects(id=session['metadata']['orderId']).first()
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        order.totalAmount = session['amount_total']
        order.status = 'paid'
        order.save()

    return '', 200

@app.route('/checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        restaurant = Restaurant.objects(id=data['restaurantId']).first()
        if not restaurant:
            raise ValueError("Restaurant not found")

        new_order = Order(
            restaurant=restaurant,
            user=user_id,
            status='placed',
            deliveryDetails=data['deliveryDetails'],
            cartItems=data['cartItems'],
            createdAt=datetime.datetime.utcnow()
        )

        line_items = create_line_items(data['cartItems'], restaurant.menuItems)

        session = create_session(line_items, str(new_order.id), restaurant.deliveryPrice, str(restaurant.id))
        if not session.url:
            return jsonify({'message': 'Error creating stripe session'}), 500

        new_order.save()
        return jsonify({'url': session.url}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': str(e)}), 500

def create_line_items(cart_items, menu_items):
    line_items = []
    for cart_item in cart_items:
        menu_item = next((item for item in menu_items if str(item['_id']) == cart_item['menuItemId']), None)
        if not menu_item:
            raise ValueError(f"Menu item not found: {cart_item['menuItemId']}")
        line_items.append({
            'price_data': {
                'currency': 'gbp',
                'unit_amount': int(menu_item['price'] * 100),
                'product_data': {
                    'name': menu_item['name'],
                },
            },
            'quantity': int(cart_item['quantity']),
        })
    return line_items

def create_session(line_items, order_id, delivery_price, restaurant_id):
    session = stripe.checkout.Session.create(
        line_items=line_items,
        shipping_options=[
            {
                'shipping_rate_data': {
                    'display_name': 'Delivery',
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': int(delivery_price * 100),
                        'currency': 'gbp',
                    },
                },
            },
        ],
        mode='payment',
        metadata={
            'orderId': order_id,
            'restaurantId': restaurant_id,
        },
        success_url=f"{FRONTEND_URL}/order-status?success=true",
        cancel_url=f"{FRONTEND_URL}/detail/{restaurant_id}?cancelled=true",
    )
    return session

if __name__ == '__main__':
    app.run(debug=True)
