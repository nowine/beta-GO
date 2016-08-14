from flask import render_template, url_for, request
from . import main_pages
from ..models import Questionnaire, Questions

@main_pages.route('/')
@main_pages.route('/index')
def index():
    return 'Hello world, this is my first blueprint'

@main_pages.route('/questionnaire/<key>', methods=['GET', 'POST'])
def load_questions(key):
    qn = Questionnaire.query.filter_by(key=key).first()
    if qn:
        if request.method == 'GET':
            return render_template('questionnaire.html', qn=qn)
        if request.method == 'POST':
            print(request.form)
            score=0
            for (key, value) in request.form.items():
                score = score + int(value)
            return render_template('result.html', score=score)



