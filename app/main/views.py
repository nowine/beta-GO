from flask import render_template, url_for, request, redirect, flash, g, abort
from flask.ext.login import login_required, current_user
from . import main_pages
from ..models import Questionnaire, Questions, User, Answers
from app import db
from app import login_manager
from app.rule_engine import rules_map

import json

@main_pages.route('/')
@main_pages.route('/index')
@main_pages.route('/index/<int:user_id>')
def index(user_id=0):
    return render_template('index.html')

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

@main_pages.route('/result/<key>', methods=['POST'])
def get_result(key):
    print(request)
    if not request.form or not 'answers' in request.form:
        abort(400)
    print(request.form)
    answers = request.form['answers']
    print(answers)
    answers = json.loads(answers)
    qnr = Questionnaire.query.filter_by(key=key).first()
    if not qnr:
        abort(400)
    rating = qnr.get_rating(answers)
    answers['RATE'] = rating
    result = rules_map[qnr.key].check_rules(answers)
    answer = Answers(g.user.id, qnr.id, answers, str(result))
    db.session.add(answer)
    db.session.commit()
    return render_template('result_page.html', qnr=qnr, result=result)
