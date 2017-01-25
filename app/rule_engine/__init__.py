from .engines import AdultEngine

rules_map = {}
#qnrs = Questionnaire.query.all()
#for qnr in qnrs:
#    rules_map[qnr.key] = BaseEngine(qnr.key)

rules_map['ADULT'] = AdultEngine()

