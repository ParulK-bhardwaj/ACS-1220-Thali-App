import datetime
from sqlalchemy_utils import URLType
from flask_login import UserMixin
from thali_app.extensions import db
from thali_app.utils import FormEnum
from datetime import datetime

class FoodCategory(FormEnum):
    """Categories of grocery items."""
    VEGETARIAN = 'Vegetarian'
    NONVEGETARIAN = 'Non-vegetarian'
    VEGAN = 'Vegan'
    OTHER = 'Other'

class City(db.Model):
    """City model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    region = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    short_desc = db.Column(db.String(500), nullable=False)
    dishes = db.relationship('Dish', back_populates='city')

    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User')

    def __str__(self):
        return f"{self.name}"
    
    def __repr__(self):
        return f"<{self.id}:{self.name}>"


class Dish(db.Model):
    """Dish model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    short_desc = db.Column(db.String(250), nullable=False)

    # The category - What category the dish relates to?
    category = db.Column(db.Enum(FoodCategory), default=FoodCategory.OTHER)

    photo_url = db.Column(URLType)
    where_to_eat = db.Column(db.String(80), nullable=False)

    rating = db.Column(db.Float, default=0)
    ratings = db.relationship('Rating', backref='dish')

    city_id = db.Column(
        db.Integer, db.ForeignKey('city.id'), nullable=False)
    city = db.relationship('City', back_populates='dishes')
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User')

    favorites_list_dishes = db.relationship(
        'User', secondary='user_favorites_list', back_populates='favorites_list_user')

    def __str__(self):
        return f"{self.name}"
    
    def __repr__(self):
        return f"<{self.id}:{self.name}>"

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
# many-to-many relationship between User and GroceryItem for the shopping list items that fixed the log in error. 
class User(UserMixin, db.Model):
    "User Model"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

    favorites_list_user = db.relationship(
        'Dish', secondary='user_favorites_list', back_populates='favorites_list_dishes')

    def __str__(self):
        return f"{self.username}"

    def __repr__(self):
        return f'<User: {self.username}>'

favorites_list_table = db.Table('user_favorites_list',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('dish_id', db.Integer, db.ForeignKey('dish.id'))
)
