from sqlalchemy import text
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from typing import List

from movie_lib import Base

from sqlalchemy import select


class Movie:    
    def __init__(self, title, id, description=None, cover_url = None, release_year=None):
        self.title = title
        self.id = id
        self.description = description
        self.cover_url = cover_url
        self.release_year = release_year



cast = Table(
'cast',
Base.metadata,
Column("actor_id", ForeignKey("Actor.id"), primary_key=True),
Column("movie_id", ForeignKey("Movie.id"), primary_key=True)
)

class MovieORM(Base):    
    __tablename__ = "Movie"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_year = Column(String)
    description = Column(String)
    cover_url = Column(String)
    
    actors: Mapped[List["ActorORM"]] = relationship(secondary='cast')

class MovieDAO():
    
    def MovieById(movieid, db):
        
        stm = select(MovieORM).where(MovieORM.id == movieid)
        
        movie = db.session.scalar(stm)
        
        return movie
    
    def allMovies(db):
        
        stm = select(MovieORM)
        
        movies = db.session.scalars(stm).all()
        
        return movies
        

class ActorORM(Base):
    __tablename__ = 'Actor'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    birthday = Column(String)
    description = Column(String)
    photo_url = Column(String)
    
    movies: Mapped[List["MovieORM"]] = relationship(secondary="cast")
    
class ActorDAO():
    def actorById(actorid, db):
        
        stm = select(ActorORM).where(ActorORM.id == actorid)
        
        actor = db.session.scalar(stm)
        
        return actor
    
    def allActors(db):
        
        stm = select(ActorORM)
        
        actors = db.session.scalars(stm).all()
        
        return actors