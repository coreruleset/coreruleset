import pytest
from lib.operators.assembler import Assembler, Peekerator
from lib.context import Context

class TestFileFormat:
    def test_preprocess_ignores_simple_comments(self):
        contents = '''##!line1
##! line2
##!\tline3
'''
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(contents.splitlines().__iter__()))

        assert len(output) == 0

    def test_preprocess_does_not_ignore_special_comments(self):
        contents = '''##!+i
##!+ smx
##!^prefix
##!^ prefix
##!$suffix
##!$ suffix
'''
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(contents.splitlines().__iter__()))

        assert output == contents.splitlines()


    def test_preprocess_does_not_require_comments_to_start_line(self):
        contents = '''##!line1
 ##! line2
 not blank ##!+smx 
\t\t##!foo
\t ##! bar
##!\tline3
'''
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(contents.splitlines().__iter__()))

        assert len(output) == 1
        assert output[0] == ' not blank ##!+smx '

    def test_preprocess_handles_preprocessor_comments(self):
        contents = '##!> assemble'
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(contents.splitlines().__iter__()))

        assert len(output) == 1
        assert output[0] == ''

    def test_preprocess_does_not_ignore_empty_lines(self):
        contents = '''some line

another line'''
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(contents.splitlines().__iter__()))

        assert output == contents.splitlines()

    def test_preprocess_fails_on_too_many_end_markers(self):
        contents = '''##!> assemble
##!> assemble
##!<
##!<
##!<
'''
        context = Context('')
        assembler = Assembler(context)

        with pytest.raises(ValueError):
            assembler.preprocess(contents.splitlines().__iter__())

    def test_preprocess_fails_on_too_few_end_markers(self):
        contents = '''##!> assemble
##!> assemble'''
        context = Context('')
        assembler = Assembler(context)

        with pytest.raises(ValueError):
            assembler.preprocess(contents.splitlines().__iter__())

    def test_preprocess_does_not_require_final_end_marker(self):
        contents = '''##!> assemble
##!> assemble
##!<
'''
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(contents.splitlines().__iter__()))

        assert len(output) == 1
        assert output[0] == ''


class TestPreprocessors:
    def test_sequential_preprocessors(self):
        contents = '''##!> cmdline unix
foo
##!<
##!> cmdline windows
bar
##!<
##!> assemble
one
two
three
##!<
four
five
'''
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert output == [
            'f[\\x5c\'\\"]*o[\\x5c\'\\"]*o',
            'b[\\"\\^]*a[\\"\\^]*r',
            '(?:t(?:hree|wo)|one)',
            'four',
            'five'
        ]

    def test_nested_preprocessors(self):
        contents = '''##!> assemble
    ##!> cmdline unix
foo
    ##!<
    ##!> cmdline windows
bar
    ##!<
##!<
four
five
'''
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))


        assert output == [
            '(?:f[\\x5c\'\\"]*o[\\x5c\'\\"]*o|b[\\"\\^]*a[\\"\\^]*r)',
            'four',
            'five'
        ]

    def test_complex_nested_preprocessors(self):
        contents = '''##!> assemble
    ##!> cmdline unix
foo
        ##!> assemble
ab
cd
        ##!<
    ##!<
    ##!> cmdline windows
bar
    ##!<
##!<
four
five
'''
        context = Context('')
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))


        assert output == [
            '(?:([\\x5c\'\\"]*?[\\x5c\'\\"]*:[\\x5c\'\\"]*a[\\x5c\'\\"]*b[\\x5c\'\\"]*|[\\x5c\'\\"]*c[\\x5c\'\\"]*d[\\x5c\'\\"]*)|f[\\x5c\'\\"]*o[\\x5c\'\\"]*o|b[\\"\\^]*a[\\"\\^]*r)',
            'four',
            'five'
        ]
