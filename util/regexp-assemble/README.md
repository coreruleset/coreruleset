# How to use regexp-assemble.py

## Set up
1. You will need a Perl environment and Perl version >= 5.10
2. You will need a Python environment with Python version >= 3
2. Initialize the Git submodule with the Regexp::Assemble Perl module by running:
    ```bash
    git submodule update --init util/regexp-assemble/lib/lib
    ```
3. You need to install some dependencies. With `virtualenv`, installing them would look like this:
    ```bash
    virtualenv -p 3 venv
    source venv/bin/activate
    pip install -r util/regexp-assemble/requirements.txt
    ```
4. You should now be able to use the script. Try running something like the following:
    ```bash
    printf "(?:homer)? simpson\n(?:lisa)? simpson" | util/regexp-assemble/regexp-assemble.py generate -
    ```
    You should see:
    ```bash
    (?:(?:homer)?|(?:lisa)?) simpson
    ```

## Example use
To generate a reduced expression from a list of expressions, simply pass the rule id to the script of pipe the contents to it:
```bash
util/regexp-assemble/regexp-assemble.py generate 942170
# or
cat util/regexp-assemble/data/942170.data | util/regexp-assemble/regexp-assemble.py generate -
```

You can also compare generated expressions to the current expressions in the rule files:
```bash
util/regexp-assemble/regexp-assemble.py compare 942170
```

Even better, you can update rule files directly:
```bash
util/regexp-assemble/regexp-assemble.py update 942170
# or update all
util/regexp-assemble/regexp-assemble.py update --all
```

Read the help for the full documentation:
```bash
util/regexp-assemble/regexp-assemble.py --help
```

## Adjusting the Logging Level
The level of logging can be adjusted with the `--loglevel` option, accepted values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.

Not many things are currently written to the log, so it may seem that changing the logging level doesn't have any effect, especially, since the processing modules depend on the rule the script processes and the command that is being run (e.g. `generate` usually produces no output since stdout is used to print the resulting regular expression). The `cmdline` processor, for example, includes debug log output, but the `assemble` prorcessor currently doesn't.

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
A line starting with `##!^` can be used to pass a global prefix to the script. The resulting expression will be prefixed with the literal contents of the line. Multiple prefix lines will be concatenated in order. For example, the
 lines
```
##!^ \W*\(
##!^ two
a+b|c
d
```
will produce the regular expression `\W*\(two(?:a+b|c|d)`.

