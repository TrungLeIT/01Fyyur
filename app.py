#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship("Show", backref="venues", lazy=False, cascade="all, delete-orphan")

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship("Show", backref="artists", lazy=False, cascade="all, delete-orphan")

# TODO  Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "Show"
    # get info for the Show
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time}"

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers. 
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # add venues
  venues = Venue.query.order_by(db.desc(Venue.created_at)).limit(10).all()
  # add artists
  artists = Artist.query.order_by(db.desc(Artist.created_at)).limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  venue_data = []
  # get all distinct locations (city, state) of Venues
  distinct_city_state_pairs = Venue.query.distinct(Venue.city, Venue.state).all()
  for location in distinct_city_state_pairs:
    city_state_info = {
      "city": location.city,
      "state": location.state
    }
    # get all venues in the current city and state
    venues_in_city_state = Venue.query.filter_by(city=location.city, state=location.state).all()

    # format each venue
    formatted_venues_list = []
    for venue in venues_in_city_state:
      formatted_venues_list.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.now(), venue.shows)))
      })

    city_state_info["venues"] = formatted_venues_list
    venue_data.append(city_state_info)
  return render_template('pages/venues.html', areas=venue_data)

#  Venues search
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_query = request.form.get("search_term", "")

  search_results = {}
  matching_venues = list(Venue.query.filter(
      Venue.name.ilike(f"%{search_query}%") |
      Venue.state.ilike(f"%{search_query}%") |
      Venue.city.ilike(f"%{search_query}%")
  ).all())
  search_results["count"] = len(matching_venues)
  search_results["data"] = []

  for venue in matching_venues:
    venue_info = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.now(), venue.shows)))
    }
    search_results["data"].append(venue_info)

  return render_template('pages/search_venues.html', results=search_results, search_term=search_query)

