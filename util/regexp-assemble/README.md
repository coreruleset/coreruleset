# Data file format
The data files (`.data` suffix) contain one regular expression per line. The contents of these files can be piped to [regexp-assemble.py](regexp-assemble.py) directly.

## Comments
Lines starting with an octothorpe (`#`) are considered comments and will be ignored. Use comments to explain the purpose of a particular
regular expression, use cases, origin, shortcomings, etc. The more information we have about individual expressions the better we will be able to understand changes or change requirements, e.g. when reviewing pull requests.

## Empty lines
Empty lines, i.e., lines containing only white space, will be skipped. You can use empty lines to improve readability, especially when adding
comments.

## Flag comment
A line starting with octothorpe and bang (`#!`) can be used to pass global flags to the script. The last found flag comment line overwrites
all previous flag comment lines. The resulting expression will be prefixed with the flags. For example, the two lines
```
#! i
a+b|c
```
will produce the regular expression `(?i)a+b|c`.

We currently only support the ignore case flag `i`.

## Prefix comment
A line starting with an octothorpe and caret (`#^`) can be used to pass a prefix to the script. The last found prefix comment line overwrites
all previous prefix comment lines. The resulting expression will be prefixed with the literal contents of the line. For example, the two lines
```
#^ \W*\(
a+b|c
```
will produce the regular expression `\W*\(a+b|c`.

## Suffix comment
A line starting with an octothorpe and dollar (`#$`) can be used to pass a suffix to the script. The last found suffix comment line overwrites all previous suffix comment lines. The resulting expression will be suffixed with the literal contents of the line.
For example, the two lines
```
#$ \W*\(
a+b|c
```
will produce the regular expression `a+b|c\W*\(`.
