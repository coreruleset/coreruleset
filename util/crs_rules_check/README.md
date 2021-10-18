crs_rules_check
===============

Welcome to the `crs_rules_check` documentation.

Prerequisites
=============

To run the tool, you need:

+ a **Python 3** interpreter
+ **msc_pyparser** - a SecRule parser

`msc_pyparser` was written in Python 3 and has not been tested with Python 2, therefore you have to use Python 3.

The best way to install the required packages just run

```
pip3 install -r requirements.txt
```

How does it work
================

The script expects an argument at least - this would be a single file or a file list, eg: `/path/to/coreruleset/*.conf`.

After it found the set, it starts a loop: open every file, and makes these steps:
  * try to parse the structure - this is a syntax check
    **note**: this script is a bit more strict than mod_security. There are some cases, where mod_security allows the syntax, but [msc_pyparser](https://github.com/digitalwave/msc_pyparser/) not.
  * runs a case sensitive format of operators, actions, transformations and ctl methods
    eg. `@beginsWith` is allowed, `@beginswith` is not.
  * check the order of actions - [see the wiki](https://github.com/coreruleset/coreruleset/wiki/Order-of-ModSecurity-Actions-in-CRS-rules)
  * CRS has a good reference for [indentation](https://github.com/coreruleset/coreruleset/blob/v3.4/dev/CONTRIBUTING.md#general-formatting-guidelines-for-rules-contributions) and other formatting. `msc_pyparser` follows these rules when it creates the config file(s) from parsed structure(s). After the re-build is done, it runs a compare between the original file and the built one with help of `difflib`. If there are any mismatch, it shows that.
  **Note**, that `difflib` is a part of the standard Python library, you don't need to install it.

If script finds any parser error, it stops immediately. In case of other error, shows it (rule-by-rule). Finally, the script returns a non-zero value.

If everything is fine, rule returns with 0.

Normally, you should run the script:

```
./rules-check.py /path/to/coreruleset/*.conf
```

Examples
========

To run these samples, see the files in `examples` directory.

### Test 1 - syntax check

```
SecRule &ARGS_GET "@eq 3" \
    "id:1,\
    phase:2,\
    pass,\
    t:none,\
    nolog,\
    chain
    SecRule ARGS_GET:foo "@rx bar" \
        "t:none,t:urlDecodeUni,t:lowercase,\
        setvar:'tx.some_vars=1'
```

As you can see, there are two `"` missing above: the first one after the `chain`, and the other one from the end of the chained rule. Mod_security allows this, but this isn't well formed. (See [#2184](https://github.com/coreruleset/coreruleset/pull/2184))

Check it:

```
$ ./rules-check.py examples/test1.conf 
Config file: examples/test1.conf
   Parsing...             Can't parse config file: examples/test1.conf
Parser error: syntax error in line 8 at pos 111, column 11
    SecRule ARGS_GET:foo "@rx bar" \
~~~~~~~~~~~^
$ echo $?
1

```

### Test 2 - case sensitive test

```
SecRule REQUEST_URI "@beginswith /index.php" \
    "id:1,\
    phase:1,\
    deny,\
    t:none,\
    nolog"
```

In this rule the operator is lowercase. Mod_security allows both form.

```
$ ./rules-check.py examples/test2.conf 
Config file: examples/test2.conf
   Parsing...              [OK] 
   Check ignore case...    [ERR] 
    In file: examples/test2.conf - rule ID: 1, Operator case mismatch in @beginswith
   Check action order...   [OK] 
   Check indentations...   [OK] 
$ echo $?
1
```

### Test 3 - wrong action ordering

```
SecRule REQUEST_URI "@beginsWith /index.php" \
    "phase:1,\
    id:1,\
    deny,\
    t:none,\
    nolog"
```

In this rule, the `phase` and `id` are interchanged. As [documentation](https://github.com/coreruleset/coreruleset/wiki/Order-of-ModSecurity-Actions-in-CRS-rules) says, the first action **must** be the `id`, the second one is the `phase`.

```
$ ./rules-check.py examples/test3.conf 
Config file: examples/test3.conf
   Parsing...              [OK] 
   Check ignore case...    [OK] 
   Check action order...   [ERR] 
    In file: examples/test3.conf - rule ID: 1, action 'phase' at pos 0 is wrong place against 'id' at pos 1
   Check indentations...   [OK] 
$ echo $?
1
```
