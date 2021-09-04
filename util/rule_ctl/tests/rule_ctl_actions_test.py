from .helpers import *

class TestReplaceAction:
    def test_replace_action_with_no_actions(self):
        arguments = [
            "--replace-action", "msg:foo,msg:bar",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar "@rx foo" "id:12"
"""
        expected = rule_string

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_replace_action_with_existing_actions(self):
        arguments = [
            "--replace-action", "msg:foo,msg:bar",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    msg:bar,\\
    log:'abc'"
"""
        expected = rule_string
        
        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_replace_action_with_duplicate_action(self):
        arguments = [
            "--replace-action", "msg:foo,msg:bar",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    msg:'foo',\\
    msg:'abc'"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    msg:'bar',\\
    msg:'abc'"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_replace_action_with_different_name(self):
        arguments = [
            "--replace-action", "msg:foo,deny",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    msg:'foo',\\
    msg:'abc'"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    deny,\\
    msg:'abc'"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)

        arguments = [
            "--replace-action", "deny,msg:foo",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    deny,\\
    msg:'abc'"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    msg:foo,\\
    msg:'abc'"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)


    def test_replace_action_without_values(self):
        arguments = [
            "--replace-action", "pass,deny",
        ]
        rule_string = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    pass,\\
    msg:'abc'"
"""
        expected = """
SecRule ARGS|ARGS:foo|!ARGS:bar \\
    "@rx foo" \\
    "id:12,\\
    deny,\\
    msg:'abc'"
"""

        context = create_context(arguments, rule_string)
        assert expected == get_output(context)