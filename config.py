import os

# For SQLite
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #########################################################
    # NEED TO SET ENVIROMENTAL VARIABLE FOR SECRET_KEY
    #########################################################
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-7634647'

    # For SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
