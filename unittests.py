# Based on https://dev.to/paurakhsharma/flask-rest-api-part-6-testing-rest-apis-4lla

import unittest
import json

# Ughhhh, ik haat testen schrijven
# Ja tkan wa lastig zijn, maar tis beter da ge t toch doe ze
# from app import app
# from database.db import db

from app import create_app, db
from sqlalchemy import func
from flask import Response
from app.models import *
from flask_testing import TestCase
from app.auth.routes import register_user_func
from app.api.tokens import login_required

import requests


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

    def help_add_MusicPref(self, user_id, genre, likes, authorization):
        music = json.dumps({
            "user": user_id,
            "genre": genre,
            "likes": likes
        })
        data = json.dumps({
            "musicpref": music
        })
        return self.client.put('/api/user',
                                headers={"Content-Type": "application/json", "Authorization": authorization},
                                data=data)

    def help_add_route(self, from_coords, to_coords, passenger_places, arrive_by, authorization):
        payload = json.dumps({
            "from": from_coords,
            "to": to_coords,
            "passenger-places": passenger_places,
            "arrive-by": arrive_by
        })

        return self.client.post('/api/drives',
                                headers={"Content-Type": "application/json", "Authorization": authorization},
                                data=payload)

    def help_add_request(self, drive_id, authorization):
        payload = json.dumps({})
        return self.client.post('/api/drives/{}/passenger-requests'.format(str(drive_id)),
                                headers={"Content-Type": "application/json", "Authorization": authorization},
                                data=payload)

    def help_status_request(self, drive_id, user_id, action, authorization):
        payload = json.dumps({
            "action": action
        })
        return self.client.post('api/drives/{}/passenger-requests/{}'.format(str(drive_id), str(user_id)),
                                headers={"Content-Type": "application/json", "Authorization": authorization},
                                data=payload)

    def help_read_request(self, drive_id, authorization):
        return self.client.get('api/drives/{}/passenger-requests'.format(str(drive_id)),
                               headers={"Content-Type": "application/json", "Authorization": authorization})

    def help_delete_request(self, drive_id, user_id, authorization):
        return self.client.delete('api/drives/{}/passenger-requests/{}'.format(str(drive_id), str(user_id)),
                                  headers={"Content-Type": "application/json", "Authorization": authorization})

    def help_create_review(self, reviewee_id, score, text, authorization):
        payload = json.dumps({
            "reviewee_id": reviewee_id,
            "score": score,
            "review_text": text
        })
        return self.client.post('api/user/reviews',
                                headers={"Content-Type": "application/json", "Authorization": authorization},
                                data=payload)

    def help_delete_review(self, reviewee_id, authorization):
        return self.client.delete('api/user/reviews/{}'.format(str(reviewee_id)),
                                  headers={"Content-Type": "application/json", "Authorization": authorization})

    def help_read_review(self, reviewer_id, reviewee_id, authorization):
        return self.client.get('api/user/{}/reviews/{}'.format(str(reviewer_id), str(reviewee_id)),
                               headers={"Content-Type": "application/json", "Authorization": authorization})

    # @login_required
    # def help_dummy_func_expired(self):
    #     pass


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
        self.assertEqual(user.username(), "TEST_MarkP")

    def test_incorrect_token(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        user = User.check_token(response.json.get("token"))
        self.assertNotEqual(user.username(), "TEST_MarkP")

    # def test_expired_tokens(self):
    #     response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
    #     response = self.help_login("TEST_MarkP", "MarkIsCool420")
    #     user = User.check_token(response.json.get("token"))
    #     fastToken = Response('localhost:5000', headers={'Authorization': user.get_token(1)})
    #     mock = self.help_dummy_func_expired()
    #     decorated = login_required(mock)
    #     response = decorated(fastToken)
    #     assert not mock.called


class RouteTest(BaseCase):
    def test_add_route(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00",
                                       authorization)
        self.assertEqual(id, response.json.get("driver-id"))
        self.assertEqual([51.130215, 4.571509], response.json.get("from"))
        self.assertEqual([51.18417, 4.41931], response.json.get("to"))
        self.assertEqual(3, response.json.get("passenger-places"))
        self.assertEqual("2020-02-12T10:00:00.00", response.json.get("arrive-by"))

    def test_add_route_missing_info(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], None, "2020-02-12T10:00:00.00",
                                       authorization)
        self.assertEqual(401, response.status_code)

    def test_add_route_no_login(self):
        # TODO: fix failing test with tokens
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00", None)
        self.assertEqual(401, response.status_code)

    def test_delete_route(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00",
                                       authorization)
        id = response.json.get("id")

        self.assertNotEqual(None, Route.query.get(id))
        response = self.client.delete('/api/drives/' + str(id),
                                      headers={"Content-Type": "application/json", "Authorization": authorization})
        self.assertEqual(None, Route.query.get(id))

    def test_update_route(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        authorization = "Bearer {token}".format(token=response.json.get("token"))
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00",
                                       authorization)
        id = response.json.get("id")

        payload = json.dumps({
            "from": [51.130326, 4.571610]
        })

        self.assertEqual([51.130215, 4.571509], response.json.get("from"))
        response = self.client.put('/api/drives/{id}'.format(id=id),
                                   headers={"Content-Type": "application/json", "Authorization": authorization},
                                   data=payload)
        self.assertEqual([51.130326, 4.571610], response.json.get("from"))
        self.assertEqual(201, response.status_code)

    def test_read_route(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        authorization = "Bearer {token}".format(token=response.json.get("token"))
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00",
                                       authorization)
        id = response.json.get("id")
        response = self.client.get('/api/drives/{id}'.format(id=id),
                                   headers={"Content-Type": "application/json", "Authorization": authorization})
        self.assertEqual([51.130215, 4.571509], response.json.get("from"))
        self.assertEqual([51.18417, 4.41931], response.json.get("to"))
        self.assertEqual(3, response.json.get("passenger-places"))
        self.assertEqual("2020-02-12T10:00:00.00", response.json.get("arrive-by"))

    def test_search_route(self):
        self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)

        # 109012, Москва, Красная площадь, 7, Китай-Город Москва Россия -> Hilda Ramstraat 39 (not close enough)
        response = self.help_add_route([55.752465, 37.623040], [51.18852, 4.42173], 3, "2021-02-12T10:00:00.00",
                                       authorization)
        drive_id1 = response.json.get("id")

        # Bartstraat 26 -> Hilda Ramstraat 39 (what we're searching for)
        response = self.help_add_route([51.13731, 4.60960], [51.18852, 4.42173], 3, "2021-02-12T10:00:00.00",
                                       authorization)
        drive_id2 = response.json.get("id")

        # Marnixdreef (Lier) 51.137939, 4.594519 -> zijstraat van Hilda Ram (what we also want)
        response = self.help_add_route([51.13731, 4.60960], [51.188626, 4.421392], 3, "2021-02-12T10:00:00.00",
                                       authorization)
        drive_id3 = response.json.get("id")

        # Bartstraat 26 -> Hilda Ramstraat 39 (other date)
        response = self.help_add_route([51.13731, 4.60960], [51.18852, 4.42173], 3, "2021-02-13T10:00:00.00",
                                       authorization)
        drive_id4 = response.json.get("id")

        # -------------- ACTUAL TEST ----------------
        data = {"from": "{lat}, {long}".format(lat=51.13731, long=4.60960),
                "to": "{lat}, {long}".format(lat=51.18852, long=4.42173), "arrive-by": "2021-02-12T10:00:00.00",
                "limit": 3}
        data = {"from": "{lat}, {long}".format(lat=51.008930, long=4.645653),
                "to": "{lat}, {long}".format(lat=51.18852, long=4.42173), "arrive-by": "2021-02-12T10:00:00.00",
                "limit": 3}
        response = self.client.get('/api/drives/search'.format(id=id),
                                   headers={"Content-Type": "application/json", "Authorization": authorization},
                                   query_string=data)

        routes = response.json
        self.assertEqual(2, len(routes))

        # Deze 2 kunnen ook omgewisseld zijn
        self.assertEqual(drive_id2, routes[0].get("id"))
        self.assertEqual(drive_id3, routes[1].get("id"))


