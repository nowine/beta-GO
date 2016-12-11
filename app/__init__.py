from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask.ext.login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigraetCommand)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# from app import views, model

# Registor blueprint
from .main import main_pages
app.register_blueprint(main_pages)

from .api import api
app.register_blueprint(api, url_prefix='/api')

from .admin import admin
app.register_blueprint(admin, url_prefix='/admin')

from .auth import auth
app.register_blueprint(auth, url_prefix='/auth')
