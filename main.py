from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json

app = FastAPI()

# Load the restaurant data from the JSON file
with open('/mnt/data/test.restaurants.json') as f:
    restaurants = json.load(f)

# Pydantic models for data validation
class MenuItem(BaseModel):
    name: str
    price: int

class Restaurant(BaseModel):
    id: str
    user: str
    restaurantName: str
    city: str
    country: str
    deliveryPrice: int
    estimatedDeliveryTime: int
    cuisines: List[str]
    menuItems: List[MenuItem]
    imageUrl: str
    lastUpdated: str

# Endpoint to get all restaurants
@app.get("/restaurants", response_model=List[Restaurant])
def get_restaurants():
    return restaurants

# Endpoint to get a restaurant by ID
@app.get("/restaurants/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str):
    for restaurant in restaurants:
        if restaurant["_id"]["$oid"] == restaurant_id:
            return restaurant
    raise HTTPException(status_code=404, detail="Restaurant not found")

# Endpoint to search restaurants by city
@app.get("/restaurants/city/{city}", response_model=List[Restaurant])
def get_restaurants_by_city(city: str):
    result = [restaurant for restaurant in restaurants if restaurant["city"].lower() == city.lower()]
    return result

# Endpoint to search restaurants by cuisine
@app.get("/restaurants/cuisine/{cuisine}", response_model=List[Restaurant])
def get_restaurants_by_cuisine(cuisine: str):
    result = [restaurant for restaurant in restaurants if cuisine.lower() in (c.lower() for c in restaurant["cuisines"])]
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
