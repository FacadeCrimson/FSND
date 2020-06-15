import time
from numpy import random
from datetime import datetime

from models import setup_db, Price, db
from app import app

with app.app_context():
  # Check if the Price table is empty
  check = db.session.query(Price).all()

  # If empty, initiate the table with current time and price 100
  if not check:
    price = Price(code = 1, price = 100, timestamp=datetime.now())
    price.insert()

  # Generate new price every 10 seconds
  # Insert a new record using current time and new price
  starttime = time.time()
  while True:
    current_time = datetime.now()
    price = db.session.query(Price.price).order_by(Price.id.desc()).first()[0]
    new_price = Price(code = 1, price = price + random.randn() * 5, timestamp=current_time)
    new_price.insert()
    time.sleep(10.0 - ((time.time() - starttime) % 10.0))
