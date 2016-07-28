from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# from app import views, model

# Registor blueprint
from .main import main_pages
app.register_blueprint(main_pages)

from .api import api
app.register_blueprint(api, url_prefix='/api')


