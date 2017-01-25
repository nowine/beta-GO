# -*- coding: utf-8 -*-

from ..models import Questionnaire, Rules

class BaseRule(object):
    def __init__(self, qnr_key, qn_key, check_method, target_value, result_code):
        self.qnr_key = qnr_key
        self.qn_key = qn_key
        self.check_method = check_method
        self.target_value = target_value
        self.result_code = result_code

    def check_rule(self, check_value):
        if self.check_method == '=':
            return self.result_code if check_value == self.target_value else None
        elif self.check_method == '>':
            return self.result_code if check_value > self.target_value else None
        elif self.check_method == '<':
            return self.result_code if check_value < self.target_value else None
        elif self.check_method == '!=':
            return self.result_code if check_value != self.target_value else None
        elif self.check_method == '>=':
            return self.result_code if check_value >= self.target_value else None
        elif self.check_method == '<=':
            return self.result_code if check_value <= self.target_value else None
        else:
            return None


class SimpleEngine(object):
    def __init__(self):
        self.engine_map = {}

    def inject(self, qnr_key):
        def decorator(f):
            self.engine_map[qnr_key] = f
            return f
        return decorator


class BaseEngine(object):
    def __init__(self, qnr_key):
        self.rules = {}
        self.qnr_key = qnr_key
        self.load_rules()

    def is_comment(self, rule_string):
        """
        Parameter: String
        Return: Boolean

        Simply, if the string read from the config file start with `#`, take it as comment
        """
        return rule_string[0] == '#'

    def load_rules(self):
        qnr = Questionnaire.query.filter_by(key=self.qnr_key).first()
        if qnr:
            for rule in qnr.rules:
                br = BaseRule(rule.questionnair.key, rule.question.key, rule.check_method,
                              rule.target_value, rule.result_code.text)
                if br.key in self.rules:
                    self.rules[br.key].append(br)
                else:
                    self.rules[br.key] = [br,]

    def chech_rules(self, answers):
        result_set = set()
        for qn_key, qn_ans in answers.iteritem():
            if qn_key in self.rules:
                for rule in self.rules[qn_key]:
                    result_set.add(rule.check_rule(qn_ans))
        return result_set


class AdultEngine(object):
    """
    This is a temporary used class to hardcode all rules for ADULT Questionnaire.
    Because the rules are hardcoded, need to initiate all fields
    """
    def __init__(self, *kwargs):
        self.full_key_list = {}
        qnr = Questionnaire.query.filter_by(key='ADULT').first()
        for qa in qnr.questions:
            self.full_key_list[qa.question.key] = qa.question.type_code

    def check_rules(self, answers):
        result_set = set()
        for key, type in self.full_key_list.items():
            if key not in answers:
                answers[key] = 0 if type == 'NUMERIC' else ''
        print(answers)
        if answers['AGE']>18:
            if (answers['空腹血糖']>=6.1 and answers['空腹血糖']<7.0) and (answers['餐后血糖']<11 and answers['餐后血糖']>0):
                result_set.add('您是糖尿病前期患者，每年有1.5\%-10.0\%的糖尿病前期患者进展为2型糖尿病')
            elif answers['RATE'] >= 25:
                result_set.add('您是糖尿病高风险人群，建议至正规医院进行口服葡萄糖耐量（OGTT）检查')
            elif answers['AGE']>=40:
                if (answers['BMI']>=24 or
                    answers['WAIST']>=90 or answers['WAIST2']>=85 or
                    answers['REL']=='A' or answers['SIT']=='B' or
                    answers['妊娠糖尿病']=='A' or answers['过大婴儿']=='A' or
                    answers['最高血压1']>=140 or answers['最高血压2']>=90 or
                    answers['血脂偏高']=='A' or answers['其他疾病']=='A' or
                    answers['卵巢']=='A' or answers['药物治疗']=='A'):
                    result_set.add('根据中国2型糖尿病防治指南，您有必要进行糖尿病筛查')
                else:
                    result_set.add('您除了年龄≥40岁外，无其他糖尿病危险因素，但根据中国2型糖尿病防治指南，依然建议您从40岁开始进行糖尿病筛查，首次筛查结果正常者，建议至少每3年重复筛查一次')
            else:
                result_set.add('根据您的回答，暂时无糖尿病危险因素。')
        return result_set


class ChildEngine(object):
    pass
