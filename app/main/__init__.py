from flask import Blueprint

main_pages = Blueprint('main_pages', __name__,
                       template_folder='../templates/main',
                       static_folder='../static')

from . import views