class RequestTest(BaseCase):

    def test_add_request(self):
        # Create driver
        self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)

        # Create route
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00",
                                       authorization)
        drive_id = response.json.get("id")

        # Create passenger
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        user_id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)

        # -------------- ACTUAL TEST ----------------
        response = self.help_add_request(drive_id, authorization)
        self.assertEqual(response.json.get("id"), user_id)
        self.assertEqual(response.json.get("username"), "TEST_MarkP")
        self.assertEqual(response.json.get("status"), "pending")
        self.assertIsNotNone(response.json.get("time-created"))

    def test_status_request(self):
        # Create driver
        self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token_d = response.json.get("token")
        authorization_d = "Bearer {token}".format(token=token_d)

        # Create route
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00",
                                       authorization_d)
        drive_id = response.json.get("id")

        # Create passenger
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        user_id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)

        # Create request
        self.help_add_request(drive_id, authorization)

        # Log in with driver
        # response = self.help_login("TEST_MarkD", "MarkIsCool420")
        # token_d = response.json.get("token")
        # authorization_d = "Bearer {token}".format(token=token_d)

        # -------------- ACTUAL TEST ----------------
        response = self.help_status_request(drive_id, user_id, "accept", authorization_d)
        # print(str(response.json))
        self.assertEqual(response.json.get("id"), user_id)
        self.assertEqual(response.json.get("username"), "TEST_MarkP")
        self.assertEqual(response.json.get("status"), "accepted")
        self.assertIsNotNone(response.json.get("time-created"))
        self.assertIsNotNone(response.json.get("time-updated"))

    def test_read_request(self):
        # Create driver
        self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token_d = response.json.get("token")
        authorization_d = "Bearer {token}".format(token=token_d)

        # Create route
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00",
                                       authorization_d)
        drive_id = response.json.get("id")

        # Create passenger
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        user_id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)

        # Create request
        self.help_add_request(drive_id, authorization)

        response = self.help_read_request(drive_id, authorization_d)
        # print(str(response.json))
        self.assertIsNotNone(response.json)

    def test_delete_request(self):
        # Create driver
        self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token_d = response.json.get("token")
        authorization_d = "Bearer {token}".format(token=token_d)

        # Create route
        response = self.help_add_route([51.130215, 4.571509], [51.18417, 4.41931], 3, "2020-02-12T10:00:00.00",
                                       authorization_d)
        drive_id = response.json.get("id")

        # Create passenger
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        user_id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)

        # Create request
        self.help_add_request(drive_id, authorization)

        response = self.help_delete_request(drive_id, user_id, authorization_d)

        route_request = RouteRequest.query.filter_by(route_id=drive_id, user_id=user_id).first()
        self.assertIsNone(route_request)


