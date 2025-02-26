import datetime
from flask_sqlalchemy import SQLAlchemy


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  # TODO: implement any missing fields, as a database migration using Flask-Migrate --done
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500))
  created_at = db.Column(db.DateTime, default= datetime.datetime.utcnow())
  shows = db.relationship('Show',backref='venue',lazy=True,cascade="all,delete",passive_deletes=True)
  def __repr__(self):
    return f'<Venue id={self.id} name={self.name}>'

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
  # TODO: --done implement any missing fields, as a database migration using Flask-Migrate
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500))
  created_at = db.Column(db.DateTime, default= datetime.datetime.utcnow())
  shows = db.relationship('Show',backref='artist',lazy=True,cascade="all,delete",passive_deletes=True)
  def __repr__(self):
    return f'<Artist id={self.id} name={self.name}>'

# TODO  Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "Show"
  # get info for the Show
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
  start_time = db.Column(db.DateTime, default= datetime.datetime.utcnow())
  def __repr__(self):
    return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time}"