from . import main_pages
from ..models import Questionnaire, Questions

@main_pages.route('/')
@main_pages.route('/index')
def index():
    return 'Hello world, this is my first blueprint'


@main_page.route('/questionnaire/<key>')
def load_questions(key):
    pass
