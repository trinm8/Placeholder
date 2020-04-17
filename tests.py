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
        # Delete all new made users, the others should be deleted with the cascade policy
        User.query.filter(User.id >= self.max_user_id).delete()
        db.session.commit()
        pass

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

    def help_add_route(self, from_coords, to_coords, passenger_places, arrive_by):
        payload = json.dumps({
            "from": from_coords,
            "to": to_coords,
            "passenger-places": passenger_places,
            "arrive-by": arrive_by
        })

        return self.client.post('/api/drives', headers={"Content-Type": "application/json"}, data=payload)


class AuthenticationTest(BaseCase):

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
        user = User.check_token(response.json.get("token"))
        self.assertEqual(user.username, "TEST_MarkP")

    def test_incorrect_token(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        user = User.check_token(response.json.get("token"))
        self.assertNotEqual(user.username, "TEST_MarkP")

class RouteTest(BaseCase):
    def test_add_route(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        # TODO: tokens meegeven aan request? Driver id checken?
        self.assertEqual(id, response.json.get("driver-id"))
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00")
        self.assertEqual([51.130215, 4.571509], response.json.get("from"))
        self.assertEqual([51.18417, 4.41931], response.json.get("to"))
        self.assertEqual(3, response.json.get("passenger-places"))
        self.assertEqual("2020-02-12T10:00:00.00", response.json.get("arrive-by"))

    def test_add_route_missing_info(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], None, "2020-02-12T10:00:00.00")
        self.assertEqual(401, response.status_code)

    def test_add_route_no_login(self):
        # TODO: fix failing test with tokens
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00")
        self.assertEqual(401, response.status_code)

    def test_delete_route(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00")
        id = response.json.get("id")

        self.assertNotEqual(None, Route.query.get(id))
        response = self.client.delete('/api/drives/' + str(id), headers={"Content-Type": "application/json"})
        self.assertEqual(None, Route.query.get(id))

    def test_update_route(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00")
        id = response.json.get("id")

        payload = json.dumps({
            "passenger-places": 4
        })

        self.assertEqual(3, response.json.get("passenger-places"))
        response = self.client.put('/api/drives/{id}'.format(id=id), headers={"Content-Type": "application/json"}, data=payload)
        self.assertEqual(4, response.json.get("passenger-places"))
        self.assertEqual(201, response.status_code)

    def test_read_route(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00")
        id = response.json.get("id")
        response = self.client.get('/api/drives/{id}'.format(id=id), headers={"Content-Type": "application/json"})
        self.assertEqual([51.130215, 4.571509], response.json.get("from"))
        self.assertEqual([51.18417, 4.41931], response.json.get("to"))
        self.assertEqual(3, response.json.get("passenger-places"))
        self.assertEqual("2020-02-12T10:00:00.00", response.json.get("arrive-by"))