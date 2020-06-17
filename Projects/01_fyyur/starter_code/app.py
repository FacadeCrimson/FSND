#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_,func,distinct,case
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


venue_genres = db.Table('venue_genres',
  db.Column('venue_id',db.Integer,db.ForeignKey('Venue.id'),primary_key=True),
  db.Column('genres_id',db.Integer,db.ForeignKey('Genres.id'),primary_key=True)
)

artist_genres = db.Table('artist_genres',
  db.Column('artist_id',db.Integer,db.ForeignKey('Artist.id'),primary_key=True),
  db.Column('genres_id',db.Integer,db.ForeignKey('Genres.id'),primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120),unique=True)
    website=db.Column(db.String(120),unique=True)
    facebook_link = db.Column(db.String(120),unique=True)
    seeking_talent=db.Column(db.Boolean)
    seeking_description=db.Column(db.String())
    image_link = db.Column(db.String(500))
    genres = db.relationship('Genres',secondary=venue_genres,backref=db.backref('venue',lazy=True))
    shows = db.relationship('Show',backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120),unique=True)
    website=db.Column(db.String(120),unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120),unique=True)
    seeking_venue=db.Column(db.Boolean)
    seeking_description=db.Column(db.String())
    genres = db.relationship('Genres',secondary=artist_genres,backref=db.backref('Genres',lazy=True))
    shows = db.relationship('Show',backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    #insert into "Venue" values (9, 'The Dueling Pianos Bar','New York','NY','335 Delancey Street','914-003-1132','https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80','https://www.facebook.com/theduelingpianos',NULL,False,'https://www.theduelingpianos.com')
    #insert into venue_genres select 2 as id1, id as id2 from "Genres" where name in ('Classical', 'R&B', 'Hip-Hop')

  
class Genres(db.Model):
    __tablename__ = 'Genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False,unique=True)
    #insert into "Genres" (name) values ('Alternative'),('Blues'),('Classical'), ('Country'),('Electronic'),('Folk'),('Funk'),('Hip-Hop'),('Heavy Metal'),('Instrumental'),('Jazz'),('Musical Theatre'),('Pop'),('Punk'),('R&B'),('Reggae'),('Rock n Roll'),('Soul'),('Other');

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artists = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
    venues = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
    time = db.Column(db.DateTime)

    # insert into "Show" (artist, venue, time) values (1,1,'2020-10-19 10:23:54');

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  t=datetime.now()
  data=db.session.query(Venue.id,Venue.name,Venue.state,Venue.city,func.count(case([(Show.time>t, 1)]))).outerjoin(Show).group_by(Venue.id,Venue.name,Venue.state,Venue.city).order_by(Venue.state,Venue.city).all()
  area=[]
  state=""
  city=""
  for x,y,b,c,count in data:
    if b!=state or c!=city:
      area.append({"city":c,"state":b,"venues": [{"id": x,"name": y,"num_upcoming_shows": count}]})
      state=b
      city=c
    else:
      area[-1]["venues"].append({"id": x,"name": y,"num_upcoming_shows": count})
  
  return render_template('pages/venues.html', areas=area)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term', '')
  query=db.session.query(Venue.id,Venue.name,func.count(Show.time>=datetime.now())).outerjoin(Show)\
    .filter(or_(Show.time>=datetime.now(),Show.time == None))\
    .filter(Venue.name.ilike('%'+search_term+'%')).group_by(Venue.id,Venue.name).all()
  response={"data":[]}
  response["count"]=len(query)
  for a,b,c in query:
    response["data"].append({"id":a,"name":b,"num_upcoming_shows":c})
    
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  query=db.session.query(Venue.name,Venue.address,Venue.city,Venue.state,Venue.phone,Venue.website,Venue.facebook_link,Venue.image_link,Venue.seeking_talent,Venue.seeking_description)\
    .filter(Venue.id==venue_id).all()
  a,b,c,d,e,f,g,h,i,j = query[0]
  data={"name":a,"address":b,"city":c,"state":d,"phone":e,"website":f,"facebook_link":g,"image_link":h,"seeking_talent":i,"seeking_description":j}
  data["id"]=venue_id
  data["genres"]=[z[0] for z in db.session.query(Genres.name).join(venue_genres).join(Venue).filter(Venue.id==venue_id).all()]
  data["past_shows_count"]=0
  data["upcoming_shows_count"]=0
  data["upcoming_shows"]=[]
  data["past_shows"]=[]
  query1=db.session.query(Artist.id,Artist.name,Artist.image_link,Show.time).join(Show).filter(Show.venues==venue_id).all()
  for a,b,c,d in query1:
    if d >= datetime.now():
      data["upcoming_shows"].append({"artist_id":a,"artist_name":b,"artist_image_link":c,"start_time":d})
      data["upcoming_shows_count"]+=1
    else:
      data["past_shows"].append({"artist_id":a,"artist_name":b,"artist_image_link":c,"start_time":d})
      data["past_shows_count"]+=1
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = VenueForm(request.form)
  try:
    name=form.name.data
    city=form.city.data
    state=form.state.data
    address=form.address.data
    phone=form.phone.data
    website=form.website.data
    image_link=form.image_link.data
    facebook_link=form.facebook_link.data
    seeking_talent=form.seeking_talent.data
    seeking_description=form.seeking_description.data
    genres=form.genres.data

    venue = db.session.query(Venue).filter(or_(Venue.name==name,Venue.address==address,Venue.phone==phone,Venue.website==website)).first()
    
    venue=Venue(name=name,city=city,state=state,address=address,phone=phone,website=website,image_link=image_link,facebook_link=facebook_link,seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(venue)
    for x in genres:
      y=Genres.query.get(x)
      venue.genres.append(y)
    
    db.session.commit()
     # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  except():
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
      db.session.close()
 
  return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  name=""
  try:
      venue = Venue.query.get(venue_id)
      name=venue.name[:]
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + name + ' was successfully deleted!')
  except():
      db.session.rollback()
  finally:
      db.session.close()
  return render_template('pages/venues.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  name=""
  try:
      artist = Artist.query.get(artist_id)
      name=artist.name[:]
      db.session.delete(artist)
      db.session.commit()
      flash('Artist ' + name + ' was successfully deleted!')
  except():
      db.session.rollback()
  finally:
      db.session.close()
  return render_template('pages/artists.html')
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=db.session.query(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  query=db.session.query(Artist.id,Artist.name)\
    .filter(Artist.name.ilike('%'+search_term+'%')).all()
  response={"data":[]}
  response["count"]=len(query)
  for a,b in query:
    response["data"].append({"id":a,"name":b})
    
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  query=db.session.query(Artist.name,Artist.city,Artist.state,Artist.phone,Artist.website,Artist.facebook_link,Artist.image_link,Artist.seeking_venue,Artist.seeking_description)\
    .filter(Artist.id==artist_id).all()
  a,c,d,e,f,g,h,i,j= query[0]
  data={"name":a,"city":c,"state":d,"phone":e,"website":f,"facebook_link":g,"image_link":h,"seeking_venue":i,"seeking_description":j}
  data["id"]=artist_id
  data["genres"]=[z[0] for z in db.session.query(Genres.name).join(artist_genres).join(Artist).filter(Artist.id==artist_id).all()]
  data["past_shows_count"]=0
  data["upcoming_shows_count"]=0
  data["upcoming_shows"]=[]
  data["past_shows"]=[]
  query2=db.session.query(Venue.id,Venue.name,Venue.image_link,Show.time).join(Show).filter(Show.venues==artist_id).all()
  for a,b,c,d in query2:
    if d >= datetime.now():
      data["upcoming_shows"].append({"venue_id":a,"venue_name":b,"venue_image_link":c,"start_time":d})
      data["upcoming_shows_count"]+=1
    else:
      data["past_shows"].append({"venue_id":a,"venue_name":b,"venue_image_link":c,"start_time":d})
      data["past_shows_count"]+=1
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  query=db.session.query(Artist.name,Artist.city,Artist.state,Artist.phone,Artist.website,Artist.facebook_link,Artist.image_link,Artist.seeking_venue,Artist.seeking_description)\
    .filter(Artist.id==artist_id).all()
  a,c,d,e,f,g,h,i,j= query[0]

  artist={"id": artist_id,"name": a,"city": c,"state": d,"phone":e,"website":f,"facebook_link":g,"image_link":h,"seeking_venue":i,"seeking_description":j}
  artist["genres"]=[z[0] for z in db.session.query(Genres.id).join(artist_genres).join(Artist).filter(Artist.id==artist_id).all()]
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  try:
    artist=Artist.query.get(artist_id)
    name=form.name.data
    city=form.city.data
    state=form.state.data
    phone=form.phone.data
    website=form.website.data
    image_link=form.image_link.data
    facebook_link=form.facebook_link.data
    seeking_venue=form.seeking_venue.data
    seeking_description=form.seeking_description.data
    genres=form.genres.data

    artist.name=name
    artist.city=city
    artist.state=state
    artist.phone=phone
    artist.website=website
    artist.image_link=image_link
    artist.facebook_link=facebook_link
    artist.seeking_venue=seeking_venue
    artist.seeking_description=seeking_description
    artist.genres=[]
    for x in genres:
      y=Genres.query.get(x)
      artist.genres.append(y)
    db.session.commit()
     # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully modified!')
  except():
    db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + name + ' could not be modified.')
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  query=db.session.query(Venue.name,Venue.address,Venue.city,Venue.state,Venue.phone,Venue.website,Venue.facebook_link,Venue.image_link,Venue.seeking_talent,Venue.seeking_description)\
    .filter(Venue.id==venue_id).all()
  a,b,c,d,e,f,g,h,i,j = query[0]
  venue={"id": venue_id,"name":a,"address":b,"city":c,"state":d,"phone":e,"website":f,"facebook_link":g,"image_link":h,"seeking_talent":i,"seeking_description":j}
  venue["genres"]=[z[0] for z in db.session.query(Genres.id).join(venue_genres).join(Venue).filter(Venue.id==venue_id).all()]
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form =  VenueForm(request.form)
  try:
    name=form.name.data
    city=form.city.data
    state=form.state.data
    address=form.address.data
    phone=form.phone.data
    website=form.website.data
    image_link=form.image_link.data
    facebook_link=form.facebook_link.data
    seeking_talent=form.seeking_talent.data
    seeking_description=form.seeking_description.data
    genres=form.genres.data

    venue=Venue.query.get(venue_id)
    venue.name=name
    venue.city=city
    venue.state=state
    venue.address=address
    venue.phone=phone
    venue.website=website
    venue.image_link=image_link
    venue.facebook_link=facebook_link
    venue.seeking_talent=seeking_talent
    venue.seeking_description=seeking_description
    venue.genres=[]

    for x in genres:
      y=Genres.query.get(x)
      venue.genres.append(y)
    db.session.commit()
     # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully modified!')
  except():
    db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + name + ' could not be modified.')
  finally:
      db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)
  try:
    name=form.name.data
    city=form.city.data
    state=form.state.data
    phone=form.phone.data
    website=form.website.data
    image_link=form.image_link.data
    facebook_link=form.facebook_link.data
    seeking_venue=form.seeking_venue.data
    seeking_description=form.seeking_description.data
    genres=form.genres.data

    artist= db.session.query(Artist).filter(or_(Artist.name==name,Artist.phone==phone,Artist.website==website)).first()
    
    
    artist=Artist(name=name,city=city,state=state,phone=phone,website=website,image_link=image_link,facebook_link=facebook_link,seeking_venue=seeking_venue,seeking_description=seeking_description)
    db.session.add(artist)
    for x in genres:
      y=Genres.query.get(x)
      artist.genres.append(y)

    db.session.commit()
     # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except():
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
      db.session.close()
 
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=db.session.query(Venue.id.label("venue_id"),Venue.name.label("venue_name"),Artist.id.label("artist_id"),Artist.name.label("artist_name"),Artist.image_link.label("artist_image_link"),Show.time.label("start_time"))\
  .join(Show,Show.venues==Venue.id).join(Artist,Show.artists==Artist.id).order_by(Show.time,Artist.id,Venue.id).all()

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  

  error = False
  form = ShowForm(request.form)
  try:
    artist_id=form.artist_id.data
    venue_id=form.venue_id.data
    start_time=form.start_time.data
    
    show=Show(artists=artist_id,venues=venue_id,time=start_time)
    db.session.add(show)
    
    db.session.commit()
     # on successful db insert, flash success
    flash('Show at time ' + str(start_time) + ' was successfully listed!')
  except():
      db.session.rollback()
      error = True
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show at time ' + str(start_time) + ' could not be listed.')
  finally:
      db.session.close()
 
  return render_template('pages/home.html')



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
