from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(app)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  start_time = db.Column(db.DateTime, nullable=True)

  venue = db.relationship("Venue", backref="artist_shows")
  artist = db.relationship("Artist", backref="venue_shows") 

  def format(self):
    return {
      'venue_id': self.venue_id,
      'venue_name': self.venue.name,
      'artist_id': self.artist_id,
      'artist_name': self.artist.name,
      'artist_image_link': self.artist.image_link,
      'start_time': str(self.start_time)
    }

  def format_for_venue(self):
    return {
        'artist_id': self.artist_id,
        'artist_name': self.artist.name,
        'artist_image_link': self.artist.image_link,
        'start_time': str(self.start_time)
      }

  def format_for_artist(self):
    return {
        'venue_id': self.venue_id,
        'venue_name': self.venue.name,
        'venue_image_link': self.venue.image_link,
        'start_time': str(self.start_time)
    }




class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String())
    genres = db.Column(db.String(), nullable=False)
    artists = db.relationship('Artist', secondary="shows", backref=db.backref('venues'), lazy=True)
    shows = db.relationship('Show', back_populates="venue", cascade='all')

    def get_upcoming_shows(self):
        upcoming_shows = []
        for show in self.shows:
          if show.start_time > datetime.now():
            upcoming_shows.append(show.format_for_venue())
        return upcoming_shows

    def get_past_shows(self):
        past_shows = []
        for show in self.shows:
            if show.start_time < datetime.now():
              past_shows.append(show.format_for_venue())
        return past_shows

    def format(self):
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres.split(','),
        'address': self.address,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'image_link': self.seeking_description,
        'upcoming_shows': self.get_upcoming_shows(),
        'past_shows': self.get_past_shows(),
        'upcoming_shows_count': len(self.get_upcoming_shows()),
        'past_shows_count': len(self.get_past_shows())
      }


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String())
    genres = db.Column(db.String(), nullable=False)

    shows = db.relationship('Show', back_populates="artist", cascade='all')

    def get_upcoming_shows(self):
        upcoming_shows = []
        for show in self.shows:
          if show.start_time > datetime.now():
            upcoming_shows.append(show.format_for_artist())
        return upcoming_shows

    def get_past_shows(self):
        past_shows = []
        for show in self.shows:
            if show.start_time < datetime.now():
              past_shows.append(show.format_for_artist())
        return past_shows

    def format(self):
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres.split(','),
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_shows': self.get_past_shows(),
        'upcoming_shows': self.get_upcoming_shows(),
        'past_shows_count': len(self.get_past_shows()),
        'upcoming_shows_count': len(self.get_upcoming_shows())
      }


