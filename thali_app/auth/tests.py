import os
from unittest import TestCase
import app

from thali_app.extensions import app, db, bcrypt
from thali_app.models import City, User

"""
Run these tests with the command:
python3 -m unittest thali_app.auth.tests
"""

#################################################
# Setup
#################################################

def create_cities():
    # Creates cities
    u1 = User(username='me1', password='password')
    c1 = City(
        name='Udaipur',
        state='Rajasthan',
        region="North-West",
        country="India",
        short_desc="ABC",
        created_by=u1
    )
    db.session.add(c1)

    u2 = User(username='Yes Sir', password='password')
    c2 = City(
        name='Jaipur',
        state='Rajasthan',
        region="North-West",
        country="India",
        short_desc="DEF",
        created_by=u2
    )
    db.session.add(c2)
    db.session.commit()

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        # Write a test for the signup route. It should:
        # - Make a POST request to /signup, sending a username & password
        post_data = {
            'username': 'parul',
            'password': 'password123'
        }
        self.app.post('/signup', data=post_data)
        # - Check that the user now exists in the database
        response = self.app.get('/login')
        response_text = response.get_data(as_text=True)
        self.assertIn('login', response_text)

    def test_signup_existing_user(self):
        # - Create a user
        create_user()
        # - Make a POST request to /signup, sending the same username & password
        post_data = {
            'username': 'me1',
            'password': 'password'
        }
        response = self.app.post('/signup', data=post_data)
        # - Check that the form is displayed again with an error message
        response_text = response.get_data(as_text=True)
        self.assertIn('That username is taken. Please choose a different one.', response_text)

    def test_login_correct_password(self):
        # - Create a user
        create_user()
        # - Make a POST request to /login, sending the created username & password
        post_data = {
            'username': 'me1',
            'password': 'password'
        }
        response = self.app.post('/login', data=post_data)
        # - Check that the "login" button is not displayed on the homepage
        response = self.app.get('/')
        response_text = response.get_data(as_text=True)
        self.assertNotIn('login', response_text)

    def test_login_nonexistent_user(self):
        # - Make a POST request to /login, sending a username & password
        post_data = {
            'username': 'WhatIsThis',
            'password': 'GONE'
        }
        response = self.app.post('/login', data=post_data)
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        response_text = response.get_data(as_text=True)
        self.assertIn('No user with that username. Please try again.', response_text)

    def test_login_incorrect_password(self):
        # - Create a user
        create_user()
        # - Make a POST request to /login, sending the created username &
        #   an incorrect password
        post_data = {
            'username': 'me1',
            'password': 'Really!!'
        }
        response = self.app.post('/login', data=post_data)
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        response_text = response.get_data(as_text=True)
        self.assertIn('Password doesn&#39;t match. Please try again.', response_text)

    def test_logout(self):
        # - Create a user
        create_user()
        # - Log the user in (make a POST request to /login)
        post_data = {
            'username': 'me1',
            'password': 'password'
        }
        self.app.post('/login', data=post_data)
        # - Make a GET request to /logout
        self.app.get('/logout')
        # - Check that the "login" button appears on the homepage
        response = self.app.get('/')
        response_text = response.get_data(as_text=True)
        self.assertIn('login', response_text)