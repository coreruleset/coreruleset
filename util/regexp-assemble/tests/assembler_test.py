import pytest

from .fixtures import *
from lib.operators.assembler import Assembler, Peekerator, NestingError
from lib.context import Context

class TestFileFormat:
    def test_preprocess_ignores_simple_comments(self, context):
        contents = '''##!line1
##! line2
##!\tline3
'''
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 0

    def test_preprocess_does_not_ignore_special_comments(self, context):
        contents = '''##!+i
##!+ smx
##!^prefix
##!^ prefix
##!$suffix
##!$ suffix
'''
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert output == contents.splitlines()


    def test_preprocess_does_not_require_comments_to_start_line(self, context):
        contents = '''##!line1
 ##! line2
 not blank ##!+smx 
\t\t##!foo
\t ##! bar
##!\tline3
'''
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 1
        assert output[0] == ' not blank ##!+smx '

    def test_preprocess_handles_preprocessor_comments(self, context):
        contents = '##!> assemble'
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 0

    def test_preprocess_ignores_empty_lines(self, context):
        contents = '''some line

another line'''
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert output == [
            'some line',
            'another line'
        ]

    def test_preprocess_fails_on_too_many_end_markers(self, context):
        contents = '''##!> assemble
##!> assemble
##!<
##!<
##!<
'''
        assembler = Assembler(context)

        with pytest.raises(NestingError):
            assembler.preprocess(Peekerator(contents.splitlines()))

    def test_preprocess_fails_on_too_few_end_markers(self, context):
        contents = '''##!> assemble
##!> assemble'''
        assembler = Assembler(context)

        with pytest.raises(NestingError):
            assembler.preprocess(Peekerator(contents.splitlines()))

    def test_preprocess_does_not_require_final_end_marker(self, context):
        contents = '''##!> assemble
##!> assemble
##!<
'''
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert len(output) == 0


class TestPreprocessors:
    def test_sequential_preprocessors(self, context):
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
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))

        assert output == [
            'f[\\x5c\'\\"]*o[\\x5c\'\\"]*o',
            'b[\\"\\^]*a[\\"\\^]*r',
            '(?:t(?:hree|wo)|one)',
            'four',
            'five'
        ]

    def test_nested_preprocessors(self, context):
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
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))


        assert output == [
            '(?:f[\\x5c\'\\"]*o[\\x5c\'\\"]*o|b[\\"\\^]*a[\\"\\^]*r)',
            'four',
            'five'
        ]

    def test_complex_nested_preprocessors(self, context):
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
##!> assemble
six
seven
##!<
eight
'''
        assembler = Assembler(context)

        output = list(assembler.preprocess(Peekerator(contents.splitlines())))


        assert output == [
            '(?:([\\x5c\'\\"]*?[\\x5c\'\\"]*:[\\x5c\'\\"]*a[\\x5c\'\\"]*b[\\x5c\'\\"]*|[\\x5c\'\\"]*c[\\x5c\'\\"]*d[\\x5c\'\\"]*)|f[\\x5c\'\\"]*o[\\x5c\'\\"]*o|b[\\"\\^]*a[\\"\\^]*r)',
            'four',
            'five',
            's(?:even|ix)',
            'eight'
        ]
