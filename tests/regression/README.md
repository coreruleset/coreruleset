owasp-crs-regressions
=====================

Introduction
============
Welcome to the OWASP Core Rule Set regression testing suite. This suite is meant to test specific rules in OWASP CRS version 3. The suite is designed to use pre-configured IDs that are specific to this version of CRS. The tests themselves can be run without CRS and one would expect the same elements to be blocked, however one must override the default Output parameter in the tests.

Installation
============
The OWASP Core Rule Set project was part of the effort to develop FTW, the Framework for Testing WAFs. As a result, we use this project to run our regression testing. FTW is not an executable that performs human-friendly web-based testing. Tests are written using YAML. You can get the tool from the [FTW releases page](https://github.com/coreruleset/go-ftw/releases).
 
Requirements
============
There are three requirements for running the OWASP CRS regressions:

1. Create `.ftw.yaml` for your environment. (see Section [Yaml Config File](https://github.com/coreruleset/go-ftw#yaml-config-file) in go-ftw for more details)
2. Specify your error.log location from ModSecurity in `.ftw.yaml`.
3. Make sure ModSecurity is in `DetectionOnly` mode.

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
