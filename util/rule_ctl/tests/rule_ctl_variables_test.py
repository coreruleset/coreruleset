from .helpers import *

class TestAppendVariable:
    def test_append_variable_with_one_variable(self):
        arguments = [
            "--append-variable", "XML",
        ]
        rule_string = """
SecRule ARGS "@rx foo" "id:12"
"""
        expected = """
SecRule ARGS|XML "@rx foo" "id:12"
"""
        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_append_variable_with_existing_variables(self):
        arguments = [
            "--append-variable", "XML",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar|XML "@rx foo" "id:12"
"""
        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_append_variable_with_duplicate_variable(self):
        arguments = [
            "--append-variable", "XML",
        ]
        rule_string = """
SecRule ARGS|XML|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = rule_string

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_append_variable_with_multiple_args(self):
        arguments = [
            "--append-variable", "XML",
            "--append-variable", "DURATION",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar|XML|DURATION "@rx foo" "id:12"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)

class TestRemoveVariable:
    def test_remove_variable_with_no_variable(self):
        arguments = [
            "--remove-variable", "XML",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = rule_string
        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_remove_variable_with_existing_variable(self):
        arguments = [
            "--remove-variable", "XML",
        ]
        rule_string = """
SecRule ARGS|XML|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_remove_variable_with_multiple_args(self):
        arguments = [
            "--remove-variable", "XML",
            "--remove-variable", "DURATION",
        ]
        rule_string = """
SecRule ARGS|XML|ARGS:foo|DURATION|!ARGS:bar "@rx foo" "id:12"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


class TestReplaceVariableName:
    def test_replace_variable_name_with_no_variable(self):
        arguments = [
            "--replace-variable-name", "XML,DURATION",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = rule_string
        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_replace_variable_name_with_existing_variable(self):
        arguments = [
            "--replace-variable-name", "XML,DURATION",
        ]
        rule_string = """
SecRule ARGS|XML|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = """
SecRule ARGS|DURATION|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        context = create_context(arguments, rule_string)
        assert expected == get_output(context)
        

    def test_replace_variable_name_with_multiple_args(self):
        arguments = [
            "--replace-variable-name", "XML,ARGS:xml",
            "--replace-variable-name", "DURATION,ARGS:duration",
        ]
        rule_string = """
SecRule ARGS|XML|ARGS:foo|DURATION|!ARGS:bar "@rx foo" "id:12"
"""
        expected = """
SecRule ARGS|ARGS:xml|ARGS:foo|ARGS:duration|!ARGS:bar "@rx foo" "id:12"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)

