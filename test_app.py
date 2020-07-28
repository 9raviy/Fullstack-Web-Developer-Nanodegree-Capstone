import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import Actor, Movie, setup_db
from app import create_app
from models import db
import datetime


class CastingTestCase(unittest.TestCase):

    def setUp(self):
        '''define test variables and initialize app'''

        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)
        db.create_all()

        self.new_movie = {
            'title': 'New Movie',
            'release_date' : datetime.date(2019, 3, 13),
        }

        self.new_actor = {
            'name': 'John Doe',
            'age': 22,
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
        res = self.client().get('/movies')
        self.assertEqual(res.status_code, 200)

    def test_get_movies_fail(self):
        res = self.client().get('/moviess')
        self.assertEqual(res.status_code, 404)

    def test_get_actors(self):
        res = self.client().get('/actors')
        self.assertEqual(res.status_code, 200)

    def test_get_actors_fail(self):
        res = self.client().get('/actorss')
        self.assertEqual(res.status_code, 404)

    def test_create_movie(self):
        res = self.client().post('/movies/create', json=self.new_movie)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['new_movie']['title'], 'New Movie')

    def test_create_actor(self):
        res = self.client().post('/actors/create', json=self.new_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['new_actor']['name'], 'John Doe')
    
    def test_delete_movie(self):
        res = self.client().delete('/movies/delete/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_delete_movie_fail(self):
        res = self.client().delete('/movies/delete/1000')
        self.assertEqual(res.status_code, 404)
    
    def test_delete_actor(self):
        res = self.client().delete('/actors/delete/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_delete_actor_fail(self):
        res = self.client().delete('/actors/delete/1000')
        self.assertEqual(res.status_code, 404)
    
    def test_patch_movie(self):
        res = self.client().patch('/movies/patch/2', json=self.new_movie)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_patch_movie_fail(self):
        res = self.client().patch('/movies/patch/2000', json=self.new_movie)
        self.assertEqual(res.status_code, 404)

    
    def test_patch_actor(self):
        res = self.client().patch('/actors/patch/2', json=self.new_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_patch_actor_fail(self):
        res = self.client().patch('/actors/patch/2000', json=self.new_actor)
        self.assertEqual(res.status_code, 404)
    






if __name__ == "__main__":
    unittest.main()
