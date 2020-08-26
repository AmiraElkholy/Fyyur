#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db 

migrate = Migrate(app, db)

# engine configuration
engine = create_engine('postgres://postgres:root@localhost:5432/fyyur')
conn = engine.connect()

from models import Show, Venue, Artist


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
    venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.order_by('city').all()

  data = []
  venue = venues[0]
  city = venue.city
  i = {}
  i['city'] = venue.city
  i['state'] = venue.state
  i['venues'] = []
  num_upcoming_shows = venue.format()['upcoming_shows_count']
  v = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': num_upcoming_shows
  }
  i['venues'].append(v)

  for venue in venues:
    if venue == venues[0]:
        continue
    if venue.city == city:
        num_upcoming_shows = venue.format()['upcoming_shows_count']  
        v = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': num_upcoming_shows
        }
        i['venues'].append(v)
        city = venue.city
    if venue.city != city:
        data.append(i)
        i = {}
        i['city'] = venue.city
        i['state'] = venue.state
        i['venues'] = []

        num_upcoming_shows = venue.format()['upcoming_shows_count']  
        v = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': num_upcoming_shows
        }
        i['venues'].append(v)
        city = venue.city
    
  data.append(i)

  return render_template('pages/venues.html', areas=data);



@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  search_term = "%{}%".format(search_term)

  venues = Venue.query.filter(Venue.name.ilike(search_term)).all()
  
  response = {
    'count': len(venues),
    'data': []
  }

  for venue in venues:
    num_upcoming_shows = venue.format()['upcoming_shows_count']  
    i = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': num_upcoming_shows
    }
    response['data'].append(i)

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))




@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id).format() 
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create/', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  if form.validate():
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        facebook_link = request.form.get('facebook_link')
        genres = request.form.getlist('genres')
        genres = ','.join(genres)
        image_link = request.form.get('image_link')
        website = request.form.get('website')
        if request.form.get('seeking_talent') is None:
          seeking_talent = False 
        else:
          seeking_talent = True
        seeking_description = request.form.get('seeking_description')

        venue = Venue(
          name=name, 
          city=city, 
          state=state, 
          address=address, 
          phone=phone, 
          facebook_link=facebook_link, 
          genres=genres,
          image_link=image_link, 
          website=website, 
          seeking_talent=seeking_talent, 
          seeking_description=seeking_description
        )

        db.session.add(venue)
        db.session.commit()

        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + venue.name + ' could not be listed.')

    finally:
        return render_template('pages/home.html')

  return redirect(url_for('create_venue_form'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for(index))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.order_by('id').all()
    return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  search_term = "%{}%".format(search_term)

  artists = Artist.query.filter(Artist.name.ilike(search_term)).all()
  
  response = {
    'count': len(artists),
    'data': []
  }

  for artist in artists:
    num_upcoming_shows = artist.format()['upcoming_shows_count']
    i = {
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': num_upcoming_shows
    }
    response['data'].append(i)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id).format()
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id) 
  artist.genres = artist.genres.split(',')
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  if form.validate():
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.address = request.form.get('address')
        artist.phone = request.form.get('phone')
        artist.facebook_link = request.form.get('facebook_link')
        genres = request.form.getlist('genres')
        artist.genres = ','.join(genres)
        artist.image_link = request.form.get('image_link')
        venue.website = request.form.get('website')
        if request.form.get('seeking_venue') is None:
          artist.seeking_venue = False 
        else:
          artist.seeking_venue = True
        artist.seeking_description = request.form.get('seeking_description')

        db.session.commit()

        flash('Artist ' + artist.name + ' was successfully updated!')
    
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + artist.name + ' could not be updated.')

    finally:
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    return redirect(url_for(edit_artist), artist_id=artist_id)




@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id) 
  venue.genres = venue.genres.split(',')
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.address = request.form.get('address')
      venue.phone = request.form.get('phone')
      venue.facebook_link = request.form.get('facebook_link')
      genres = request.form.getlist('genres')
      venue.genres = ','.join(genres)
      venue.image_link = request.form.get('image_link')
      venue.website = request.form.get('website')
      if request.form.get('seeking_talent') is None:
        venue.seeking_talent = False 
      else:
        venue.seeking_talent = True
      venue.seeking_description = request.form.get('seeking_description')

      db.session.commit()

      flash('Venue ' + venue.name + ' was successfully updated!')
    
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + venue.name + ' could not be updated.')

    finally:
        return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    return redirect(url_for('edit_venue', venue_id = venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  if form.validate():
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      facebook_link = request.form.get('facebook_link')
      genres = request.form.getlist('genres')
      genres = ','.join(genres)
      image_link = request.form.get('image_link')
      website = request.form.get('website')
      if request.form.get('seeking_venue') is None:
        seeking_venue = False 
      else:
        seeking_venue = True
      seeking_description = request.form.get('seeking_description')

      artist = Artist(
        name=name, 
        city=city, 
        state=state, 
        phone=phone, 
        facebook_link=facebook_link, 
        genres=genres, 
        image_link=image_link, 
        website=website, 
        seeking_venue=seeking_venue, 
        seeking_description=seeking_description
      )

      db.session.add(artist)
      db.session.commit()

      flash('Artist ' + artist.name + ' was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + artist.name + ' could not be listed.')

    finally:
        return render_template('pages/home.html')
  else:
    return redirect(url_for('create_artist_form'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append(show.format())
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():  
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  if form.validate():
    try:
      venue_id = request.form.get('venue_id')
      artist_id = request.form.get('artist_id')
      start_time = request.form.get('start_time')

      venue = Venue.query.get(venue_id)
      artist = Artist.query.get(artist_id)
      venue.artists.append(artist)

      db.session.commit()

      result = conn.execute("UPDATE shows SET start_time = '" + start_time + "' WHERE venue_id = " + venue_id + " AND artist_id = " + artist_id + " AND start_time IS NULL")

      result.close()

      flash('Show was successfully listed!')

    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
  
    finally:
      return render_template('pages/home.html')

  else:
    return redirect(url_for('create_shows'))


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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
