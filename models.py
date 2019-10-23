from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from demo import db

from flask_login import UserMixin
from demo import login



class Episode(db.Model):

    #################################################
    # All podcast episodes
    #################################################
    __tablename__ = 'Episodes_' + str(db.ForeignKey('Podcasts.id'))

    id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pod_id = db.Column(db.Integer, db.ForeignKey('Podcasts.id'))

    epname = db.Column(db.String(128), index=True)
    epnum = db.Column(db.String(64), index=True)
    epdesc = db.Column(db.String(1024))
    audio_path = db.Column(db.String(256))
    eplink = db.Column(db.String(256), unique=True)          # episode website link

    # itunes info
    it_sum = db.Column(db.String(1024))
    it_subtitle = db.Column(db.String(256))

    def __repr__(self):
        return '<Episode {}>'.format(self.body)



class Podcast(db.Model):

    #################################################
    # podcasts
    #################################################

    __tablename__ = 'Podcasts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    username = db.Column(db.String(64))

    # basic info
    author = db.Column(db.String(64), index=True)
    podname = db.Column(db.String(128), index=True)
    podlink = db.Column(db.String(256), unique=True)
    image_path = db.Column(db.String(512))
    poddesc = db.Column(db.String(1024))
    buildtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    rsslink = db.Column(db.String(256), unique=True)

    # itunes info
    it_own_name = db.Column(db.String(64))
    it_own_email = db.Column(db.String(256))
    it_cat = db.Column(db.String(128))
    it_subcat = db.Column(db.String(128))
    it_sum = db.Column(db.String(1024))
    it_subtitle = db.Column(db.String(256))
    it_keys = db.Column(db.String(512))
    it_explicit = db.Column(db.String(32))

    pod_eps = db.relationship('Episode', backref='Podcasts', lazy='dynamic')

    def __repr__(self):
        return '<Podcast {}>'.format(self.body)



class User(UserMixin, db.Model):

    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # Backref must be the same as the Table name?
    user_pods = db.relationship('Podcast', backref='Users', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))
