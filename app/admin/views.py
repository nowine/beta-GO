from flask import render_template, url_for, request
from . import admin
from ..models import Questionnaire, Questions

@admin.route('/Quetionnnaire/<key>', methods=['GET', 'POST'])
def maint_questionnaire(key):
    pass
