#!flask/bin/python
# -*- coding: utf-8 -*-

import os
import unittest

from config import basedir
from app import app, db
from app.models import Questionnaire, Questions, quest_asso


class Tests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_quest_relationship(self):
        quest1 = Questions(body='问题A', answers='答案A')
        quest2 = Questions(body='问题B', answers='答案B')
        quest3 = Questions(body='问题C', answers='答案C')
        db.session.add(quest1)
        db.session.add(quest2)
        db.session.add(quest3)

        qn1 = Questionnaire(name='问卷A', description='问卷测试A')
        qn2 = Questionnaire(name='问卷B', description='问卷测试B')
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

        assert quest3.questionnaires.count() ==2
        assert qn1.questions.count() == 2
        assert qn2.questions.count() == 2
        assert qn1.questions.first().sequence == 1
        assert qn1.has_question(quest1.id)
        assert qn1.questions.first().question.body == '问题A'
        assert qn1.has_question(quest1.id)

        assert qn1.append_question(quest1) == None

        quest4 = Questions(body='问题D', answers='答案D')
        db.session.add(quest4)
        db.session.commit()

        qn1.append_question(quest4)
        db.session.add(qn1)
        db.session.commit()


        assert qn1.questions.count() == 3
        # print(qn1.questions.filter(quest_asso.question_id == quest4.id).first())
        assert qn1.questions.filter(quest_asso.question_id == quest4.id).first().sequence == 3

        assert qn1.shift_sequence(3, -1) == None
        asso_list = qn1.shift_sequence(3, 1)
        assert asso_list[0].sequence == 4
        assert qn1.questions.filter(quest_asso.sequence == 3).first() is None
        asso_list = qn1.shift_sequence(4, -1)
        assert asso_list[0].sequence == 3
        assert qn1.questions.filter(quest_asso.sequence == 3).first() is not None

        qn1.remove_question(quest4)
        db.session.add(qn1)
        db.session.commit()
        assert qn1.questions.count() == 2


if __name__ == '__main__':
    unittest.main()








