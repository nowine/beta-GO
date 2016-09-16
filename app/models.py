# -*- coding: utf-8 -*-

from app import db
import json

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(15), index=True)
    name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role')

    def __init__(self, mobile, name, age, gender):
        self.mobile = mobile
        self.name = name
        self.age = age
        self.gender = gender

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User: %r>' % self.name




class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)


class quest_asso(db.Model):
    # Define Association table to link up the questionnair and its questions.
    __tablename__ = 'q_asso'
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('qnr.id'),
                                 primary_key=True, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('qn.id'),
                            primary_key=True, index=True)
    sequence = db.Column(db.Integer, index=True)
    questionnaire = db.relationship('Questionnaire',
                                    backref=db.backref('questions',
                                                       lazy='dynamic',
                                                       cascade='delete, delete-orphan'))
    question = db.relationship('Questions',
                               backref=db.backref('questionnaires',
                                                  lazy='dynamic'))
                                                  #cascade='delete, delete-orphan'))
        # Why I got SAWarning: Object of type <quest_asso> not in session, add
        # operation along 'Questionnaire.questions' will not proceed   error if
        # question's cascade is turned on when user Questionnaire.questions
        # relationship set as cascode delete and delete orphan, a question to
        # be ask on stackoverflow.

    def __repr__(self):
        try:
            return '<quest_asso: %i, %i, %i\n%s\n%s>' % (
                self.questionnaire_id,
                self.question_id,
                self.sequence,
                self.questionnaire,
                self.question)
        except TypeError:
            return '<quest_asso (uncreated): %i\n%s\n%s>' % (
                self.sequence, self.questionnaire, self.question
                )


class Questions(db.Model):
    """Definning the qeustionnaire structure
    This class used to store the question settings, with Question body,
    key for searching the question, and also type of the question answers,
    the answers column is optionnal, only useful when the type_code is
    `SELECT_ANSWER_TYPE`, the choices/rating mapping would stored in answers field
    in JSON format
    """
    __tablename__ = 'qn'
    SELECT_ANSWER_TYPE = 1
    BOOLEAN_ANSWER_TYPE = 2
    VALUE_ANSWER_TYPE = 3
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, index=True)
    type_code = db.Column(db.Integer)
    body = db.Column(db.UnicodeText)
    _answers = db.Column(db.UnicodeText, nullable=True)
    dependencies = db.relationship('Quest_Dependency')

    @property
    def answers(self):
        d = json.loads(self._answers)
        return d

    @answers.setter
    def answers(self, dict):
        self._answers = json.dumps(dict)

    # Assume the option-score map would be stored as json string
    def __init__(self, *args, **kwargs):
        super(Questions, self).__init__(*args, **kwargs)

    def __repr__(self):
        try:
            return '<Questions: %i, %s, % s>' % (self.id, self.body, self.answers)
        except TypeError:
            return '<Questions (uncreated): %s, % s>' % (self.body, self.answers)

    def to_dict(self):
        dep = []
        for d in self.dependencies:
            dep.append(d.to_dict())
        dic = {
            'key': self.key,
            'body': self.body,
            'type_code': self.type_code,
            'answers': self.answers,
            'dependencies': dep
            }
        return dic

    def is_required(self, qnr, answer_dict):
        """The function will be used to check whether the question is required.
        It will run through the dependency relation of the question record and
        calculate until a true is received. If the no dependency record found,
        by default we can take it as true."""
        # 这个方法暂时无法满足所有情形，比如一个问题1在问卷A中依赖于问题2，
        # 但在问卷B可能会依赖于问题3，对于某一份问卷，这两个问题都会被筛选，
        # 但是问卷A中没必要检查问题3. 需要进一步设计将问卷信息一起考虑，包括
        # 正向过滤（选择当前问卷的内容），和反向过滤（去掉与本次问卷无关的内容）
        if self.dependencies.count() == 0:
            return True
        required = False
        affected = True
        hit_dependency = 0
        for dep in self.dependencies:
            if dep.is_affecting(qnr):
                required = required or dep.check_dependency(answer_dict)
                hit_dependency += 1
            else:
                affected = False

        if hit_dependency == 0 and not affected:
            # 所有Dependency都不影响当前问卷，则Return True
            return True
        return required
            # 有问卷受影响，则对每个Dependency进行 OR
            # 运算，只要有任意一个问题为真，则 required，


