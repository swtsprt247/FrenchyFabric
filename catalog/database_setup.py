import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


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


###########insert at end of file###################
engine = create_engine('sqlite:///frenchy_fabric.db')
Base.metadata.create_all(engine)
