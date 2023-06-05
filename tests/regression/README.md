owasp-crs-regressions
=====================

Introduction
============
Welcome to the OWASP Core Rule Set regression testing suite. This suite is meant to test specific rules in OWASP CRS version 3. The suite is designed to use pre-configured IDs that are specific to this version of CRS. The tests themselves can be run without CRS and one would expect the same elements to be blocked, however one must override the default Output parameter in the tests.

Installation
============
The OWASP Core Rule Set project was part of the effort to develop FTW, the Framework for Testing WAFs. As a result, we use this project to run our regression testing. FTW uses existing testing frameworks to perform human-friendly web-based testing, provided in YAML. You can install FTW with Go or Python:
 
```sh
# Go: https://github.com/coreruleset/go-ftw#install
go install github.com/coreruleset/go-ftw@latest

# Python: https://github.com/coreruleset/ftw#installation
git clone https://github.com/coreruleset/ftw.git
cd ftw
pip install -r requirements.txt 
```

This will install FTW as a library. It can also be run natively, see the FTW documentation for more detail.

Requirements
============
There are three requirements for running the OWASP CRS regressions.

1. You must have ModSecurity specify the location of your error.log, this is done in the config.ini file. If you are using nginx you can use the parameter `--config=modsec3-nginx` (as specified in config.ini)
2. ModSecurity must be in DetectionOnly (or anomaly scoring) mode
3. You must disable IP blocking based on previous events

Note: The test suite compares timezones -- if your test machine and your host machine are in different timezones this can cause bad results

To accomplish 2. and 3. you may use the following rule in your setup.conf:

```
SecAction "id:900005,\
  phase:1,\
  nolog,\
  pass,\
  ctl:ruleEngine=DetectionOnly,\
  ctl:ruleRemoveById=910000,\
  setvar:tx.blocking_paranoia_level=4,\
  setvar:tx.crs_validate_utf8_encoding=1,\
  setvar:tx.arg_name_length=100,\
  setvar:tx.arg_length=400,\
  setvar:tx.max_file_size=64100,\
  setvar:tx.combined_file_sizes=65535"
```

Once these requirements have been met the tests can be run by using pytest.

Running The Tests
=================

On Windows this will look like:
-------------------------------
Single Rule File:
```py.test.exe -v CRS_Tests.py --rule=tests/test.yaml```
The Whole Suite:
```py.test.exe -v CRS_Tests.py --ruledir_recurse=tests/```

On Linux this will look like:
-----------------------------
Single Rule File:
```py.test -v CRS_Tests.py --rule=tests/test.yaml```
The Whole Suite:
```py.test -v CRS_Tests.py --ruledir_recurse=tests/```

Contributions
=============

We'd like to thank Fastly for their help and support in developing these tests.