<!-- TODO: fix url -->
The prefix marker exists for convenience and improved readability. The same can be achieved with the (assemble concat)[#] preprocessor.

### Suffix marker
A line starting with `##!$` can be used to pass a suffix to the script. The last found suffix comment line overwrites all previous suffix comment lines. The resulting expression will be suffixed with the literal contents of the line.
For example, the two lines
```
##!$ \W*\(
##!$ two
a+b|c
d
```
will produce the regular expression `(?:a+b|c|d)\W*\(two`.

<!-- TODO: fix url -->
The suffix marker exists for convenience and improved readability. The same can be achieved with the (assemble concat)[#] preprocessor.

### Preprocessor marker
A line starting with `##!>` is a preprocessor directive. The preprocessor marker can be used to preprocess a block of lines.
A line starting with `##!<` marks the end of the most recent preprocessor.

Processor markers have the following general format: `<marker> <processor name>[<processor arguments>]`.
Example: `##!> cmdline unix`.
The arguments depend on the preprocessor and may be empty.

Preprocessors are defined in the [regexp-assemble.py](regexp-assemble.py) script. Whenever a preprocessor runs, the concerning markers are consumed (not passed on to any subsequently running script), all other markers are left in tact. 

#### Nesting
Preprocessors may be nested. This enables complex scenarios, such as assembling a smaller expression to concatenate it to another line of block of lines. For example:
```python
##!> assemble concat
line1
##!=>
  ##!> assemble
ab
cd
  ##!<
##!<
```

There is no practical limit to the nesting depth. Each preprocess block must be ended with the end marker `##!<`, except for the outermost block, where the end marker is optional.

#### Command line evasion preprocessor
Processor name: `cmdline`

##### Arguments
- `unix|windows` (required): The processor argument determines the escaping strategy used for the regular expression. Currently, the two supported strategies are Windows cmd (`windows`) and "unix like" terminal (`unix`).

##### Output
One line per line of input, escaped for the specified environment.

##### Description
The command line evasion preprocessor processes the entire file. Each line is treated as a word (e.g. shell command) that needs to be escaped.

Lines starting with a single quote `'` are treated as literals and will not be escaped.

The special token `@` will be replaced with the expression `(?:\s|<|>).*` in `unix` mode and `(?:[\s,;]|\.|/|<|>).*` in `windows` mode. This can be used in the context of shell to reduce the number of of false positives for a word by requiring a subsequent token to be present. Example: `diff@`.


#### Assemble preprocessor
Processor name: `assemble`

##### Arguments
This preprocessor does not accept any arguments.

##### Output
Single line regular expression, where each line of the input is treated as an alternation of the regular expression. Input can also be concatenated by using the two marker comments for input `##!=<` and `##!=>` output.

##### Description
Each line of the input is treated as an alternation of a regular expression, processed into a single line. The resulting regular expression is not optimized (in the strict sense) but reduced (i.e., common elements may be put into character classes or groups). The ordering of alternations in the output can differ from the order in the file (ordering alternations by length is a simple performance optimization).

This processor can also produce the concatenation of blocks delimited with `##!=>`. It supports two special markers, one for output (`##!=>`) and one for input (`##!=<`).

Lines within blocks delimited by input or output markers are treated as alternations, as usual. The input and output markers enables more complex scenarios, such as separating parts of the regular expression in the data file for improved readability. Rule 930100, for example, uses separate rules for periods and slashes and it easier to reason about the differences when they are physically separated. The following example is based on rules from 930100:
```python
##!> assemble
##! slash patterns
\x5c
##! URI encoded
%2f
%5c
##!=>

##! dot patterns
\.
\.%00
\.%01
```
The above would produce the following, concatenated regular expression:
```python
(?:%(?:2f|5c)|\x5c)\.(?:%0[01])?
```

The input marker `##!=<` takes an identifier as parameter and associates the associated block with the identifier. No output is produced when using the input `##!=<` marker. To concatenate the output of a previously stored block, the appropriate identifier must be passed to the output marker `##!=>` as argument. Stored blocks remain in storage until the end of the program and are available globally. However, since preprocessors run from innermost nesting level to outermost, the following would produce an error because the input `myinput` hasn't been stored yet:
```python
##!> assemble
ab
##!=< myinput
  ##!> assemble
  ##!=> myinput
  ##!<
```
Storing the input earlier works and produces the expect ouput `ab`:
```python
##!> assemble
ab
##!=< myinput
##!<
##!> assemble
##!=> myinput
```

Rule 930100 requires the following concatenation of rules: `<slash rules><dot rules><slash rules>`, `slash rules` is concatenated twice. The following example produces this sequence by storing the expression for slashes with the identifier `slashes`, thus avoiding duplication:
```python
##!> assemble concat
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
```

#### Template preprocessor
Processor name: `template`

##### Arguments
- identifier (required): The name of the template that will be processed by this preprocessor
- replacement (required): The string that replaces the template identified by `identifier`

##### Output
One line per line of input, with all template strings replaced with the specified replacement.

##### Description
The template processor makes it easy to add recurring strings to expressions. This helps reduce maintenance when a template needs to be updated and it improves readability as template strings provide readable and bounded information, where otherwise a regular expression must be read and boundaries must be identified.

The format of template strings is as follows:
```
{{identifier}}
```
The template string starts with two opening braces, is followed by an identifier, and ened with two closing braces. The identifier format must satisfy the following regular expression:
```python
[a-z-A-Z\d_-]+
```
An identifier must have at least one character and consist only of upper and lowercase letters a through z, digits 0 through 9, and underscore or dash.

The following example shows how to use the template processor:
```python
##!> template slashes [/\]
regex with {{slashes}}
```
This would result in the output `regex with [\/\]` (the assembler escapes the forward slash).

#### Include preprocessor
Processor name: `include`

##### Arguments
- include file name (required): The name of the file to include, without suffix

##### Output
The exact contents of the included file.

##### Description
The incluce preprocessor reduces repetition across data files. Repeated blocks can be put into a file in the `include` directory and then be included with the `include` preprocessor comment. The contents of an include file could for example be the alternation of accepted HTTP headers:

```python
POST
GET
HEAD
```

This could be included into a data file for a rule that adds an additional method:

```python
##!> include http-headers
OPTIONS
```

The resulting regular expression would be `(?:(?:POS|GE)T|OPTIONS|HEAD)`.

Note that the include preprocessor does not have a body, therefore, the end marker is optional.

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
