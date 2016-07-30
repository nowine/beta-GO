from flask import render_template
from . import main_pages
from ..models import Questionnaire, Questions

@main_pages.route('/')
@main_pages.route('/index')
def index():
    return 'Hello world, this is my first blueprint'

@main_pages.route('/questionnaire/<key>')
def load_questions(key):
    qn = Questionnaire.query.filter_by(key=key).first()
    print(qn)
    for q in qn.questions:
        print(q.question)
        print(q.question.answers)
        for (k, v) in q.question.answers.items():
            print('%s: %i' % (k, v))
    return render_template('questionnaire.html', qn=qn)
