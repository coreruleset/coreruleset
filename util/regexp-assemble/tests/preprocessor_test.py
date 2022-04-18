import pytest

from lib.context import Context
from lib.processors.assemble import Assemble
from lib.processors.cmdline import CmdLine

class TestAssemblePreprocessor:
    def test_handles_ignore_case_flag(self):
        for contents in ['##!+i', '##!+ i', '##!+   i' ]:
            context = Context("")
            assemble = Assemble.create(context, [])

            assemble.process_line(contents)
            output = assemble.complete()

            assert len(output) == 1
            assert output[0] == "(?i)"

    def test_handles_no_other_flags(self):
        contents = '##!+smx'
        context = Context("")
        assemble = Assemble.create(context, [])

        assemble.process_line(contents)

        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == ''

    def test_handles_prefix_comment(self):
        contents = '''##!^ a prefix
a
b'''
        context = Context("")
        assemble = Assemble.create(context, [])

        for line in contents.splitlines():
            assemble.process_line(line)

        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == 'a prefix[ab]'

    def test_handles_suffix_comment(self):
        contents = '''##!$ a suffix
a
b'''
        context = Context("")
        assemble = Assemble.create(context, [])

        for line in contents.splitlines():
            assemble.process_line(line)

        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == '[ab]a suffix'

    def test_ignores_empty_lines(self):
        contents = '''##!+ i
some line

another line'''
        context = Context("")
        assemble = Assemble.create(context, [])

        for line in contents.splitlines():
            assemble.process_line(line)

        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == '(?i)(?:another|some) line'

    def test_returns_empty_string_for_empty_input(self):
        contents = '''##!+ _

'''
        context = Context("")
        assemble = Assemble.create(context, [])

        for line in contents.splitlines():
            assemble.process_line(line)

        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == ''

    def test_handles_backslash_escape_correctly(self):
        contents = r'\x5c\x5ca'
        context = Context("")
        assemble = Assemble.create(context, [])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'\x5c\x5ca'

    def test_always_escapes_double_quotes(self):
        contents = r'"\"\\"a'
        context = Context("")
        assemble = Assemble.create(context, [])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'\"\"\\\"a'

    def test_does_not_convert_hex_escapes(self):
        contents = r'\x48'
        context = Context("")
        assemble = Assemble.create(context, [])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'\x48'



class TestCmdLinePreprocessor:
    def test_adds_unix_escapes(self):
        contents = 'foo'
        context = Context("")
        assemble = CmdLine.create(context, ['unix'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'''f[\x5c'\"]*o[\x5c'\"]*o''' 
        
    def test_adds_windows_escapes(self):
        contents = 'foo'
        context = Context("")
        assemble = CmdLine.create(context, ['windows'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'''f[\"\^]*o[\"\^]*o'''

    def test_does_not_escape_literals(self):
        contents = '\'foo'
        context = Context("")
        assemble = CmdLine.create(context, ['windows'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == 'foo'

    def test_at_adds_windows_anti_evasion_suffix(self):
        contents = 'foo@'
        context = Context("")
        assemble = CmdLine.create(context, ['windows'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'''f[\"\^]*o[\"\^]*o[\"\^]*(?:[\s,;]|\.|/|<|>).*'''
    
    def test_at_adds_unix_anti_evasion_suffix(self):
        contents = 'foo@'
        context = Context("")
        assemble = CmdLine.create(context, ['unix'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'''f[\x5c'\"]*o[\x5c'\"]*o[\x5c'\"]*(?:\s|<|>).*'''

    def test_literal_has_precendence_over_other_operations(self):
        contents = r''''foo@.-    '''
        context = Context("")
        assemble = CmdLine.create(context, ['unix'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'foo@.-    '

    def test_period_always_escaped(self):
        contents = r'.\.\\.'
        context = Context("")
        assemble = CmdLine.create(context, ['unix'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'''\.[\x5c'\"]*\[\x5c'\"]*\.[\x5c'\"]*\[\x5c'\"]*\[\x5c'\"]*\.'''

    def test_dash_always_escaped(self):
        contents = r'-\-\\-'
        context = Context("")
        assemble = CmdLine.create(context, ['unix'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'''\-[\x5c'\"]*\[\x5c'\"]*\-[\x5c'\"]*\[\x5c'\"]*\[\x5c'\"]*\-'''

    def test_mutltiple_spaces_matched(self):
        contents = r'a b     c  e'
        context = Context("")
        assemble = CmdLine.create(context, ['unix'])

        assemble.process_line(contents)
        output = assemble.complete()

        assert len(output) == 1
        assert output[0] == r'''a[\x5c'\"]*\s+[\x5c'\"]*b[\x5c'\"]*\s+[\x5c'\"]*\s+[\x5c'\"]*\s+[\x5c'\"]*\s+[\x5c'\"]*\s+[\x5c'\"]*c[\x5c'\"]*\s+[\x5c'\"]*\s+[\x5c'\"]*e'''

    def test_fails_for_unknown_target_system(self):
        contents = 'foo'
        context = Context("")
        with pytest.raises(ValueError):
            CmdLine.create(context, ['unknown'])

        with pytest.raises(ValueError):
            CmdLine.create(context, [''])

        with pytest.raises(ValueError):
            CmdLine.create(context, [])
