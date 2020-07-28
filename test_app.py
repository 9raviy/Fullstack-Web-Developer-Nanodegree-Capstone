import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import Actor, Movie, setup_db
from app import create_app
from models import db
import datetime


# Tokens to Test the Unit Tests
director_header = {
    'Authorization': 'Bearer ' + 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQySVdBUkZMQWp1N1dnZDJSd0RvQiJ9.eyJpc3MiOiJodHRwczovL2xvZ2lucGF0aC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWVmMjA3YTE3Nzk3YzEwMDEzNzAxODdiIiwiYXVkIjoiY2FzdCIsImlhdCI6MTU5NTk2NjczMiwiZXhwIjoxNTk1OTczOTMyLCJhenAiOiJtbGthY1JvS2ZlN3dUTnNWdTBlZkFGbzlTM25EVXJxVyIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9yIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvciIsInBvc3Q6bW92aWUiLCJ2aWV3OmFjdG9ycyIsInZpZXc6bW92aWVzIl19.JuJ4qLilUdANT5cV1iGnCPXIGa3nQUo7JcvQg3xEbTtK_nU3ZEorFlayZGuu-KLzl7IomjAC6IZpCFg--pMI6QcLekcG-WIFUskg73pJ1Z9OYYZtehIJP5OVySKLLRJkP5aWaQiLPQgOCtn_V0zNRDnCUO9cLJ49YiZLoBuUVN_rnBs92vMGnGfqswsVvofxG_2r19GcYPek7stGzNTmN9beGFsepdEPPUfgtfl41tkdqCsTtzuJsw8X-eYJzLZoPfeVUhwUIi-I2W13Taglw0CIJbchi9LBFbWYjRvMAgEAaCKpoX1gF2gF98oZBQrpwUdBHZWuhxJEQ2SoAkOQDA'
}
assistant_header = {
    'Authorization': 'Bearer ' + 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQySVdBUkZMQWp1N1dnZDJSd0RvQiJ9.eyJpc3MiOiJodHRwczovL2xvZ2lucGF0aC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYxZjk1ZmZkOTNjMTAwMDNkY2IwZWNkIiwiYXVkIjoiY2FzdCIsImlhdCI6MTU5NTk2NzA1MywiZXhwIjoxNTk1OTc0MjUzLCJhenAiOiJtbGthY1JvS2ZlN3dUTnNWdTBlZkFGbzlTM25EVXJxVyIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsidmlldzphY3RvcnMiLCJ2aWV3Om1vdmllcyJdfQ.xn1iwJn-KzsquDznT5GJ6otE-8ytp8WthqHHE43uqxb2ybiA1yYhMPbB7VrIQowoCcsoXWLpQNVnqs2LUrebG55om3f-RzVcAadJKPabkGxzKy2KrYIfOyiloJsFObiod3uHxCWSG0nIT9Ua--DR_I_SxB-0CjN1ebnPfTYiZq-XxAk_boVauMaClcYHP3-1lkyjRyfCUzp232CLA_hs7l02AbxQWf-EesnFMdYdteLKxv6X77wQ_-MIP9ixcxs2oAGnHhYsVEpJfWEdmeCTIAjpmZDNi-xu-MoMSZpLwUb9r9F4uL2x-D_wsFYrHjPRf7pc0hDPGXnH8QGLUeCvEQ'
}
producer_header = {
    'Authorization': 'Bearer ' + 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQySVdBUkZMQWp1N1dnZDJSd0RvQiJ9.eyJpc3MiOiJodHRwczovL2xvZ2lucGF0aC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWVmMjM0YjJlZmY0NTYwMDE5MzA1YWYyIiwiYXVkIjoiY2FzdCIsImlhdCI6MTU5NTk2Njk0MywiZXhwIjoxNTk1OTc0MTQzLCJhenAiOiJtbGthY1JvS2ZlN3dUTnNWdTBlZkFGbzlTM25EVXJxVyIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9yIiwiZGVsZXRlOm1vdmllIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvciIsInBvc3Q6bW92aWUiLCJ2aWV3OmFjdG9ycyIsInZpZXc6bW92aWVzIl19.QNYocyoN80XS7IubReA2kBklbqCxCdi-jUKELiL0Qad2QzxY3UOnnXjbr42gzBj_D09JbhQU5r8s5j9mwsYH-JipVkqyJ0x-UJnIhzjgD6m87oCJOJOZ5Qh2bY7FHs7c1z_qnkf-u-3cghkEX0PQYdWkyDeAsKzoyf-sDaVH2yehE5DuaUgXuBp9DVrX_XUYIKIr0KnCJrX06k3Qc7vuLrl-a2OVLfEIX4HpL9R_nae5oQFclRzPAPo71xngPv3uXv7cct9iZmnyUl0eyQtCY8kUBu_Hqo-77EU2kCwzNvduCK1aO682QvxLf-F_5wYxQrrjof6CKJCHM2qDz4rT2w'
}


class AgencyTestCase(unittest.TestCase):

    def setUp(self):
        '''define the variables and initialize the app'''

        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)
        db.create_all()

        self.new_movie = {
            'title': 'Mission',
            'release_date': datetime.date(2020, 6, 20),
        }

        self.new_actor = {
            'name': 'Ravi Yadav',
            'age': 30,
            'gender': 'Male',
            'movie_id': 1
        }

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        pass

    def test_get_movies(self):
        res = self.client().get('/movies', headers=assistant_header)
        self.assertEqual(res.status_code, 200)

    def test_get_movies_fail(self):
        res = self.client().get('/moviess', headers=assistant_header)
        self.assertEqual(res.status_code, 404)

    def test_get_actors(self):
        res = self.client().get('/actors', headers=assistant_header)
        self.assertEqual(res.status_code, 200)

    def test_get_actors_fail(self):
        res = self.client().get('/actorss', headers=assistant_header)
        self.assertEqual(res.status_code, 404)

    def test_create_movie(self):
        res = self.client().post('/movies/create', json=self.new_movie, headers=producer_header)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['new_movie']['title'], 'Mission')

    def test_create_actor(self):
        res = self.client().post('/actors/create', json=self.new_actor, headers=producer_header)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['new_actor']['name'], 'Ravi Yadav')

    def test_delete_movie(self):
        res = self.client().delete('/movies/delete/1', headers=producer_header)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_movie_fail(self):
        res = self.client().delete('/movies/delete/1000', headers=producer_header)
        self.assertEqual(res.status_code, 404)

    def test_delete_actor(self):
        res = self.client().delete('/actors/delete/1', headers=producer_header)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_actor_fail(self):
        res = self.client().delete('/actors/delete/1000', headers=producer_header)
        self.assertEqual(res.status_code, 404)

    def test_patch_movie(self):
        res = self.client().patch('/movies/patch/2', json=self.new_movie, headers=producer_header)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_movie_fail(self):
        res = self.client().patch('/movies/patch/2000', json=self.new_movie, headers=producer_header)
        self.assertEqual(res.status_code, 404)

    def test_patch_actor(self):
        res = self.client().patch('/actors/patch/2', json=self.new_actor, headers=producer_header)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_actor_fail(self):
        res = self.client().patch('/actors/patch/2000', json=self.new_actor, headers=producer_header)
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
