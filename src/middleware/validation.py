from flask import Flask, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key

class MenuItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Menu item name is required")])
    price = FloatField('Price', validators=[DataRequired(message="Menu item price is required and must be a positive number"), NumberRange(min=0, message="Menu item price must be a positive number")])

class RestaurantForm(FlaskForm):
    restaurantName = StringField('Restaurant Name', validators=[DataRequired(message="Restaurant name is required")])
    city = StringField('City', validators=[DataRequired(message="City is required")])
    country = StringField('Country', validators=[DataRequired(message="Country is required")])
    deliveryPrice = FloatField('Delivery Price', validators=[DataRequired(message="Delivery price must be a positive number"), NumberRange(min=0, message="Delivery price must be a positive number")])
    estimatedDeliveryTime = IntegerField('Estimated Delivery Time', validators=[DataRequired(message="Estimated delivery time must be a positive integer"), NumberRange(min=0, message="Estimated delivery time must be a positive integer")])
    cuisines = FieldList(StringField('Cuisine', validators=[DataRequired(message="Cuisines array cannot be empty")]), validators=[DataRequired(message="Cuisines must be an array")])
    menuItems = FieldList(FormField(MenuItemForm), validators=[DataRequired(message="Menu items must be an array")])

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Name must be a string"), Length(min=1)])
    addressLine1 = StringField('Address Line 1', validators=[DataRequired(message="AddressLine1 must be a string"), Length(min=1)])
    city = StringField('City', validators=[DataRequired(message="City must be a string"), Length(min=1)])
    country = StringField('Country', validators=[DataRequired(message="Country must be a string"), Length(min=1)])

def handle_validation_errors(form):
    errors = []
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            errors.append({'field': fieldName, 'message': err})
    return errors

@app.route('/validate-user', methods=['POST'])
def validate_user():
    form = UserForm(request.form)
    if not form.validate():
        return jsonify({'errors': handle_validation_errors(form)}), 400
    return jsonify({'message': 'User data is valid'}), 200

@app.route('/validate-restaurant', methods=['POST'])
def validate_restaurant():
    form = RestaurantForm(request.form)
    if not form.validate():
        return jsonify({'errors': handle_validation_errors(form)}), 400
    return jsonify({'message': 'Restaurant data is valid'}), 200

if __name__ == '__main__':
    app.run(debug=True)
