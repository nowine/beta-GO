from flask_admin.contrib.sqla import ModelView
from app import db
from ..models import Questions, Questionnaire, Quest_Dependency, quest_asso

question_view = ModelView(Questions, db.session)
questionnaire_view = ModelView(Questionnaire, db.session)
q_dep_view = ModelView(Quest_Dependency, db.session)
q_asso_view = ModelView(quest_asso, db.session)
