# How to use regexp-assemble.py

## Set up
1. You will need a Perl environment and Perl version >= 5.10
2. Initialize the Git submodule with the Regexp::Assemble Perl module by running:
    ```bash
    git submodule update --init util/regexp-assemble/lib/lib
    ```
3. You should now be able to use the script. Try running something like the following:
    ```bash
    printf "(?:homer)? simpson\n(?:lisa)? simpson" | util/regexp-assemble/regexp-assemble.py
    ```
    You should see:
    ```bash
    (?:(?:homer)?|(?:lisa)?) simpson
    ```

## Example use
To generate a reduced expression from a list of expressions, simply pass the rule id to the script of pipe the contents to it:
```bash
util/regexp-assemble/regexp-assemble.py 942170
# or
cat util/regexp-assemble/data/942170.data | util/regexp-assemble/regexp-assemble.py
```

# Data file format
The data files (`.data` suffix, under `util/regexp-assemble/data`) contain one regular expression per line. These files are meant to be processed by [regexp-assemble.py](regexp-assemble.py).

## Comments
Lines starting with `##!` are considered comments and will be skipped. Use comments to explain the purpose of a particular
regular expression, use cases, origin, shortcomings, etc. The more information we have about individual expressions the better we will be able to understand changes or change requirements, e.g. when reviewing pull requests.

## Empty lines
Empty lines, i.e., lines containing only white space, will be skipped. You can use empty lines to improve readability, especially when adding
comments.

## Processing markers
### Flag marker
A line starting with `##!+` can be used to pass global flags to the script. The last found flag comment line overwrites
all previous flag comment lines. The resulting expression will be prefixed with the flags. For example, the two lines
```
##!+ i
a+b|c
```
will produce the regular expression `(?i)a+b|c`.

We currently only support the ignore case flag `i`.

### Prefix marker
A line starting with `##!^` can be used to pass a prefix to the script. The last found prefix comment line overwrites
all previous prefix comment lines. The resulting expression will be prefixed with the literal contents of the line. For example, the
 lines
```
##!^ \W*\(
a+b|c
d
```
will produce the regular expression `\W*\((?:a+b|c|d)`.

### Suffix marker
A line starting with `##!$` can be used to pass a suffix to the script. The last found suffix comment line overwrites all previous suffix comment lines. The resulting expression will be suffixed with the literal contents of the line.
For example, the two lines
```
##!$ \W*\(
a+b|c
d
```
will produce the regular expression `(?:a+b|c|d)\W*\(`.

### Preprocessor marker
A line starting with `##!>` is a preprocessor directive. The preprocessor marker can be used to preprocess a single line, a block of lines or the entire file.

Processor markers have the following general format: `<marker> <processor name>[ <processor arguments>]`.
Example: `##!> cmdline unix`.
The arguments depend on the preprocessor and may be empty.

Preprocessors are defined in the [regexp-assemble.py](regexp-assemble.py) script. Whenever a preprocessor runs, the concerning markers are consumed (not passed on to any subsequently running script), all other markers are left in tact. 
#### Line preprocessors
A line preprocessor transforms the line immediately following the preprocessor marker.

Currently, no line preprocessors are defined.

#### Block preprocessors
A block preprocessor transforms all the lines up to the next block end marker `##!<`. In absence of an end marker, lines will be consumed to the end of file.

##### Negative lookbehind block processor
Processor name: `neglook`

###### Arguments
- `-h` (optional): The optional argument `-h` prints the output of the negative lookbehind preprocessor in human readable form (i.e., with line breaks). Use this option only for debugging.

###### Output
Single negative lookbehind expression (single line).

###### Description
The negative lookbehind block processor processes a block of lines as alternatives of a negative lookbehind expression. For example, to generate a regex equivalent to `(?<!a[bB]c|1234)` you would write the following:
```
...
##!> neglook
a[bB]c
1234
##!<
```

The purpose of this processor is to provide an alternative for regular expressions that require negative lookbehind for non-backtracking regular expression engines (e.g. re2).

Note that this processor is limited in it's ability to process arbitrary expressions, specifically, it can't deal with escape `\` and range `-` operators.
#### File preprocessors
A file preprocessor transforms all the lines of the file (except for comments).

##### Command line evasion preprocessor
Processor name: `cmdline`

###### Arguments
- `unix|windows` (required): The processor argument determines the escaping strategy used for the regular expression. Currently, the two supported strategies are Windows cmd (`windows`) and "unix like" terminal (`unix`).

###### Output
One line per line of input, escaped for the specified environment.

###### Description
The command line evasion preprocessor processes the entire file. Each line is treated as a word (e.g. shell command) that needs to be escaped.

Lines starting with a single quote `'` are treated as literals and will not be escaped.

The special token `@` will be replaced with the expression `(?:\s|<|>).*` in `unix` mode and `(?:[\s,;]|\.|/|<|>).*` in `windows` mode. This can be used in the context of shell to reduce the number of of false positives for a word by requiring a subsequent token to be present. Example: `diff@`.

## Example
The following is an example of what a data file might contain:

```
##! This line is a comment and will be ignored. The next line is empty and will also be ignored.
    
##! The next line sets the *ignore case* flag on the resulting expression:
##!+ i

##! The next line is the prefix comment. The assembled expression will be prefixed with its contents:
##!^ \b

##! The next line is the suffix comment. The assembled expression will be suffixed with its contents:
##!$ \W*(

##! The following two lines are regular expressions that will be assembled:
--a--
__b__

##! Another comment, followed by another regular expression:
^#!/bin/bash
```

This data file would produce the following assembled expression: `(?i)\b(?:^#!\/bin\/bash|--a--|__b__)\W*(`
