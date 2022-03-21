crs_rules_check
===============

Welcome to the `crs_rules_check` documentation.

Prerequisites
=============

To run the tool, you need:

+ a **Python 3** interpreter
+ **msc_pyparser** - a SecRule parser (>=1.2.0)

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
./rules-check.py -r /path/to/coreruleset/*.conf
```

Optionally, you can add the option `--output=github` (default value is `native`):

```
./rules-check.py --output=github -r /path/to/coreruleset/*.conf
```

In this case, each line will have a prefix, which could be `::debug` or `::error`. See [this](https://docs.github.com/en/actions/learn-github-actions/workflow-commands-for-github-actions#setting-an-error-message).

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
$ ./rules-check.py -r examples/test1.conf
Config file: examples/test1.conf
Can't parse config file: examples/test1.conf
  file=examples/test1.conf, line=8, endLine=8, title=Parser error: can't parse file
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
$ ./rules-check.py -r examples/test2.conf
Config file: examples/test2.conf
 Parsing ok.
 Ignore case check found error(s)
  file=examples/test2.conf, line=1, endLine=1, title=Case check: Operator case mismatch: @beginswith (rule: 1)
 Action order check ok.
 Indentation check ok.
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
$ ./rules-check.py -r examples/test3.conf
Config file: examples/test3.conf
 Parsing ok.
 Ignore case check ok.
 Action order check found error(s)
  file=examples/test3.conf, line=3, endLine=3, title=Action order check: action 'phase' at pos 0 is wrong place against 'id' at pos 1 (rule: 1)
 Indentation check ok.
$ echo $?
1
```

### Test 4 - wrong indentation

```
 SecRule ARGS "@rx foo" \
   "id:1,\
    phase:1,\
    pass,\
    nolog"

SecRule ARGS "@rx foo" \
    "id:2,\
    phase:1,\
    pass,\
    nolog"

SecRule ARGS "@rx foo" \
     "id:3,\
    phase:1,\
    pass,\
    nolog"
```

In this rule set, the first line and the rule with `id:3` first action have an extra leading space. As [documentation](https://github.com/coreruleset/coreruleset/blob/v3.4/dev/CONTRIBUTING.md#general-formatting-guidelines-for-rules-contributions) describes, CRS has a strict indentation rules. The script checks the indentation with help of Python's [difflib](https://docs.python.org/3.9/library/difflib.html).

```
$ ./rules-check.py -r examples/test4.conf
Config file: examples/test4.conf
 Parsing ok.
 Ignore case check ok.
 Action order check ok.
 Indentation check found error(s)
---
+++
  file=examples/test4.conf, line=1, endLine=6, title=Indentation error: an indetation error has found
@@ -1,5 +1,5 @@
- SecRule ARGS "@rx foo" \
-   "id:1,\
+SecRule ARGS "@rx foo" \
+    "id:1,\
     phase:1,\
     pass,\
     nolog"
  file=examples/test4.conf, line=11, endLine=18, title=Indentation error: an indetation error has found
@@ -11,7 +11,7 @@
     nolog"

 SecRule ARGS "@rx foo" \
-     "id:3,\
+    "id:3,\
     phase:1,\
     pass,\
     nolog"
```
