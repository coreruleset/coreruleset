from .helpers import *

class TestFilterRuleId:
    def test_filter_rule_id_exact_match(self):
        arguments = [
            "--filter-rule-id", "12",
            "--append-tag", "foo"
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12,tag:'foo'"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_filter_rule_id_prefix_match(self):
        arguments = [
            "--filter-rule-id", "^12",
            "--append-tag", "foo"
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:122"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:122,tag:'foo'"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_filter_rule_id_suffix_match(self):
        arguments = [
            "--filter-rule-id", ".*22$",
            "--append-tag", "foo"
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:122"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:122,tag:'foo'"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_filter_rule_id_no_match(self):
        arguments = [
            "--filter-rule-id", "11",
            "--append-tag", "foo"
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = rule_string

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)
