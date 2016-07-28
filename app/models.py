from app import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    mobile = db.Column(db.String(15))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role')


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
    # Definning the qeustionnaire structure
    # This class used to store the question settings, with Question body,
    # choices/rating mapping
    # choices/rating mapping would stored as JSON text
    __tablename__ = 'qn'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, index=True)
    body = db.Column(db.UnicodeText)
    answers = db.Column(db.UnicodeText)
    # Assume the option-score map would be stored as json string

    def __init__(self, *args, **kwargs):
        super(Questions, self).__init__(*args, **kwargs)

    def __repr__(self):
        try:
            return '<Questions: %i, %s, % s>' % (self.id, self.body, self.answers)
        except TypeError:
            return '<Questions (uncreated): %s, % s>' % (self.body, self.answers)

    def to_dict(self):
        d = {
            'key': self.key,
            'body': self.body,
            'answers': self.answers
        }
        return d


class Questionnaire(db.Model):
    # This class models the controlling information of questionaires, e.g. the version, name, purpose and etc
    __tablename__ = 'qnr'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, index=True)
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
