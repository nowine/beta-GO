#!flask/bin/python
# -*- coding: utf-8 -*-

from app import app, db
from app.models import Questionnaire, Questions, quest_asso


def test_db_init():
    quest1 = Questions(body='问题A', key='A', answers='答案A')
    quest2 = Questions(body='问题B', key='B', answers='答案B')
    quest3 = Questions(body='问题C', key='C', answers='答案C')
    db.session.add(quest1)
    db.session.add(quest2)
    db.session.add(quest3)

    qn1 = Questionnaire(name='问卷A', key='A', description='问卷测试A')
    qn2 = Questionnaire(name='问卷B', key='B', description='问卷测试B')
    db.session.add(qn1)
    db.session.add(qn2)

    db.session.commit()

    qn1.append_question(quest1)
    qn2.append_question(quest2)
    qn1.append_question(quest3)
    qn2.append_question(quest3)

    db.session.add(qn1)
    db.session.add(qn2)
    db.session.commit()

if __name__ == '__main__':
    test_db_init()
