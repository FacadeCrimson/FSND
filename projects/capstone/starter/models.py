
import os
from sqlalchemy import Column, String, Integer, DateTime, create_engine, ForeignKey
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
class Price(db.Model):  
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey('stock.code'), index=True)
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


trader_stocks = db.Table('trader_stocks',
  Column('trader_id', String, ForeignKey('trader.id'),primary_key = True),
  Column('stock_code', String, ForeignKey('stock.code'),primary_key = True),
  Column('position', Integer, nullable = False)
)

class Stock(db.Model):  
    __tablename__ = 'stock'

    code = Column(String, index = True, primary_key = True)
    name = Column(String,nullable = False)
    market_id = Column(Integer, ForeignKey('market.id'))
    prices = db.relationship('Price',backref = 'stock', cascade='all,delete', lazy = True)

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Trader(db.Model):
    __tablename__ = 'trader'

    id = Column(String, index = True, primary_key = True)
    name = Column(String,nullable = False)
    email = Column(String, nullable = False)
    cash = Column(Integer,nullable = False)
    stocks = db.relationship('Stock',secondary = trader_stocks,backref = db.backref('trader',cascade='all,delete', lazy = True))

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Market(db.Model):
    __tablename__ = 'market'

    id = Column(Integer, primary_key = True)
    name = Column(String,nullable = False)
    stocks = db.relationship('Stock',backref = 'market', lazy = True)