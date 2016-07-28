from flask import Blueprint

main_pages = Blueprint('main_pages', __name__, template_folder='templates', static_folder='statics')

from . import views 
