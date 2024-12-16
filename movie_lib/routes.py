from movie_lib import app, db
from movie_lib.models import *

from flask import render_template


@app.route("/")
def hello_world():
    return render_template('home.html')


@app.route("/movie/<movieid>")
def movie_load(movieid):
    
    movie_found = MovieDAO.MovieById(movieid,db)

    return render_template('movie.html',movie=movie_found)

@app.route("/movies")
def list_movies():
    
    found_movies = MovieDAO.allMovies(db)
    
    return render_template('movies_list.html', 
                        movies=found_movies)


@app.route("/actors")
def list_actors():
    
    found_actors = ActorDAO.allActors(db)
    
    return render_template('actors_list.html', actors= found_actors)

@app.route("/actor/<actorid>")
def actor_load(actorid):
    
    found_actor = ActorDAO.actorById(actorid, db=db)
    
    return render_template('actor.html', actor=found_actor)