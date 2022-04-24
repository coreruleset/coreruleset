import pytest

from lib.context import Context
from lib.operators.assembler import Assembler, Peekerator
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

    def test_assembling_1(self):
        contents = '''##!^ \W*\(
##!^ two
a+b|c
d
'''
        context = Context("")
        assembler = Assembler(context)

        output = assembler._run(Peekerator(contents.splitlines()))
        assert output == '\W*\(two(?:a+b|c|d)'

    def test_assembling_2(self):
        contents = '''##!$ \W*\(
##!$ two
a+b|c
d
'''
        context = Context("")
        assembler = Assembler(context)

        output = assembler._run(Peekerator(contents.splitlines()))
        assert output == '(?:a+b|c|d)\W*\(two'

    def test_assembling_3(self):
        contents = '''##!> assemble concat
line1
##!=>
  ##!> assemble
ab
cd
  ##!<
##!<
'''
        context = Context("")
        assembler = Assembler(context)

        output = assembler._run(Peekerator(contents.splitlines()))
        assert output == 'line1(?:ab|cd)'

class TestAssembleConcatPreprocessor:
    def test_fails_for_unknown_type(self):
        context = Context("")
        with pytest.raises(ValueError):
            Assemble.create(context, ['unknown'])

    def test_concatenating(self):
        contents = '''##!> assemble concat
one
two
##!=>
three
four
##!<
five
'''
        context = Context("")
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 2
        assert output == [
            '(?:one|two)(?:three|four)',
            'five'
        ]

    def test_concatenating_multiple_segments(self):
        contents = '''##!> assemble concat
one
two
##!=>
three
four
##!=>
five
##!=>
  ##!> assemble concat
six
seven
  ##!=>
eight
nine
  ##!<
##!=>
ten
##!<
'''
        context = Context("")
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 1
        assert output[0] == '(?:one|two)(?:three|four)fives(?:even|ix)(?:eight|nine)ten'
        
    def test_concatenating_multiple_segments_(self):
        contents = '''##!> assemble concat
one
two
##!=>
three
four
##!=>
five
##!=>
  ##!> assemble concat
six
seven
  ##!=>
eight
nine
  ##!<
ten
##!<
'''
        context = Context("")
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 1
        assert output[0] == '(?:one|two)(?:three|four)five(?:s(?:even|ix)(?:eight|nine)|ten)'

    def test_concatenating_with_stored_input(self):
        contents = '''##!> assemble concat
##! slash patterns
\x5c
##! URI encoded
%2f
%5c
##!=< slashes
##!=> slashes

##! dot patterns
\.
\.%00
\.%01
##!=>
##!=> slashes
'''
        context = Context("")
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 1
        assert output[0] == '(?:%(?:2f|5c)|\\)\\.(?:%0[01])?(?:%(?:2f|5c)|\\)'

    def test_stored_input_is_global(self):
        contents = '''##!> assemble concat
ab
cd
##!=< globalinput
##!<

##!> assemble concat
##!=> globalinput
'''
        context = Context("")
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 1
        assert output[0] == '(?:ab|cd)'

    def test_stored_input_isnt_available_to_inner_scope(self):
        contents = '''##!> assemble concat
ab
cd
##!=< globalinput
    ##!> assemble concat
    ##!=> globalinput
    ##!<
##!<
'''
        context = Context("")
        assembler = Assembler(context)

        with pytest.raises(KeyError):
            assembler.preprocess(Peekerator(contents.splitlines()))

    def test_stored_input_is_available_to_outer_scope(self):
        contents = '''##!> assemble concat
  ##!> assemble concat
ab
cd
  ##!=< globalinput
  ##!<
##!=> globalinput
'''
        context = Context("")
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 1
        assert output[0] == '(?:ab|cd)'

    def test_concatenating_fails_when_input_unknown(self):
        contents = '''##!> assemble concat
##!=> unknown
'''
        context = Context("")
        assembler = Assembler(context)

        with pytest.raises(KeyError):
            assembler.preprocess(Peekerator(contents.splitlines()))


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
        context = Context("")
        with pytest.raises(ValueError):
            CmdLine.create(context, ['unknown'])

        with pytest.raises(ValueError):
            CmdLine.create(context, [''])

        with pytest.raises(ValueError):
            CmdLine.create(context, [])
