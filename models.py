from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class DeliveryDetails(Base):
    __tablename__ = 'delivery_details'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    addressLine1 = Column(String, nullable=False)
    city = Column(String, nullable=False)

class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, index=True)
    menuItemId = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    delivery_details_id = Column(Integer, ForeignKey('delivery_details.id'))
    cart_items = relationship("CartItem", cascade="all, delete-orphan")
    totalAmount = Column(Integer)
    status = Column(Enum("placed", "paid", "inProgress", "outForDelivery", "delivered"), default="placed")
    createdAt = Column(DateTime, default=datetime.utcnow)

class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    restaurant = relationship("Restaurant", back_populates="menu_items")

class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    restaurantName = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    deliveryPrice = Column(Float, nullable=False)
    estimatedDeliveryTime = Column(Integer, nullable=False)
    imageUrl = Column(String, nullable=False)
    lastUpdated = Column(DateTime, default=datetime.utcnow, nullable=False)
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
