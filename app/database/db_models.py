# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
# from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, Boolean, String

from .database import Base

class User(Base):
    # Base is the declarative_base() from sqlalchemy

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True) 
    #, autoincrement=True)

    # uid used in the game 
    # uid = Column(Integer, primary_key=True, index=True)
    
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    current_game = Column(String, default="")
    