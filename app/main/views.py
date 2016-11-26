from flask import render_template, url_for, request, redirect, flash, g
from flask.ext.login import login_required, current_user
from . import main_pages
from ..models import Questionnaire, Questions, User
from app import db
from app import login_manager

@main_pages.route('/')
@main_pages.route('/index')
@main_pages.route('/index/<int:user_id>')
def index(user_id=0):
    return render_template('index.html')

#@main_pages.route('/questionnaire/<key>', methods=['GET', 'POST'])
@main_pages.route('/questions/<key>', methods=['GET', 'POST'])
def load_questions(key):
    qn = Questionnaire.query.filter_by(key=key).first()
    if qn:
        if request.method == 'GET':
            #return render_template('questionnaire.html', qn=qn)
            return render_template('questions.html', qn=qn)
        if request.method == 'POST':
            print(request.form)
            score=0
            for (key, value) in request.form.items():
                score = score + int(value)
            return render_template('result.html', score=score)
    return redirect(url_for('main_pages.index'))

@main_pages.route('/qlist', methods=['GET'])
def qnr_list():
    qlist = Questionnaire.query.all()
    return render_template('qnr_list.html', qlist=qlist)

@main_pages.before_request
def before_request():
    g.user = current_user

@main_pages.route('/qnr/<key>', methods=['GET', 'POST'])
@login_required
def load_qnr(key):
    qnr = Questionnaire.query.filter_by(key=key).first()
    if qnr:
        if request.method == 'GET':
            return render_template('qnr.html', qnr=qnr)
        if request.method == 'POST':
            if g.user is not None and g.user.is_authenticated():
                print(request.__dict__)
                answers = request.json['answers']
                print(answers)
                return redirect(url_for('main_pages.index'))
    flash('该问卷不存在，请重新选择问卷')
    return redirect(url_for('main_pages.index'))
