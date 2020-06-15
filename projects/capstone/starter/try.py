import time
from numpy import random
from datetime import datetime

from models import setup_db, Stock, db
from app import create_app

app = create_app()
app.app_context().push()

# Check if the Stock table is empty
check = db.session.query(Stock).all()

# If empty, initiate the table with current time and price 100
if not check:
  stock = Stock(price = 100, timestamp=datetime.now())
  stock.insert()

# Generate new price every 10 seconds
# Insert a new record using current time and new price
starttime = time.time()
while True:
  current_time = datetime.now()
  price = db.session.query(Stock.price).order_by(Stock.id.desc()).first()[0]
  new_price = Stock(price = price + random.randn() * 5, timestamp=current_time)
  new_price.insert()
  time.sleep(10.0 - ((time.time() - starttime) % 10.0))
