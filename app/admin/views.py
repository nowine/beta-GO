from flask import render_template, url_for, request, flash
from flask.ext.login import login_required, current_user
from . import admin
from ..models import Questionnaire, Questions
from app import db

@admin.before_request
def before_request():
    g.user = current_user

@admin.route('/Quetionnnaire/<key>', methods=['GET', 'POST'])
def maint_questionnaire(key):
    if g.user.role.is_admin():
        pass
    else:
        flash("当前用户无权限访问该功能")
        return redirect(url_for("main_pages.index"))