class Questionnaire(db.Model):
    """ This class models the controlling information of questionaires,
    e.g. the version, name, purpose and etc
    """
    __tablename__ = 'qnr'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(10), index=True)
    name = db.Column(db.UnicodeText)
    description = db.Column(db.UnicodeText)

    def __init__(self, *args, **kwargs):
        super(Questionnaire, self).__init__(*args, **kwargs)

    def __repr__(self):
        try:
            return '<Questionnaire: %i, %s, %s>' % (self.id, self.name, self.description)
        except TypeError:
            return '<Questionnaire (uncreated): %s, %s>' % (self.name, self.description)

    def has_question(self, quest_id):
        return self.questions.filter(quest_asso.question_id == quest_id).count() > 0

    def append_question(self, quest):
        # Validate if the the question already in questionnaire before adding question in
        if not self.has_question(quest.id):
            sequence = self.questions.count() + 1
            asso = quest_asso()
            asso.sequence = sequence
            asso.question = quest
            self.questions.append(asso)
            return self

    def shift_sequence(self, starting, shift):
        '''
        The method is used to update the questions sequence within the questionnaire,
        it receive parameters:
            starting - point of the sequence(from which the sequence need to be shifted),
            shift - the steps to be shifted

        Validations:
            starting should be greater then 0, the every beginning of the sequence
            and after shifting, the new sequence number must not less then 1
            and the new sequence number should be vacoon.
        '''
        if starting < 1:
            return None
        if starting + shift < 1:
            return None
        if shift < 0:
            # shift_size < 0 means update the seqence smaller, before doing it,
            # need to ensure those records not exists.
            if self.questions.filter(quest_asso.sequence>=starting+shift, quest_asso.sequence<starting).count() > 0:
                return None
        asso_list = self.questions.filter(quest_asso.sequence >= starting).all()
        for asso in asso_list:
            asso.sequence = asso.sequence + shift
        return asso_list

    def remove_question(self, quest):
        # remove the question from questionnaire, should support removed by sequence, or removed by question_id?
        if self.has_question(quest.id):
            asso = self.questions.filter(quest_asso.question_id == quest.id).first()
            self.questions.remove(asso)
            return self

    def insert_question(self, sequence, quest):
        # Insert quetion to a certain place, rest of question sequence would increase automatically
        # lowest priority
        if sequence < 1:
            return None
        if self.shift_sequence(sequence, 1) is not None:
            asso = quest_asso()
            asso.question = quest
            self.questions.append(asso)
            return self

    def to_dict(self):
        d = {'name': self.name,
             'key': self.key,
             'desc': self.description
            }
        return d

    def get_question(self, sequence, answer_dict=None):
        if sequence < 1 or sequence > self.questions.count():
            raise IndexError('Sequence out of range')
        asso = self.questions.filter_by(
            quest_asso.sequence >= sequence).order_by(quest_asso.sequence).all()
        for a in asso:
            if a.question.is_required():
                return (a.sequence, a.question)


class Quest_Dependency(db.Model):
    """This class is used to maintenance the dependency whether a questions should
    be asked. Usually, it depends on the answer previous questions to determine
    whether to asked the question, or not.
    As one question might be depends on different questions in different questionnaire,
    so create a dedicated model to keep such relationship.
    """
    __tablename__ = 'qz_depend'
    GREATER_THAN = 'GT'
    LESS_THAN = 'LT'
    EQUAL_TO = 'EQ'
    NOT_EQAUL_TO = 'NE'
    GREATER_EQUAL = 'GE'
    LESS_EQUAL = 'LE'
    FUNCTION = 'FN'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('qn.id'), index=True)
    check_method = db.Column(db.String(2))
    check_value = db.Column(db.String(64))
    check_against = db.Column(db.String(64))
    # The check against would be used record which question's answer would be
    # checked. Not using the question id because expecting get the answer dict
    # using question's key as the answer key too
    affecting_all = db.Column(db.Boolean)
    # Assumption, if there is multiple dependency, it should be an `or` logic
    affected_qnr = db.Column(db.Text, nullable=True)

    def append_qnr(self, qnr_key):
        if self.affected_qnr is None:
            self.affected_qnr = qnr_key
            return self.append_qnr
        self.affected_qnr = "%s|%s" % (self.affected_qnr, qnr_key)
        return self.append_qnr

    def is_affecting(self, qnr_key):
        return self.affecting_all or self.affected_qnr.find(qnr_key)

    def check_dependency(self, answer_dict, fn=None):
        # The method supports equal, not equal and function checking only. For
        # other checking method, would be implemented in future
        # Check if the preceding question has been answer, if not then return
        # False, as we assume the depending question should be asked
        # previously.
        if not answer_dict[self.check_against]:
            return False
        if self.check_method == self.EQUAL_TO:
            return answer_dict[self.check_against] == self.check_value
        if self.check_method == self.NOT_EQUAL_TO:
            return answer_dict[self.check_against] != self.check_value

    def to_dict(self, qnr_key=None):
        dependence = {'check_method': self.check_method,
                      'check_against': self.check_against,
                      'check_value': self.check_value,
                      'affecting_all': self.affecting_all,
                      'affected_qnr': self.affected_qnr
                      }
        if not qnr_key or self.is_affecting(qnr_key):
            return dependence
        else:
            return {}

class Answers(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('qnr.id'), index=True)
    user = db.relationship('User', backref=db.backref('answers',
                                                      lazy='dynamic'))
    _answers = db.Column(db.UnicodeText)
    result = db.Column(db.UnicodeText)

    @property
    def answers(self):
        return json.loads(self._answers)

    @answers.setter
    def answers(self, ans):
        self._answers = json.dumps(ans)

    def add_answer(self, key, value):
        answers = self.answers
        answers[key]=value
        self.answers = answers

    def __init__(self, user_id, qnr_id, answers):
        self.user_id = user_id
        self.questionnaire_id = qnr_id
        if answers:
            self.answers = answers
        else:
            self.answers = {}
