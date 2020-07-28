import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from models import setup_db, Movie, Actor, db
from auth import AuthError, requires_auth


def create_app(test_config=None):

    # create the app and set up the database
    app = Flask(__name__)
    CORS(app, resources={r"/api/": {"origins": "*"}})
    setup_db(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
        'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
        'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    @app.route('/movies')
    @requires_auth('view:movies')
    def get_movies():
        movies = Movie.query.all()
        movies = [movie.format() for movie in movies]
        for movie in movies:
            movie['actors'] = [item.format() for item in movie['actors']]
        return jsonify(movies)

    @app.route('/actors')
    @requires_auth('view:actors')
    def get_actors():
        actors = Actor.query.all()
        actors = [actor.format() for actor in actors]
        return jsonify(actors)

    @app.route('/movies/create', methods=['POST'])
    @requires_auth('post:movie')
    def post_new_movie():
        body = request.get_json()

        title = body.get('title', None)
        date_released = body.get('release_date', None)

        movie = Movie(title=title, release_date=date_released)
        movie.insert()
        fresh_movie = Movie.query.get(movie.id)
        fresh_movie = fresh_movie.format()

        return jsonify({
            'success': True,
            'created': movie.id,
            'new_movie': fresh_movie
        })

    @app.route('/actors/create', methods=['POST'])
    @requires_auth('post:actor')
    def post_new_actor():
        body = request.get_json()
        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        movie_id = body.get('movie_id', None)

        actor = Actor(name=name, age=age, gender=gender, movie_id=movie_id)
        actor.insert()
        fresh_actor = Actor.query.get(actor.id)
        fresh_actor = fresh_actor.format()

        return jsonify({
            'success': True,
            'created': actor.id,
            'new_actor': fresh_actor
        })

    @app.route('/movies/delete/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(movie_id):
        Movie.query.filter(Movie.id == movie_id).delete()
        db.session.commit()
        db.session.close()
        return jsonify({
            "success": True,
            "message": "Delete occured"
        })

    @app.route('/actors/delete/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(actor_id):
        if not actor_id:
            abort(404)

        actor_to_delete = Actor.query.get(actor_id)
        if not actor_to_delete:
            abort(404)
        
        actor_to_delete.delete()

        db.session.commit()
        db.session.close()
        return jsonify({
            "success": True,
            "message": "Delete occured"
        })

    @app.route('/actors/patch/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def patch_actor(actor_id):

        actor = Actor.query.filter(Actor.id == actor_id)
        body = request.get_json()
        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        movie_id = body.get('movie_id', None)
        actor.name = name
        actor.age = age
        actor.gender = gender
        actor.movie_id = movie_id
        actor.update()
        return jsonify({
            "success": True,
            "message": "update occured"
        })

    @app.route('/movies/patch/<int:movie_id>')
    @requires_auth('patch:movies')
    def patch_movie(movie_id):
        movie = Movie.query.filter(Movie.id == movie_id)
        body = request.get_json()
        title = body.get('title', None)
        date_released = body.get('release_date', None)
        movie.title = title
        movie.release_date = date_released
        movie.update()
        return jsonify({
            "success": True,
            "message": "update occured"
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        })
    
    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
