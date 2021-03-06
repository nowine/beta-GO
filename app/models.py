# -*- coding: utf-8 -*-

from app import db, login_manager
from flask.ext.login import UserMixin
from datetime import datetime
import json
import pdb


class User(db.Model, UserMixin):
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


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Role(db.Model):
    ADMIN = "Admin"
    USER = "User"
    REVIEWER = "Reviewer"
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role_type = db.Column(db.String(32))
    _rights = db.Column(db.UnicodeText)

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(*args, **kwargs)

    @property
    def rights(self):
        return json.loads(self._rights)

    @rights.setter
    def rights(self, dictionary):
        self._rights = json.dumps(dictionary)

    def is_admin(self):
        return self.role_type==self.ADMIN

    def __repr__(self):
        try:
            return '<Role: %i, %s, % s>' % (self.id, self.role_type, self.rights)
        except TypeError:
            return '<Role (uncreated): %s, % s>' % (self.role_type, self.rights)


class quest_asso(db.Model):
    MAP='M'
    RANGE='R'
    NA = 'N'
    # Define Association table to link up the questionnair and its questions.
    __tablename__ = 'q_asso'
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('qnr.id'),
                                 primary_key=True, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('qn.id'),
                            primary_key=True, index=True)
    sequence = db.Column(db.Integer, index=True)
    rule_type = db.Column(db.String(32))
    '''
    The _rules keeps a JSON format object for saving the detail rating logic.
    According to the `rule_type` field, the data structure will be a little different.
        if `rule_type` is MAP:
            the rules will be a map, with user answer code as key, and value is the weight
            this suitable for RADIO type answer
        if `rule_type` is RANGE:
            the rules will be a map, with user weight as key, and value is a list[2].
            in the list, list[0] is starting range, and list[1] is the ending range. When
            user input answer fall into the range,
    '''
    _rules = db.Column(db.UnicodeText)
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
            return '<quest_asso: %i, %i, %i\n%s\n%s\n%s\n%s>' % (
                self.questionnaire_id,
                self.question_id,
                self.sequence,
                self.questionnaire,
                self.question,
                self.rule_type,
                self.rules
            )
        except TypeError:
            return '<quest_asso (uncreated): %i\n%s\n%s\n%s\n%s>' % (
                self.sequence, self.questionnaire, self.question,
                self.rule_type, self.rules
            )

    @property
    def rules(self):
        if self._rules and self._rules != '':
            return json.loads(self._rules)
        else:
            return {}

    @rules.setter
    def rules(self, d):
        self._rules = json.dumps(d)

    def calculate(self, answer_value):
        if self.rule_type == self.RANGE:
            for weight, answer_range in self.rules.items():
                if len(answer_range) > 1:
                    if answer_value >= answer_range[0] and answer_value < answer_range[1]:
                        return int(weight)
                else:
                    if answer_value >= answer_range[0]:
                        return int(weight)
            else:
            # if no match
                return 0
        if self.rule_type == self.MAP:
            if answer_value in self.rules:
                return self.rules[answer_value]
            else:
                return 0


