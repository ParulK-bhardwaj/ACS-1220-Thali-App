from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, PasswordField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, URL
# from wtforms.fields.html5  import DateField
from thali_app.models import *
from thali_app.extensions import bcrypt


class CityForm(FlaskForm):
    """Form for adding/updating a City."""
    name = StringField("City Name",
        validators=[
            DataRequired(),
            Length(min=3, max=80, message="The city name needs to be between 3 and 80 chars")
        ])
    state = StringField("State",
            validators=[
            Length(min=0, max=80, message="The state name needs to be between 3 and 80 chars")
        ])
    region = StringField("Region",
            validators=[
            Length(min=0, max=80, message="The region name needs to be between 3 and 80 chars")
        ])
    country = StringField("Country",
        validators=[
        Length(min=3, max=80, message="The country name needs to be between 3 and 80 chars")
    ])
    short_desc = StringField("Short Description",
        validators=[
            Length(min=0, max=250, message= "The description needs to be less than 250 charcaters")
    ])
    submit = SubmitField("Submit")

class DishForm(FlaskForm):
    """Form for adding/updating a Dish."""
    name = StringField("Dish Name",
        validators=[
            DataRequired(),
            Length(min=3, max=80, message= "The dish name needs to be between 3 to 80 charcaters")
    ])
    short_desc = StringField("Short Description",
        validators=[
            Length(min=0, max=250, message= "The description needs to be less than 250 charcaters")
    ])
    category = SelectField("Category", choices=FoodCategory.choices())
    photo_url = StringField("Photo URL")
    where_to_eat = StringField("Where to Eat",
        validators=[
            Length(min=0, max=250, message= "The name needs to be less than 250 charcaters")
    ])
    city = QuerySelectField("City",
        query_factory=lambda: City.query, allow_blank=False)
    submit = SubmitField("Submit")