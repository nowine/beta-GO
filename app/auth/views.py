# -*- coding: utf-8 -*-

from flask import render_template, request, url_for, flash, redirect
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm, RegistrationForm
from app import db
from . import auth
from ..models import User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        user = User.query.filter_by(mobile = form.mobile.data).first()
        print(user)
        if user is not None:
            login_user(user, True) #Always remember the user login
            return redirect(request.args.get('next') or url_for('main_pages.index'))
        return redirect(url_for('main_pages.registration'))
    return render_template('login.html', title="登录", form=form)

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('你已成功退出登录')
    return redirect(url_for('main_pages.index'))

@auth.route('/registration', methods=['GET', 'POST'])
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
        login_user(user)
        return redirect(url_for('main_pages.index'))
    return render_template("register.html", title="注册", form=form)
