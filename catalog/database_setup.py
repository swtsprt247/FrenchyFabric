import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()



class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture
        }



class MainPage(Base):


    __tablename__ = 'main_page'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class Categories(Base):


    __tablename__ = 'categories'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    main_page_id = Column(Integer, ForeignKey('main_page.id'))
    main_page = relationship(MainPage)

# We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }


###########insert at end of file###################
engine = create_engine('sqlite:///frenchy_fabric.db')
Base.metadata.create_all(engine)
