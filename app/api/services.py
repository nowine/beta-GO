from flask import jsonify
from . import api
from ..models import Questionnaire, Questions

# Todo:
# 1. Service to append a question into qustionnaire.
# 2. Service to remove a question from questionnaire.
# 3. Service to update a questionnaire
# 4. Service to update a question
# 5. Service to calculate questionnaire results and provide suggestion.

@api.route('/assess/<username>')
def assess(username):
    return 'You are very healthy, %s' % username

@api.route('/questionnaire/<key>', methods=['GET'])
def questionnaire_summary(key):
    qn = Questionnaire.query.filter_by(key = key).first()
    return jsonify({ 'Questionnaire': qn.to_dict() })

@api.route('/questionnaire/<key>/questions', methods=['GET'])
def question_list(key):
    qlist = Questionnaire.query.filter_by(key=key).first().questions
    d = {}
    for q in qlist:
        d[q.sequence] = q.question.to_dict()
    return jsonify({ 'Questions': d })
