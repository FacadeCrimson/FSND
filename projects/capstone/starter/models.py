
import os
from sqlalchemy import Column, String, Integer, DateTime, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "stock_price"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Stock Price

'''
class Stock(db.Model):  
  __tablename__ = 'stock'

  id = Column(Integer, primary_key=True)
  price = Column(Integer,nullable=False)
  timestamp = Column(DateTime,nullable=False)

#   def __init__(self, question, answer, category, difficulty):
#     self.question = question
#     self.answer = answer
#     self.category = category
#     self.difficulty = difficulty

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

#   def format(self):
#     return {
#       'id': self.id,
#       'question': self.question,
#       'answer': self.answer,
#       'category': self.category,
#       'difficulty': self.difficulty
#     }