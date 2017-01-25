from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask.ext.login import LoginManager
from flask_admin import Admin

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

admin = Admin(app, template_mode='bootstrap3')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# from app import views, model

# Registor blueprint
from .main import main_pages
app.register_blueprint(main_pages)

from .api import api
app.register_blueprint(api, url_prefix='/api')

#from .admin import admin
#app.register_blueprint(admin, url_prefix='/admin')

from .auth import auth
app.register_blueprint(auth, url_prefix='/auth')

from .administration import question_view, questionnaire_view,q_dep_view, q_asso_view
from .administration import rules_view, result_code_view
admin.add_view(question_view)
admin.add_view(questionnaire_view)
admin.add_view(q_dep_view)
admin.add_view(q_asso_view)
admin.add_view(rules_view)
admin.add_view(result_code_view)
