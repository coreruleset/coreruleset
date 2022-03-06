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

import sys, re
from typing import TypeVar, Type
import logging

from lib.processors.processor import Processor

T = TypeVar('T', bound='CmdLine')

COMMENT_REGEX = re.compile(r"^##!")
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())


class CmdLine(Processor):
    lines: list[bytes] = []

    def __init__(self, evasion_pattern, suffix_evasion_pattern):
        self.evasion_pattern = evasion_pattern
        self.suffix_evasion_pattern = suffix_evasion_pattern

    # override
    @classmethod
    def create(cls: Type[T], type: str) -> T:
        if type == 'unix':
            return CmdLineUnix()
        elif type == 'windows':
            return CmdLineWindows()
        else:
            raise ValueError(f'No command line processor of type {type} defined')

    # override
    def process_line(self, line: bytes):
        processed = self.regexp_str(line)
        LOGGER.debug(line)
        LOGGER.debug(processed)
        self.lines.append(processed)

    # overrride
    def complete(self) -> list[bytes]:
        try:
            return self.lines
        finally:
            self.lines = []

    # Convert a single line to regexp format, and insert anti-cmdline
    # evasions between characters.
    def regexp_str(self, input):
        # By convention, if the line starts with ' char, copy the rest
        # verbatim.
        if input[0] == "'":
            return input[1:]
        elif COMMENT_REGEX.match(input) is not None:
            return input

        result = ""
        for i, char in enumerate(input):
            if i > 0:
                result += self.evasion_pattern
            result += self.regexp_char(char)

        return result

    # Ensure that some special characters are escaped
    def regexp_char(self, char):
        char = str.replace(char, ".", "\.")
        char = str.replace(char, "-", "\-")
        if char == "@":
            char = str.replace(char, "@", self.suffix_evasion_pattern)

        # Ensure multiple spaces are matched
        return str.replace(char, " ", "\s+")


class CmdLineUnix(CmdLine):
    def __init__(self):
        super().__init__(
            # Insert these sequences between characters to prevent evasion.
            # This emulates the relevant parts of t:cmdLine.
            r"""[\x5c'\"]*""",
            # Unix: "cat foo", "cat<foo", "cat>foo"
            r"""(?:\s|<|>).*""",
        )


class CmdLineWindows(CmdLine):
    def __init__(self):
        super().__init__(
            # Insert these sequences between characters to prevent evasion.
            # This emulates the relevant parts of t:cmdLine.
            r"""[\"\^]*""",
            # Windows: "more foo", "more,foo", "more;foo", "more.com", "more/e",
            # "more<foo", "more>foo"
            r"""(?:[\s,;]|\.|/|<|>).*""",
        )


if __name__ == "__main__":
    import fileinput

    # Parse arguments
    if len(sys.argv) <= 1 or not sys.argv[1] in ("unix", "windows"):
        print(sys.argv[0] + " unix|windows [infile]")
        sys.exit(1)

    mode = sys.argv[1]
    del sys.argv[1]
    processor = CmdLine.of_type(mode)

    # Process lines from input file, or if not specified, standard input
    for line in fileinput.input():
        if line != "":
            processor.process_line(line.rstrip("\n"))

    sys.stdout.writelines(processor.complete())
