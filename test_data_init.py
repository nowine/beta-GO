#!flask/bin/python
# -*- coding: utf-8 -*-

from app import app, db
from app.models import Questionnaire, Questions


def test_db_init():
    answer = {0: u"19-24岁",
              4: u"25-34岁",
              8: u"35-39岁",
              11: u"40-44岁",
              12: u"45-49岁",
              13: u"50-54岁",
              15: u"55-59岁",
              16: u"60-64岁",
              18: u"65-74岁"}
    quest1 = Questions(body=u"年龄", key='AGE', answers=answer)
    answer = {2: u"男", 0: u"女"}
    quest2 = Questions(body=u"性别", key='GENDER', answers=answer)
    answer = {0: u"BMI<22",
              1: u"BMI 22.0-23.9",
              3: u"BMI 24.0-29.9",
              5: u"BMI > 30"}
    quest3 = Questions(body="BMI", key="BMI", answers=answer)
    db.session.add(quest1)
    db.session.add(quest2)
    db.session.add(quest3)

    answer = {0: u"<75",
              3: u"75.0-79.9",
              5: u"80.0-84.9",
              7: u"85.0-89.9",
              8: u"90.0-94.9",
              10: u">=95.0"}
    quest4 = Questions(body=u"腰围（厘米）", key="WAIST", answers=answer)
    db.session.add(quest4)

    qn1 = Questionnaire(name=u"糖尿病人高位人群自我筛查问卷", key="ADULT", description=u"成人版")
    db.session.add(qn1)

    db.session.commit()

    qn1.append_question(quest1)
    qn1.append_question(quest2)
    qn1.append_question(quest3)
    qn1.append_question(quest4)

    db.session.add(qn1)
    db.session.commit()

if __name__ == '__main__':
    test_db_init()
