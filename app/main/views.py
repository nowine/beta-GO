from flask import render_template, url_for, request, redirect, flash
from . import main_pages
from .forms import RegistrationForm
from ..models import Questionnaire, Questions, User
from app import db

@main_pages.route('/')
@main_pages.route('/index')
@main_pages.route('/index/<int:user_id>')
def index(user_id=0):
    return render_template('index.html')

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
    return redirect(url_for('/index'))

@main_pages.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(form.mobile.data,
                    form.name.data,
                    form.age.data,
                    form.gender.data)

        db.session.add(user)
        db.session.commit()
        flash("注册成功")
        return redirect(url_for('main_pages.index'))
    return render_template("register.html", title="注册", form=form)

@main_pages.route('/qlist', methods=['GET'])
def qnr_list():
    qlist = Questionnaire.query.all()
    return render_template('qnr_list.html', qlist=qlist)

