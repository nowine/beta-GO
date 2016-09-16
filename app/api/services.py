from flask import jsonify, abort, make_response, request, url_for
from . import api
from ..models import Questionnaire, Questions, Answers, User, quest_asso

# Todo:
# 1. Service to append a question into qustionnaire.
# 2. Service to remove a question from questionnaire.
# 3. Service to update a questionnaire
# 4. Service to update a question
# 5. Service to calculate questionnaire results and provide suggestion.

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({ 'error': 'Not Found' }), 404)

@api.route('/v1.0/assess/<username>')
def assess(username):
    return 'You are very healthy, %s' % username

@api.route('/v1.0/qnrs/', methods=['GET'])
def questionnaires():
    qnr_list = Questionnaire.query.all()
    qlist = []
    for qnr in qnr_list:
        summary = {'name': qnr.name,
                   'description': qnr.description,
                   'questions': url_for('api.question_list', id=qnr.id)
                   }
        qlist.append(summary)
    return jsonify({'Questionnaires': qlist})

@api.route('/v1.0/qnrs/<int:id>', methods=['GET'])
def questionnaire_summary(id):
    qn = Questionnaire.query.filter_by(id=id).first()
    summary = {'name': qn.name,
               'description': qn.description,
               'questions': url_for('api.question_list')
                }
    return jsonify({'Questionnaire': summary})

@api.route('/v1.0/qnr/<int:id>/questions', methods=['GET'])
def question_list(id):
    qnr = Questionnaire.query.filter_by(id=id).first()
    if not qnr:
        abort(404)
    questions = []
    for q in qnr.questions.order_by(quest_asso.sequence).all():
        questions.append({ 'Sequence': q.sequence,
                           'Question': q.question.to_dict()
                          })
        #questions[q.sequence] = q.question.to_dict()
    return jsonify({ 'Questions': questions })