class Questions(db.Model):
    """Definning the qeustionnaire structure
    This class used to store the question settings, with Question body,
    key for searching the question, and also type of the question, and the labels.
    Currently supported question types are "RADIO", "NUMERIC" and "TEXT".
    for RADIO type of question, the label field will store a JSON format list of
    pre-defined options, with the option name and the weight.
    For the other 2 types, it should store the label of the input field and also
    other attributes to built an input field on HTML
    """
    __tablename__ = 'qn'
    SELECT_ANSWER_TYPE = "RADIO"
    NUMERIC_ANSWER_TYPE = "NUMERIC"
    TEXT_ANSWER_TYPE = "TEXT"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, index=True)
    type_code = db.Column(db.String)
    body = db.Column(db.UnicodeText)
    _labels = db.Column(db.UnicodeText, nullable=True)
    linked_to_id = db.Column(db.Integer, db.ForeignKey('qn.id'))
    linked_from = db.relationship('Questions', backref=db.backref('linked_to', remote_side=[id]))
    dependencies = db.relationship('Quest_Dependency', backref=db.backref('question'))

    @property
    def labels(self):
        if self._labels and self._labels != '':
            return json.loads(self._labels)
        return {}

    @labels.setter
    def labels(self, dic):
        self._labels = json.dumps(dic)

    # Assume the option-score map would be stored as json string
    def __init__(self, *args, **kwargs):
        super(Questions, self).__init__(*args, **kwargs)

    def __repr__(self):
        try:
            return '<Questions: %i, %s, %s>' % (self.id, self.body, self.labels)
        except TypeError:
            return '<Questions (uncreated): %s, %s>' % (self.body, self.labels)

    def to_dict(self):
        dep = []
        # pdb.set_trace()
        for d in self.dependencies:
            dep.append(d.to_dict())
        if self.linked_to_id:
            dic = {
                'key': self.key,
                'body': self.body,
                'type_code': self.type_code,
                'labels': self.labels,
                'dependencies': dep,
                'linked_to': self.linked_to.to_dict()
            }
        else:
            dic = {
                'key': self.key,
                'body': self.body,
                'type_code': self.type_code,
                'labels': self.labels,
                'dependencies': dep
            }
        return dic

    def is_required(self, qnr, answer_dict):
        """The function will be used to check whether the question is required.
        It will run throug:h the dependency relation of the question record and
        calculate until a true is received. If the no dependency record found,
        by default we can take it as true."""
        # 这个方法暂时无法满足所有情形，比如一个问题1在问卷A中依赖于问题2，
        # 但在问卷B可能会依赖于问题3，对于某一份问卷，这两个问题都会被筛选，
        # 但是问卷A中没必要检查问题3. 需要进一步设计将问卷信息一起考虑，包括
        # 正向过滤（选择当前问卷的内容），和反向过滤（去掉与本次问卷无关的内容）
        if len(self.dependencies) == 0:
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
            print(asso)
            self.questions.remove(asso)
            self.shift_sequence(asso.sequenc+1, -1)
            return self
        return None

    def insert_question(self, sequence, quest):
        # Insert quetion to a certain place, rest of question sequence would increase automatically
        # lowest priority
        if sequence < 1:
            return None
        if self.shift_sequence(sequence, 1) is not None:
            asso = quest_asso()
            asso.question = quest
            asso.sequence = sequence
            self.questions.append(asso)
            return self

    def to_dict(self):
        d = {'name': self.name,
             'key': self.key,
             'desc': self.description
            }
        return d

    def get_question(self, sequence, answer_dict=None):
        count = self.questions.count()
        # print(count)
        if sequence < 1 or sequence > count:
            raise IndexError('Sequence out of range')
        asso = self.questions.filter(
            quest_asso.sequence >= sequence).order_by(quest_asso.sequence).all()
        for a in asso:
            if a.question.is_required(self, answer_dict):
                next_seq = a.sequence < count and a.sequence+1 or 0
                return {'sequence': a.sequence,
                        'detail': a.question.to_dict(),
                        'next_seq': next_seq}

    def get_rating(self, answer_dict):
        rating = 0
        rating_list = self.questions.filter(quest_asso.rule_type != quest_asso.NA).all()
        for asso in rating_list:
            if asso.question.key in answer_dict:
                print('Question Key: %s, Rating: %i' % (asso.question.key, asso.calculate(answer_dict[asso.question.key])))
                rating = rating + asso.calculate(answer_dict[asso.question.key])
        return rating


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
    questionnaire = db.relationship('Questionnaire')
    answered_at = db.Column(db.DateTime)
    _answers = db.Column(db.UnicodeText)
    _result = db.Column(db.UnicodeText)

    @property
    def answers(self):
        if self._answers and self._answers != '':
            return json.loads(self._answers)
        return {}

    @answers.setter
    def answers(self, ans):
        self._answers = json.dumps(ans)

    def add_answer(self, ans_dict):
        answers = self.answers
        answers.update(ans_dict)
        self.answers = answers

    @property
    def result(self):
        if self._result and self._result != '':
            return json.loads(self._result)
        return {}

    @result.setter
    def result(self, res):
        self._result = json.dumps(res)


    def __init__(self, user_id, qnr_id, answers, result):
        self.user_id = user_id
        self.questionnaire_id = qnr_id

        if answers:
            self.answers = answers
        else:
            self.answers = {}

        self.result = result
        now = datetime.utcnow()
        self.answered_at = now

    def __repr__(self):
        try:
            return '<Answers: \n  id=%i,\n  user=%s,\n  questionnaire=%s,\n  answers=%s,\n  result=%s,\n  answered_at=%s>' % (
                self.id, self.user, self.questionnaire, self.answers, self.result, self.answered_at
            )
        except TypeError:
            return '<Answers(Not Created): \n  user=%s,\n  questionnaire=%s,\n  answers=%s,\n  result=%s,\n  answered_at=%s>' % (
                self.user, self.questionnaire, self.answers, self.result, self.answered_at
            )


class ResultCode(db.Model):
    __tablename__ = 'result_code'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.UnicodeText)

    def __init__(self, *args, **kwargs):
        super(ResultCode, self).__init__(*args, **kwargs)

    def __repr__(self):
        try:
            return '<ResultCode: %i, %s>' % (self.id, self.text)
        except TypeError:
            return '<ResultCode (uncreated): %s>' % (self.text)


class Rules(db.Model):
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('qnr.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('qn.id'))
    result_code_id = db.Column(db.Integer, db.ForeignKey('result_code.id'))
    check_method = db.Column(db.String(2))
    target_value = db.Column(db.String(32))
    questionnaire = db.relationship('Questionnaire', backref=db.backref('rules',
                                                      lazy='dynamic'))
    question = db.relationship('Questions', backref=db.backref('rules',
                                                      lazy='dynamic'))
    result_code = db.relationship('ResultCode', backref=db.backref('rules',
                                                      lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(Rules, self).__init__(*args, **kwargs)

    def __repr__(self):
        try:
            s = '<Rules: \n id = {id:d}\n check_method = {check_method}\n'
            'target_value = {target_value!r}\n result_code = {resultcode!r}\n'
            'questionnaire = {questionnaire!r}\n question = {question!r}\n'
            return s.format(id=self.id, check_method=self.check_method,
                            target_value=self.target_value,
                            result_code=self.result_code,
                            questionnnaire=self.questionnaire,
                            question=self.question)
        except TypeError:
            s = '<Rules: \n check_method = {check_method}\n'
            'target_value = {target_value!r}\n result_code = {resultcode!r}\n'
            'questionnaire = {questionnaire!r}\n question = {question!r}\n'
            return s.format(check_method=self.check_method,
                            target_value=self.target_value,
                            result_code=self.result_code,
                            questionnnaire=self.questionnaire,
                            question=self.question)
