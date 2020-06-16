Capstone
-----


### Introduction

This project is a simple API to simulate a stock exchange.
Each stock's opening price is set upon its listing, and its following price is simulated using random walk every 10 seconds.
This API allows all people to view latest price, view latest price on specific exchange and register as trader
This API allows traders to log in and log out, buy and sell stock at its current price.
This API allows administrator to list, modify and unlist a stock.


### File

* app.py -- the main app
* auth.py -- handle authorization of jwt tokens and communication with Auth0 API
* manage.py
* models.py -- implement the models
* price_generator.py -- generate new stock price continuously
* Procfile
* requirements.txt -- required Python packages
* setup.sh -- set environmental variables
* test_app.py -- implement unit testing


### Role and permission

* Admin
    * list:stock
    * modify:stock
    * unlist:stock
    Test account: email: aaa@gmail.com, password: A1aaaaaaa

* Trader
    * trade:stock
    Test account: email: bbb@gmail.com, password: B2bbbbbbb
