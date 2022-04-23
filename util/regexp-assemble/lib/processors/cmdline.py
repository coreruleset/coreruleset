#!/usr/bin/env python
#
# Convert a word list to a list of regexps usable by Regexp::Assemble.
#
# This script is used to create regular expressions against attacks that use command line
# evasion. It emulates ModSecurity's `t:cmdLine` but enables us to match starts of commands
# (;) and paths (\).
# Use this script to enhance the expressions from a data file before handing them to
# regexp-assemble.pl.
#
# Note: if your regular expression is not related to shell commands you can run the data file
# through regexp-assemble.pl directly.
#
# Examples:
# cat regexp-932100.txt | ./regexp-cmdline.py unix | ./regexp-assemble.pl
# cat regexp-932110.txt | ./regexp-cmdline.py windows | ./regexp-assemble.pl
# cat regexp-932150.txt | ./regexp-cmdline.py unix | ./regexp-assemble.pl
#
# Refer to rule 932100, 932110, 932150 for documentation.
#

from typing import TypeVar, List

from lib.processors.processor import Processor
from lib.context import Context

T = TypeVar('T', bound='CmdLine')


class CmdLine(Processor):
    def __init__(self, context: Context, evasion_pattern: str, suffix_evasion_pattern: str):
        super().__init__(context)

        self.evasion_pattern = evasion_pattern
        self.suffix_evasion_pattern = suffix_evasion_pattern

    # override
    @classmethod
    def create(cls: T, context: Context, args: List[str]) -> T:
        if len(args) < 1:
            raise ValueError('No type defined for command line processor, expected `unix` or `windows`')

        type = args[0]
        if type == 'unix':
            return CmdLineUnix(context)
        elif type == 'windows':
            return CmdLineWindows(context)
        else:
            raise ValueError(f'No command line processor of type {type} defined')

    # override
    def process_line(self, line: str):
        if line == '':
            return

        processed = self.regexp_str(line)
        self.lines.append(processed)

        self.logger.debug('cmdline in:  %s', line)
        self.logger.debug('cmdline out: %s', processed)

    # overrride
    def complete(self) -> List[bytes]:
        try:
            return self.lines
        finally:
            self.lines = []

    # Convert a single line to regexp format, and insert anti-cmdline
    # evasions between characters.
    def regexp_str(self, input) -> str:
        # By convention, if the line starts with ' char, copy the rest
        # verbatim.
        if input[0] == "'":
            return input[1:]
        elif self.comment_regex.match(input) is not None:
            return input

        result = ''
        for i, char in enumerate(input):
            if i > 0:
                result += self.evasion_pattern
            result += self.regexp_char(char)

        return result

    # Ensure that some special characters are escaped
    def regexp_char(self, char):
        char = str.replace(char, '.', '\.')
        char = str.replace(char, '-', '\-')
        if char == '@':
            char = str.replace(char, '@', self.suffix_evasion_pattern)

        # Ensure multiple spaces are matched
        return str.replace(char, ' ', '\s+')


class CmdLineUnix(CmdLine):
    def __init__(self, context: Context):
        super().__init__(
            context,
            # Insert these sequences between characters to prevent evasion.
            # This emulates the relevant parts of t:cmdLine.
            r'''[\x5c'\"]*''',
            # Unix: "cat foo", "cat<foo", "cat>foo"
            r'''(?:\s|<|>).*''',
        )


class CmdLineWindows(CmdLine):
    def __init__(self, context: Context):
        super().__init__(
            context,
            # Insert these sequences between characters to prevent evasion.
            # This emulates the relevant parts of t:cmdLine.
            r'''[\"\^]*''',
            # Windows: "more foo", "more,foo", "more;foo", "more.com", "more/e",
            # "more<foo", "more>foo"
            r'''(?:[\s,;]|\.|/|<|>).*''',
        )
