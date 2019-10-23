from flask import Flask
from config import Config

from flask_login import LoginManager

# For SQLite
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

# For SQLite
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

import routes, models

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

