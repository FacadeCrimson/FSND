import time
from numpy import random
from datetime import datetime
from sqlalchemy import distinct

from app import app
from models import Price, Stock, db

with app.app_context():
    #Retrieve the newest price for each stock
    query = db.session.query(Price).distinct(Price.code).order_by(Price.code,Price.id.desc()).all()
    values = {x.code:x.price for x in query}

    # Generate new price every 10 seconds
    # The new price is generated using random walk model
    # Insert a new record using current time and new price
    starttime = time.time()
    while True:
        # Check if there is any insertion or deletion on table stock
        # If so, retrieve the last traded price for each stock again
        if len(values) != db.session.query(Stock).count():
            query = db.session.query(Price).distinct(Price.code).order_by(Price.code,Price.id.desc()).all()
            values = {x.code:x.price for x in query}
        for record in values:
            current_time = datetime.now()
            value = values[record]
            new_value = value + random.randn() * 3
            new_price = Price(code = record, price = new_value, timestamp=current_time)
            new_price.insert()
            values[record] = new_value
        time.sleep(10.0 - ((time.time() - starttime) % 10.0))
