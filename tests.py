 # Based on https://dev.to/paurakhsharma/flask-rest-api-part-6-testing-rest-apis-4lla

import unittest
import json

# Ughhhh, ik haat testen schrijven
# from app import app
# from database.db import db

from app import create_app, db
from sqlalchemy import func
from app.models import *
from flask_testing import TestCase
from app.auth.routes import register_user_func


class BaseCase(TestCase):

    def create_app(self):
        return create_app()

    def setUp(self):

        User.query.filter(User.id >= 45).delete()
        db.session.commit()

        user_id = register_user_func("TEST_max_user_id", "firstname", "lastname", "password")
        self.assertTrue(user_id)  # When this assertion gets triggered, you should remove any TEST_* user from your db
        self.max_user_id = user_id
        pass

    def tearDown(self):
        # Delete all new made users
        User.query.filter(User.id >= self.max_user_id).delete()
        db.session.commit()
        pass


class AuthenticationTest(BaseCase):

    def help_register(self, username, firstname, lastname, password):
        payload = json.dumps({
            "username": username,
            "firstname": firstname,
            "lastname": lastname,
            "password": password
        })

        return self.client.post('/api/users/register', headers={"Content-Type": "application/json"}, data=payload)

    def help_login(self, username, password):
        payload = json.dumps({
            "username": username,
            "password": password
        })

        return self.client.post('/api/users/auth', headers={"Content-Type": "application/json"}, data=payload)

    def test_succesful_register(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")

        self.assertEqual(201, response.status_code)
        self.assertEqual(self.max_user_id + 1, response.json.get("id"))

    def test_register_username_already_taken(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        self.assertEqual(401, response.status_code)

    def test_succesful_login(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        self.assertEqual(200, response.status_code)
        self.assertEqual(str, type(response.json.get("token")))

    def test_unsuccesful_login(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsNietCool69")
        self.assertEqual(401, response.status_code)

    def test_correct_token(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        #print(User.check_token(response.json.get("token")))
