# Find the rules without test cases

This page describes how can you find the rules without any test cases

## Goal

The main goal that we must to have at least regression test for all relevant REQUEST-* rules. (In this context, the PL controll rules are not relevant, because they do not need to have tests.)

You need to pass the CORERULESET root as argument.

The script collects all avaliable test files, based on the name of the test files. It will look up under CORERULESET_ROOT/tests/regression/tests/*.

Then it starts to read all rule files with name "REQUEST-\*", which means this won't handles the RESPONSE-* rules.

The script parses the rules, uses `msc_pyparser`, reads the rule's id, and try to find the test case.

The sctipt ignores the check in case of PL control rules (rules with id under 9XX100), and some hardcoded rules:
 * REQUEST-900-
 * REQUEST-901-
 * REQUEST-905-
 * REQUEST-910-
 * REQUEST-912.
 * REQUEST-949-


## Prerequisites

* Python3 interpreter
* Py-YAML
* msc_pyparser
* CRS rule set
