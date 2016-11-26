# -*- coding: utf-8 -*-

import re
from flask_wtf import Form
from wtforms import StringField, SelectField, IntegerField, validators
from ..models import User


class LoginForm(Form):
    mobile = StringField("手机", validators=[validators.Required()])

    def validate(self):
        if not Form.validate(self):
            print('testing')
            return False
        _mobile = self.mobile.data
        if not re.match(r'^1[3|4|5|7|8]\d{9}$', _mobile):
            self.mobile.errors.append("电话号码格式有误，请重新输入")
            return False
        return True


class RegistrationForm(Form):
    mobile = StringField("手机", validators=[validators.Required()])
    name = StringField("姓名", validators=[validators.Required(),
                                           validators.Length(max=50)])
    age = IntegerField("年龄", validators=[validators.Required()])
    gender = SelectField("性别", validators=[validators.required()],
                         choices=[('M',"男"), ('F', "女")])

    def validate(self):
        if not Form.validate(self):
            return False
        _mobile = self.mobile.data
        if not re.match(r'^1[3|4|5|7|8]\d{9}$', _mobile):
            self.mobile.errors.append("电话号码格式有误，请重新输入")
            return False
        user = User.query.filter_by(mobile=_mobile).first()
        if user != None:
            self.mobile.errors.append("该号码已存在，请尝试登录")
            return False
        return True
