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

import fileinput, sys, re

COMMENT_REGEX = re.compile(r'^##!')

# Convert a single line to regexp format, and insert anti-cmdline
# evasions between characters.
def regexp_str(input, evasion, mode):
    # By convention, if the line starts with ' char, copy the rest
    # verbatim.
    if input[0] == "'":
        return input[1:]
    elif COMMENT_REGEX.match(input) is not None:
        return input

    result = ''
    for i, char in enumerate(input):
        if i > 0:
            result += evasion
        result += regexp_char(char, mode)

    return result

# Ensure that some special characters are escaped
def regexp_char(char, mode):
    char = str.replace(char, '.', '\.')
    char = str.replace(char, '-', '\-')
    if char == '@':
        if mode == 'unix':
            # Unix: "cat foo", "cat<foo", "cat>foo"
            pattern = r'''(?:\s|<|>).*'''
        elif mode == 'windows':
            # Windows: "more foo", "more,foo", "more;foo", "more.com", "more/e",
            # "more<foo", "more>foo"
            pattern = r'''(?:[\s,;]|\.|/|<|>).*'''
        char = str.replace(char, '@', pattern)

    # Ensure multiple spaces are matched
    return str.replace(char, ' ', '\s+')

# Insert these sequences between characters to prevent evasion.
# This emulates the relevant parts of t:cmdLine.
evasions = {
    'unix': r'''[\\\\'\"]*''',
    'windows': r'''[\"\^]*''',
}

# Parse arguments
if len(sys.argv) <= 1 or not sys.argv[1] in evasions:
    print(sys.argv[0] + ' unix|windows [infile]')
    sys.exit(1)

mode = sys.argv[1]
evasion = evasions[mode]
del sys.argv[1]

# Process lines from input file, or if not specified, standard input
for line in fileinput.input():
    line = line.rstrip('\n ')
    if line != '':
        print(regexp_str(line, evasion, mode))
