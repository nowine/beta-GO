from flask import jsonify, abort, make_response, request
from . import api
from ..models import Questionnaire, Questions, Answers, User

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


@api.route('/v1.0/qnr/summary/<key>', methods=['GET'])
def questionnaire_summary(key):
    qn = Questionnaire.query.filter_by(key=key).first()
    summary = {'name': qn.name,
               'description': qn.description}
    return jsonify({'Questionnaire': summary})


@api.route('/v1.0/qnr/<id>/questions', methods=['GET'])
def question_list(id):
    qlist = Questionnaire.query.filter_by(id=id).first().questions
    d = {}
    for q in qlist:
        d[q.sequence] = q.question.to_dict()
    return jsonify({ 'Questions': d })


# @api.route('/v1.0/questionnaire/<key>/questions', methods=['GET'])
@api.route('/v1.0/questionnaire/<qn_id>/questions/<int:seq>/user/<int:user_id>', methods=['GET'])
def get_questions_for_user(qn_id, user_id, seq=1):
    """Receive id and seq, id will be used to filter the questionnaire, while seq is use to
    determine which question should be loaded. If the seq is not provided in the URI, by
    default load the 1st question"""
    qn = Questionnaire.query.filter_by(id=id).first()
    ans = Answers.query.filter_by(user_id=user_id, questionnaire_id=id).first()
    quest = qn.get_question(seq, ans.answers)
    return jsonify({ 'next_seq': quest[1], 'question': quest[2].to_dict() })


@api.route('/v1.0/questionnaire/<qn_id>/questions/<int:seq>/user/<int:user_id>', methods=['POST'])
def answer_questions_of_user(qnr_id, user_id, seq=1):
    #Validate user existence before appending answer
    if not request.json or not 'key' in request.json or not 'answer' in request.json:
        abort(400)
    usr = User.query.filter_by(id=user_id).first()
    if not usr:
        abort(404)
    ans = usr.answers.filter_by(questionnair_id=qnr_id).first()
    if not ans:
        ans = Answer()
        ans.user_id = usr.id
        ans.questionnaire_id = qn_id

