import os
import re

default_path = os.path.abspath(os.path.dirname(__file__))
default_path = os.path.join(default_path, 'config.ini')

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
    def __init__(self):
        self.result_set = set()
        self.rules = {}

    def is_comment(self, rule_string):
        """
        Parameter: String
        Return: Boolean

        Simply, if the string read from the config file start with `#`, take it as comment
        """
        return rule_string[0] == '#'

    def decode_rule(self, rule_string):
        """
        Parameter: String
        Return: BaseRule object

        The function is to split the rules factors from rule_string using regular expression.
        The rule_string uses `,` as seperator, and the parameter should be like:
            Questionnaire_key, Question_key, Check_method, Target_value, Result_code
        Create a BaseRule object with the splited list
        """
        raw_list = re.split(r',\s*', rule_string)
        return BaseRule(*raw_list)


    def load_rules(self, config_path=default_path):
        with open(config_path, 'r') as f:
            for line in f.readlines():
                if not self.is_comment(line):
                    raw_rule = self.decode_rule(line)
                    if raw_rule[0] in self.rules:
                        pass
