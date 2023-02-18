import os
import unittest
import app

from datetime import date
from thali_app.extensions import app, db, bcrypt
from thali_app.models import City, Dish, User, FoodCategory

"""
Run these tests with the command:
python -m unittest thali_app.main.tests
"""

#################################################
# Setup
#################################################

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def create_cities():
    # Creates cities
    u1 = User(username='me1', password='password')
    c1 = City(
        name='Udaipur',
        state='Rajasthan',
        region="North-West",
        country="India",
        created_by=u1
    )
    db.session.add(c1)

    u2 = User(username='Yes Sir', password='password')
    c2 = City(
        name='Jaipur',
        state='Rajasthan',
        region="North-West",
        country="India",
        created_by=u2
    )
    db.session.add(c2)
    db.session.commit()

def create_user():
    # Creates a user with username 'me1' and password of 'password'
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class MainTests(unittest.TestCase):
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
 
    def test_homepage_logged_out(self):
        """Test that the Cities show up on the homepage."""
        # Set up
        create_cities()
        create_user()

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Udaipur', response_text)
        self.assertIn('Rajasthan', response_text)
        self.assertIn('India', response_text)
        self.assertIn('Log In', response_text)
        self.assertIn('Sign Up', response_text)

        # Check that the page doesn't contain things we don't expect
        # (these should be shown only to logged in users)
        self.assertNotIn('Create City', response_text)
        self.assertNotIn('Create Dish', response_text)
 
    def test_homepage_logged_in(self):
        """Test that the books show up on the homepage."""
        # Set up
        create_cities()
        create_user()
        login(self.app, 'me1', 'password')

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Udaipur', response_text)
        self.assertIn('Jaipur', response_text)
        self.assertIn('New City', response_text)
        self.assertIn('New Dish', response_text)

        # Check that the page doesn't contain things we don't expect
        # (these should be shown only to logged out users)
        self.assertNotIn('Log In', response_text)
        self.assertNotIn('Sign Up', response_text)

    def test_city_detail_logged_out(self):
        """Test that the book appears on its detail page."""
        # Use helper functions to create cities, user
        create_cities()
        create_user()

        # Make a GET request to the URL /login, check to see that the
        # status code is 200
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_city_detail_logged_in(self):
        """Test that the City appears on its detail page."""
        # Use helper functions to create books, authors, user, & to log in
        create_cities()
        create_user()
        login(self.app, 'me1', 'password')

        #  Make a GET request to the URL /city/1, check to see that the
        # status code is 200
        response = self.app.get('/city/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Check that the response contains the book's title, publish date,
        # and author's name
        response_text = response.get_data(as_text=True)
        # self.assertIn("<h1>City - Udaipur</h1>", response_text)
        # self.assertIn("Rajasthan", response_text)
        # # self.assertIn("North-West", response_text)
        # self.assertIn("India", response_text)
        # # self.assertIn("me1", response_text)
        # # #  Check that the response contains the 'Favorite' button
        # # self.assertIn("Add to list", response_text)
    pass

    def test_update_city(self):
        """Test updating a city."""
        # Set up
        create_cities()
        create_user()
        login(self.app, 'me1', 'password')

        # Make POST request with data
        post_data = {
            'name': 'Jodhpur',
            'state': 'Rajasthan',
            'region': "",
            'country': "India",
            'created_by_id': 2,
        }
        self.app.post('/city/1', data=post_data)
        
        # Make sure the city was updated as we'd expect
        city = City.query.get(1)
        self.assertEqual(city.name, 'Jodhpur')
        self.assertEqual(city.state, 'Rajasthan')
        self.assertEqual(city.region, '')

    def test_new_city(self):
        """Test creating a book."""
        # Set up
        create_cities()
        create_user()
        login(self.app, 'me1', 'password')

        # Make POST request with data
        post_data = {
            'name': 'Udaipur',
            'state': 'Rajasthan',
            'region': "North-West",
            'country': "India",
            'created_by': 1,
        }
        self.app.post('/new_city', data=post_data)

        # Make sure city was updated as we'd expect
        created_city = City.query.filter_by(name='Udaipur').one()
        self.assertIsNotNone(created_city)
        self.assertEqual(created_city.state, 'Rajasthan')
        self.assertEqual(created_city.created_by.username, 'me1')

    def test_new_city_logged_out(self):
        """
        Test that the user is redirected when trying to access the new city
        route if not logged in.
        """
        # Set up
        create_cities()
        create_user()

        # Make GET request
        response = self.app.get('/create_book')

        # Make sure that the user was redirecte to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?next=%2Fcreate_book', response.location)

    def test_create_author(self):
        """Test creating an author."""
        # Create a user & login (so that the user can access the route)
        """Test updating an author."""
        # Set up
        create_user()
        login(self.app, 'me1', 'password')

        # Make POST request with data
        post_data = {
            'name': 'Yuval Noah Harrari',
            'biography': 'author of the book sapiens'
        }
        self.app.post('/create_author', data=post_data)

        # Make sure author was updated as we'd expect
        created_author = Author.query.filter_by(name='Yuval Noah Harrari').one()
        self.assertIsNotNone(created_author)
        # Verify that the author was updated in the database
        self.assertEqual(created_author.name, 'Yuval Noah Harrari')

    def test_create_genre(self):
        # Create a user & login (so that the user can access the route)
                # Set up
        create_user()
        login(self.app, 'me1', 'password')

        post_data = {
            'name': 'non-fiction'
        }

        self.app.post('/create_genre', data=post_data)
        # Make GET request
        created_genre = Genre.query.filter_by(name='non-fiction').one()
        self.assertIsNotNone(created_genre)
        # Verify that the author was updated in the database
        self.assertEqual(created_genre.name, 'non-fiction')

    def test_profile_page(self):
        # Make a GET request to the /profile/me1 route
        create_user()
        login(self.app, 'me1', 'password')
        # Verify that the response shows the appropriate user info
        response = self.app.get('/profile/me1')
        self.assertEqual(response.status_code, 200)
        response_text = response.get_data(as_text=True)
        self.assertIn("me1", response_text)

    def test_favorite_book(self):
        # Login as the user me1
        create_cities()
        create_user()
        login(self.app, 'me1', 'password')
        #  Make a POST request to the /favorite/2 route
        post_data = {
            'book_id': 2
        }
        response = self.app.post('/favorite/2', data=post_data)
        #  Verify that the book with id 2 was added to the user's favorites
        user = User.query.filter_by(username='me1').one()
        book = Book.query.get(2)
        self.assertIn(book, user.favorite_books)

    def test_unfavorite_book(self):
        # Login as the user me1, and add book with id 1 to me1's favorites
        create_cities()
        create_user()
        login(self.app, 'me1', 'password')
        #  Make a POST request to the /unfavorite/2 route
        post_data = {
            'book_id': 2
        }
        response = self.app.post('/unfavorite/2', data=post_data)
        #  Verify that the book with id 2 was removed from the user's favorites
        user = User.query.filter_by(username='me1').one()
        book = Book.query.get(2)
        self.assertNotIn(book, user.favorite_books)