class UserTests(BaseCase):
    def test_update_user(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        authorization = "Bearer {token}".format(token=response.json.get("token"))

        payload = json.dumps({
            "email": "mark.peeters@gmail.com"
        })

        response = self.client.get('/api/user/{id}'.format(id=id),
                                   headers={"Content-Type": "application/json", "Authorization": authorization})

        self.assertEqual(None, response.json.get("email"))
        self.assertEqual("TEST_MarkP", response.json.get("username"))

        response = self.client.put('/api/user',
                                   headers={"Content-Type": "application/json", "Authorization": authorization},
                                   data=payload)
        self.assertEqual("mark.peeters@gmail.com", response.json.get("email"))
        self.assertEqual(201, response.status_code)

    def test_delete_user(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)

        self.assertNotEqual(None, User.query.get(id))
        response = self.client.delete('/api/user',
                                      headers={"Content-Type": "application/json", "Authorization": authorization})
        self.assertEqual(None, User.query.get(id))

    def test_update_musicPref(self):
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        id = response.json.get("id")
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        authorization = "Bearer {token}".format(token=response.json.get("token"))
        response = self.client.get('/api/user/{id}'.format(id=id),
                                   headers={"Content-Type": "application/json", "Authorization": authorization})

        self.assertEqual([], response.json.get("liked_genres"))
        self.assertEqual([], response.json.get("disliked_genres"))
        self.assertEqual("TEST_MarkP", response.json.get("username"))

        payload = json.dumps({
            "liked_genres": ["R&B", "Jazz"],
            "disliked_genres": ["Pop"]
        })

        response = self.client.put('/api/user',
                                   headers={"Content-Type": "application/json", "Authorization": authorization},
                                   data=payload)

        self.assertEqual(["R&B", "Jazz"], response.json.get("liked_genres"))
        self.assertEqual(["Pop"], response.json.get("disliked_genres"))

        self.assertEqual(201, response.status_code)


class ReviewTests(BaseCase):
    def test_create_review(self):
        # create Reviewer
        response = self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        reviewer_id = response.json.get("id")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token_d = response.json.get("token")
        authorization_d = "Bearer {token}".format(token=token_d)

        # create Reviewee
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        reviewee_id = response.json.get("id")

        # -------------- ACTUAL TEST ----------------
        response = self.help_create_review(reviewee_id, 4.5, "test", authorization_d)
        self.assertEqual(response.json.get("reviewer_id"), reviewer_id)
        self.assertEqual(response.json.get("reviewee_id"), reviewee_id)
        self.assertEqual(response.json.get("score"), 4.5)
        self.assertEqual(response.json.get("review_text"), "test")

    def test_update_review(self):
        # create Reviewer
        response = self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        reviewer_id = response.json.get("id")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token_d = response.json.get("token")
        authorization_d = "Bearer {token}".format(token=token_d)

        # create Reviewee
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        reviewee_id = response.json.get("id")

        # create Review
        response = self.help_create_review(reviewee_id, 4.5, "test", authorization_d)

        self.assertEqual(response.json.get("reviewer_id"), reviewer_id)
        self.assertEqual(response.json.get("reviewee_id"), reviewee_id)
        self.assertEqual(response.json.get("score"), 4.5)
        self.assertEqual(response.json.get("review_text"), "test")

        payload = json.dumps({
            "score": 5,
            "review_text": "good"
        })

        # -------------- ACTUAL TEST ----------------
        response = self.client.put('/api/user/reviews/{reviewee_id}'.format(reviewee_id=reviewee_id),
                                   headers={"Content-Type": "application/json", "Authorization": authorization_d},
                                   data=payload)

        self.assertEqual(response.json.get("reviewer_id"), reviewer_id)
        self.assertEqual(response.json.get("reviewee_id"), reviewee_id)
        self.assertEqual(response.json.get("score"), 5)
        self.assertEqual(response.json.get("review_text"), "good")

    def test_delete_review(self):
        # create Reviewer
        response = self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        reviewer_id = response.json.get("id")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token_d = response.json.get("token")
        authorization_d = "Bearer {token}".format(token=token_d)

        # create Reviewee
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        reviewee_id = response.json.get("id")

        # create Review
        response = self.help_create_review(reviewee_id, 4.5, "test", authorization_d)

        self.assertNotEqual(None, Review.query.get({"reviewer_id": reviewer_id, "reviewee_id": reviewee_id}))

        # -------------- ACTUAL TEST ----------------
        self.help_delete_review(reviewee_id, authorization_d)

        self.assertEqual(None, Review.query.get({"reviewer_id": reviewer_id, "reviewee_id": reviewee_id}))

    def test_read_review(self):
        # create Reviewer
        response = self.help_register("TEST_MarkD", "Mark", "Peeters", "MarkIsCool420")
        reviewer_id = response.json.get("id")
        response = self.help_login("TEST_MarkD", "MarkIsCool420")
        token_d = response.json.get("token")
        authorization_d = "Bearer {token}".format(token=token_d)

        # create Reviewee
        response = self.help_register("TEST_MarkP", "Mark", "Peeters", "MarkIsCool420")
        reviewee_id = response.json.get("id")

        response = self.help_create_review(reviewee_id, 4.5, "test", authorization_d)

        # -------------- ACTUAL TEST ----------------
        response = self.help_read_review(reviewer_id, reviewee_id, authorization_d)
        self.assertEqual(response.json.get("reviewer_id"), reviewer_id)
        self.assertEqual(response.json.get("reviewee_id"), reviewee_id)
        self.assertEqual(response.json.get("score"), 4.5)
        self.assertEqual(response.json.get("review_text"), "test")

        # switch user
        response = self.help_login("TEST_MarkP", "MarkIsCool420")
        token = response.json.get("token")
        authorization = "Bearer {token}".format(token=token)

        response = self.help_read_review(reviewee_id, reviewer_id, authorization)
        self.assertEqual(None, response.json)
