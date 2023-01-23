crs_rules_check
===============

Welcome to the `crs_rules_check` documentation.

Prerequisites
=============

To run the tool, you need:

+ a **Python 3** interpreter
+ **msc_pyparser** - a SecRule parser (>=1.2.1)

`msc_pyparser` was written in Python 3 and has not been tested with Python 2, therefore you have to use Python 3.

The best way to install the required packages just run

```
pip3 install -r requirements.txt
```

How does it work
================

The script expects an argument at least - this would be a single file or a file list, eg: `/path/to/coreruleset/*.conf`.

First it parses all of the files what you given, and tries to parse. This is a "pre-check", and runs on all files before the other tests.
  * **Parsing check** - try to parse the structure, this is a syntax check
    **note**: this script is a bit more strict than mod_security. There are some cases, where mod_security allows the syntax, but [msc_pyparser](https://github.com/digitalwave/msc_pyparser/) not. Also note, that this step runs on all rules files before the others

After it found the set, it starts a loop: on each parsed structure it does these steps:
  * **Case sensitive check** - runs a case sensitive format of operators, actions, transformations and ctl methods
    eg. `@beginsWith` is allowed, `@beginswith` is not. In this step, the script also ensures that an operator is present, eg `SecRule ARGS "^.*"` isn't allowed without `@rx` operator.
  * **Order actions check** - checking the order of actions - [see the wiki](https://github.com/coreruleset/coreruleset/wiki/Order-of-ModSecurity-Actions-in-CRS-rules)
  * **Identation check** CRS has a good reference for [indentation](https://github.com/coreruleset/coreruleset/blob/v3.4/dev/CONTRIBUTING.md#general-formatting-guidelines-for-rules-contributions) and other formatting. `msc_pyparser` follows these rules when it creates the config file(s) from parsed structure(s). After the re-build is done, it runs a compare between the original file and the built one with help of `difflib`. If there are any mismatch, it shows that.
  **Note**, that `difflib` is a part of the standard Python library, you don't need to install it.
  * **checking the 'ctl:auditLogParts' actions** - this step checks that the `ctl:auditLogParts` action is on the right place. In cae of a chained rule this action **must** placed in the last rule.
  * **Duplicate ID's check** - checks the uniqueness of identifiers, and refers if a duplicate ID has found
  * **paranoia-level/N tag and its value** - checks the existence (or non-existence) of `paranoia-level` tag where it is necessary or not, and its correctness. This step does:
    * if a rule activated on a certain PL, and it does not have `nolog` action, it **must** have the correct `tag:'paranoia-level/N'` action with correct `N` value
    * if a rule activated outside of any PL, or it has a `nolog` action, it **must not** have any `tag:paranoia-level/N` action
 * **PL anomaly_scores check** - checks the scoring mechanism checks the rule consistency on a certain PL:
    * rule must have the `severity` action
    * rule must have the `setvar:(inbound|outbound)_anomaly_score_plN=+%{tx.SEVERITY_anomaly_score}`
 * **Initialization of used TX variables** - all used TX variables have to initialize before it used. Using of a TX variable means:
    * it occurs as a target, eg `SecRule TX.foo ...`
    * it occurs as an operator argument, eg `SecRule ARGS "@rx %{TX.foo}"...`
    * it occurs as a right side operand in a `setvar` action, eg `setvar:tx.bar=%{tx.foo}`
    * it occurs as a substitution, eg in a `msg` value: `msg:'Current value of variable: %{tx.foo}`

After these steps there is a cumulated report about not used TX variables. This could happen if a rule creates a TX variable (eg. `setvar:tx.foo=1`) but variable never used. This will only be revealed after we have reviewed all the rules.


If script finds any parser error, it stops immediately. In case of other error, shows it (rule-by-rule). Finally, the script returns a non-zero value.

If everything is fine, rule returns with 0.

Normally, you should run the script:

```
./util/crs-rules-check/rules-check.py -r crs-setup.conf.example -r rules/*.conf
```

Optionally, you can add the option `--output=github` (default value is `native`):

```
./util/crs-rules-check/rules-check.py --output=github -r crs-setup.conf.example -r rules/*.conf
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

### Test 5 - empty (implicit @rx) operator

```
SecRule REQUEST_URI "index.php" \
    "phase:1,\
    id:1,\
    deny,\
    t:none,\
    nolog"
```

In this rule, the operator is missing. As [ModSecurity documentation](https://github.com/SpiderLabs/ModSecurity/wiki/Reference-Manual-(v2.x)#rx) says "the rules that do not explicitly specify an operator default to @rx". In CRS, this isn't allowed.

```
$ ./rules-check.py -r examples/test5.conf
Config file: examples/test5.conf
 Parsing ok.
 Ignore case check found error(s)
  file=examples/test5.conf, line=1, endLine=1, title=Case check: Empty operator isn't allowed (rule: 1)
 Action order check ok.
 Indentation check ok.
$ echo $?
1
```

### Test 6 - check that rule does not contain 'ctl:auditLogParts'

```
SecRule TX:sql_error_match "@eq 1" \
    "id:1,\
    phase:4,\
    block,\
    capture,\
    t:none,\
    ctl:auditLogParts=+E"
```

The `ctl:auditLogParts=+E` (or any kind of `ctl:auditLogParts`) is not allowed in CRS.

See the CRS PR [#3034](https://github.com/coreruleset/coreruleset/pull/3034)

```
$ util/crs-rules-check/rules-check.py -r util/crs-rules-check/examples/test6.conf
Config file: util/crs-rules-check/examples/test6.conf
 Parsing ok.
 Ignore case check ok.
 Action order check ok.
 Indentation check ok.
 Found 'ctl:auditLogParts' action is in wrong place.
  file=util/crs-rules-check/examples/test6.conf, line=7, endLine=7, title='ctl:auditLogParts' action in wrong place: action can only be placed in last part of a chained rule (rule: 1)
$ echo $?
1
```

### Test 7 - check duplicated id's

```
SecRule ARGS "@rx foo" \
    "id:1001,\
    phase:2,\
    block,\
    capture,\
    t:none"

SecRule ARGS_NAMES "@rx bar" \
    "id:1001,\
    phase:2,\
    block,\
    capture,\
    t:none"
```

In this rule file, there are two rules with same `id`.

```
$ util/crs-rules-check/rules-check.py -r util/crs-rules-check/examples/test7.conf
Config file: util/crs-rules-check/examples/test7.conf
 Parsing ok.
Checking parsed rules...
util/crs-rules-check/examples/test7.conf
 Ignore case check ok.
 Action order check ok.
 Indentation check ok.
 'ctl:auditLogParts' actions are in right place.
 Found duplicated id('s)
  file=util/crs-rules-check/examples/test7.conf, line=10, endLine=10, title='id' is duplicated: id 1001 is duplicated, previous place: util/crs-rules-check/examples/test7.conf:3
 paranoia-level tags are correct.
 PL anomaly_scores are correct.
 All TX variables are set
End of checking parsed rules
$ echo $?
1
```

### Test 8 - paranoia-level consitency check

```

SecRule &TX:blocking_paranoia_level "@eq 0" \
    "id:901120,\
    phase:1,\
    pass,\
    nolog,\
    ver:'OWASP_CRS/4.0.0-rc1',\
    setvar:'tx.blocking_paranoia_level=1'"

SecRule &TX:detection_paranoia_level "@eq 0" \
    "id:901125,\
    phase:1,\
    pass,\
    nolog,\
    ver:'OWASP_CRS/4.0.0-rc1',\
    setvar:'tx.detection_paranoia_level=%{TX.blocking_paranoia_level}'"

SecRule &TX:error_anomaly_score "@eq 0" \
    "id:901141,\
    phase:1,\
    pass,\
    nolog,\
    ver:'OWASP_CRS/4.0.0-rc1',\
    setvar:'tx.error_anomaly_score=4'"

SecRule TX:DETECTION_PARANOIA_LEVEL "@lt 1" "id:920011,phase:1,pass,nolog,skipAfter:END-REQUEST-920-PROTOCOL-ENFORCEMENT"
SecRule TX:DETECTION_PARANOIA_LEVEL "@lt 1" "id:920012,phase:2,pass,nolog,skipAfter:END-REQUEST-920-PROTOCOL-ENFORCEMENT"

SecRule REQUEST_HEADERS:Content-Length "!@rx ^\d+$" \
    "id:920160,\
    phase:1,\
    block,\
    t:none,\
    tag:'paranoia-level/2',\
    severity:'CRITICAL',\
    setvar:'tx.inbound_anomaly_score_pl1=+%{tx.error_anomaly_score}'"

SecRule REQUEST_HEADERS:Content-Length "!@rx ^\d+$" \
    "id:920161,\
    phase:1,\
    block,\
    t:none,\
    tag:'paranoia-level/1',\
    setvar:'tx.inbound_anomaly_score_pl1=+%{tx.error_anomaly_score}'"

SecRule REQUEST_HEADERS:Content-Length "!@rx ^\d+$" \
    "id:920162,\
    phase:1,\
    block,\
    t:none,\
    tag:'paranoia-level/1',\
    severity:'CRITICAL',\
    setvar:'tx.inbound_anomaly_score_pl2=+%{tx.critical_anomaly_score}'"

SecMarker "END-REQUEST-920-PROTOCOL-ENFORCEMENT"

```

In this rule file, there are more problems:
* rule 920160 is activated on PL1, but the `tag` value is PL2
* at rule 920160, the TX variable gets error_anomaly_score, but the severity is CRITICAL
* at rule 920161 there is no severity action
* rule 920162 increments anomaly_score_pl2, but it's in PL1

```
$ ./rules-check.py -r examples/test8.conf
Config file: examples/test8.conf
 Parsing ok.
Checking parsed rules...
examples/test8.conf
 Ignore case check ok.
 Action order check ok.
 Indentation check ok.
 'ctl:auditLogParts' actions are in right place.
 no duplicate id's
 Found incorrect paranoia-level/N tag(s)
  file=examples/test8.conf, line=34, endLine=34, title=wrong or missing paranoia-level/N tag: tag 'paranoia-level/2' on PL 1, rule id: 920160
 Found incorrect (inbound|outbout)_anomaly_score value(s)
  file=examples/test8.conf, line=36, endLine=36, title=wrong (inbound|outbout)_anomaly_score variable or value: invalid value for anomaly_score_pl1: tx.error_anomaly_score with severity critical, rule id: 920160
  file=examples/test8.conf, line=44, endLine=44, title=wrong (inbound|outbout)_anomaly_score variable or value: missing severity action, rule id: 920161
  file=examples/test8.conf, line=53, endLine=53, title=wrong (inbound|outbout)_anomaly_score variable or value: variable inbound_anomaly_score_pl2 on PL 1, rule id: 920162
 There are one or more unset TX variables.
  file=examples/test8.conf, line=53, endLine=53, title=unset TX variable: TX variable 'critical_anomaly_score' not set / later set (rvar) in rule 920162
End of checking parsed rules
Cumulated report about unused TX variables
 No unused TX variable
$ echo $?
1
```

### Test 9 - check state of used TX variables


```
SecRule TX:foo "@rx bar" \
    "id:1001,\
    phase:1,\
    pass,\
    nolog"

SecRule ARGS "@rx ^.*$" \
    "id:1002,\
    phase:1,\
    pass,\
    nolog,\
    setvar:tx.bar=1"
```

In this rule file, there are more problems:
* rule 1001 used an uninitialized variable (`TX:foo`)
* rule 1002 sets a TX variable which never used
