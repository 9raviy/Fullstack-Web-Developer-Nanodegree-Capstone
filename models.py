from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()





def setup_db(app):
    database_name = "agency"
    database_path = "postgres://{}:{}@{}/{}".format('postgres','Password@123' , 'localhost:5432', database_name)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path #os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    



class Movie(db.Model):
    #this is the movie table in my database . It will have a one to many relationship with the actors table since there are many actors to one movie 
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    release_date = db.Column(db.Date)
    actors = db.relationship('Actor', backref='movies')

    def format(self):
        return{
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date,
            'actors': self.actors        
        }
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Actor(db.Model):
    #this would be the actors table. It will be the child of the Movie table
    __tablename__ = 'actors' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer)
    gender = db.Column(db.String)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'movie_id': self.movie_id
        }
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()