#  Venues by id
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_details = Venue.query.get(venue_id)
  setattr(venue_details, "genres", venue_details.genres.split(",")) # convert genre string back to array

  # get past shows
  past_performances = list(filter(lambda performance: performance.start_time < datetime.now(), venue_details.shows))
  formatted_past_shows = []
  for performance in past_performances:
    past_show_info = {
      "artist_name": performance.artists.name,
      "artist_id": performance.artists.id,
      "artist_image_link": performance.artists.image_link,
      "start_time": performance.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    formatted_past_shows.append(past_show_info)

  setattr(venue_details, "past_shows", formatted_past_shows)
  setattr(venue_details, "past_shows_count", len(past_performances))

  # get future shows
  future_performances = list(filter(lambda performance: performance.start_time > datetime.now(), venue_details.shows))
  formatted_upcoming_shows = []
  for performance in future_performances:
    upcoming_show_info = {
      "artist_name": performance.artists.name,
      "artist_id": performance.artists.id,
      "artist_image_link": performance.artists.image_link,
      "start_time": performance.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    formatted_upcoming_shows.append(upcoming_show_info)

  setattr(venue_details, "upcoming_shows", formatted_upcoming_shows)    
  setattr(venue_details, "upcoming_shows_count", len(future_performances))

  return render_template('pages/show_venue.html', venue=venue_details)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  venue_form = VenueForm(request.form)
  if venue_form.validate():
    try:
      new_venue_record = Venue(
        name=venue_form.name.data,
        city=venue_form.city.data,
        state=venue_form.state.data,
        address=venue_form.address.data,
        phone=venue_form.phone.data,
        genres=",".join(venue_form.genres.data),
        facebook_link=venue_form.facebook_link.data,
        image_link=venue_form.image_link.data,
        seeking_talent=venue_form.seeking_talent.data,
        seeking_description=venue_form.seeking_description.data,
        website=venue_form.website_link.data
      )
      db.session.add(new_venue_record)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except Exception:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    finally:
      db.session.close()
  else:
    print("\n\n", venue_form.errors)
    # TODO: --done on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return redirect(url_for("index"))

#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.genres.data = venue.genres.split(",") # convert genre string back to array
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue_form = VenueForm(request.form)
  if venue_form.validate():
      try:
        venue_to_update = Venue.query.get(venue_id)

        venue_to_update.name = venue_form.name.data
        venue_to_update.city = venue_form.city.data
        venue_to_update.state = venue_form.state.data
        venue_to_update.address = venue_form.address.data
        venue_to_update.phone = venue_form.phone.data
        venue_to_update.genres = ",".join(venue_form.genres.data)  # convert array to string separated by commas
        venue_to_update.facebook_link = venue_form.facebook_link.data
        venue_to_update.image_link = venue_form.image_link.data
        venue_to_update.seeking_talent = venue_form.seeking_talent.data
        venue_to_update.seeking_description = venue_form.seeking_description.data
        venue_to_update.website = venue_form.website_link.data
        db.session.add(venue_to_update)
        db.session.commit()
        flash("Venue " + venue_form.name.data + " edited successfully")
          
      except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Venue was not edited successfully.")
      finally:
        db.session.close()
  else: 
    print("\n\n", venue_form.errors)
    flash("Venue was not edited successfully.")
  return redirect(url_for('show_venue', venue_id=venue_id))



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: --done Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue " + venue.name + " was deleted successfully!")
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Venue was not deleted successfully.")
  finally:
    db.session.close()
  return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: --done replace with real data returned from querying the database
  artists = db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: --done implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_query = request.form.get('search_term', '')
  matching_artists = Artist.query.filter(
    Artist.name.ilike(f"%{search_query}%") |
    Artist.city.ilike(f"%{search_query}%") |
    Artist.state.ilike(f"%{search_query}%")
  ).all()
  search_results = {
    "count": len(matching_artists),
    "data": []
  }

  for artist in matching_artists:
    artist_info = {}
    artist_info["name"] = artist.name
    artist_info["id"] = artist.id

    upcoming_shows_count = 0
    for show in artist.shows:
        if show.start_time > datetime.now():
            upcoming_shows_count += 1
    artist_info["upcoming_shows"] = upcoming_shows_count

    search_results["data"].append(artist_info)
  return render_template('pages/search_artists.html', results=search_results, search_term=search_query)

#  Artists Show
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: --done replace with real artist data from the artist table, using artist_id
  artist_details = Artist.query.get(artist_id)
  setattr(artist_details, "genres", artist_details.genres.split(","))  # convert genre string back to array

  # get past shows
  past_performances = list(filter(lambda performance: performance.start_time < datetime.now(), artist_details.shows))
  formatted_past_shows = []
  for performance in past_performances:
    past_show_info = {
        "venue_name": performance.venues.name,
        "venue_id": performance.venues.id,
        "venue_image_link": performance.venues.image_link,
        "start_time": performance.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    formatted_past_shows.append(past_show_info)

  setattr(artist_details, "past_shows", formatted_past_shows)
  setattr(artist_details, "past_shows_count", len(past_performances))

  # get upcoming shows
  future_performances = list(filter(lambda performance: performance.start_time > datetime.now(), artist_details.shows))
  formatted_upcoming_shows = []
  for performance in future_performances:
    upcoming_show_info = {
        "venue_name": performance.venues.name,
        "venue_id": performance.venues.id,
        "venue_image_link": performance.venues.image_link,
        "start_time": performance.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    formatted_upcoming_shows.append(upcoming_show_info)

  setattr(artist_details, "upcoming_shows", formatted_upcoming_shows)
  setattr(artist_details, "upcoming_shows_count", len(future_performances))

  return render_template('pages/show_artist.html', artist=artist_details)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: --done populate form with fields from artist with ID <artist_id>
  form = ArtistForm()  
  artist = Artist.query.get(artist_id)
  form.genres.data = artist.genres.split(",") # convert genre string back to array
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: --done take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_form = ArtistForm(request.form)

  if artist_form.validate():
    try:
      artist_to_update = Artist.query.get(artist_id)

      artist_to_update.name = artist_form.name.data
      artist_to_update.city = artist_form.city.data
      artist_to_update.state = artist_form.state.data
      artist_to_update.phone = artist_form.phone.data
      artist_to_update.genres = ",".join(artist_form.genres.data)  # convert array to string separated by commas
      artist_to_update.facebook_link = artist_form.facebook_link.data
      artist_to_update.image_link = artist_form.image_link.data
      artist_to_update.seeking_venue = artist_form.seeking_venue.data
      artist_to_update.seeking_description = artist_form.seeking_description.data
      artist_to_update.website = artist_form.website_link.data

      db.session.add(artist_to_update)
      db.session.commit()
      flash("Artist " + artist_to_update.name + " was successfully edited!")
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash("Artist was not edited successfully.")
    finally:
      db.session.close()
  else:
    print("\n\n", artist_form.errors)
    flash("Artist was not edited successfully.")

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: --done insert form data as a new Venue record in the db, instead
  # TODO: --done modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: --done on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  artist_form = ArtistForm(request.form)
  if artist_form.validate():
    try:
      new_artist_record = Artist(
        name=artist_form.name.data,
        city=artist_form.city.data,
        state=artist_form.state.data,
        phone=artist_form.phone.data,
        genres=",".join(artist_form.genres.data),  # convert array to string separated by commas
        image_link=artist_form.image_link.data,
        facebook_link=artist_form.facebook_link.data,
        website=artist_form.website_link.data,
        seeking_venue=artist_form.seeking_venue.data,
        seeking_description=artist_form.seeking_description.data,
      )
      db.session.add(new_artist_record)
      db.session.commit()
      flash("Artist " + request.form["name"] + " was successfully listed!")
    except Exception:
      db.session.rollback()
      flash("Artist was not successfully listed.")
    finally:
      db.session.close()
  else:
    print(artist_form.errors)
    flash("Artist was not successfully listed.")

  return redirect(url_for("index"))
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: --done replace with real venues data.
  show_data = []
  all_shows = Show.query.all()
  for show in all_shows:
    show_info = {
      "venue_id": show.venues.id,
      "venue_name": show.venues.name,
      "artist_id": show.artists.id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    show_data.append(show_info)
  return render_template('pages/shows.html', shows=show_data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: --done insert form data as a new Show record in the db, instead

  show_form = ShowForm(request.form)
  if show_form.validate():
    try:
      new_show_record = Show(
          artist_id=show_form.artist_id.data,
          venue_id=show_form.venue_id.data,
          start_time=show_form.start_time.data
      )
      db.session.add(new_show_record)
      db.session.commit()
      flash('Show was successfully listed!')
    except Exception:
      db.session.rollback()
      print(sys.exc_info())
      flash('Show was not successfully listed.')
    finally:
      db.session.close()
  else:
    print(show_form.errors)
    flash('Show was not successfully listed.')
  return redirect(url_for("index"))


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
