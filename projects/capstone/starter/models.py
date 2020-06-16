
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
Table for constantly updating stock price
'''
class Price(db.Model):  
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey('stock.code'), index=True)
    price = Column(Integer,nullable=False)
    timestamp = Column(DateTime,nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

'''
Asscociation table for the many-to-many relationship between Trader and Stock
'''
class Possession(db.Model):
    __tablename__ = 'possession'

    trader_id = Column(String, ForeignKey('trader.id'), primary_key=True)
    stock_code = Column(String, ForeignKey('stock.code'), primary_key=True)
    position = Column(Integer, nullable = False)
    stock = db.relationship("Stock", back_populates="traders")
    trader = db.relationship("Trader", back_populates="stocks")

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Stock(db.Model):  
    __tablename__ = 'stock'

    code = Column(String, index = True, primary_key = True)
    name = Column(String,nullable = False)
    market_id = Column(Integer, ForeignKey('market.id'))
    prices = db.relationship('Price',backref = 'stock', cascade='all,delete', lazy = True)
    traders = db.relationship("Possession", back_populates="stock")

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
    stocks = db.relationship("Possession", back_populates="trader")

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