#!/usr/bin/env python3

# This file helps to find the longest data size in all test cases under
# CORERULESET_ROOT/test/regression/tests directory.

# You just have to pass the CORERULESET_ROOT as argument.

# At the end, the script will print the longest length, and the rule where
# the data is.


import sys
import os
import os.path
import yaml

if __name__ == "__main__":
    test_cases = {}
    if len(sys.argv) < 2:
        print("Argument missing!")
        print("Use: %s /path/to/coreruleset/" % (sys.argv[0]))
        sys.exit(1)
    testpath = sys.argv[1].rstrip("/") + "/tests/regression/tests/"

    if not os.path.isdir(testpath):
        print("Directory does not exist: %s" % (testpath))
        sys.exit(1)

    try:
        max_len = 0
        max_title = ""
        for root, dirs, files in os.walk(testpath):
            path = root.split(os.sep)
            for file in files:
                if file.endswith(".yaml"):
                    with open(os.path.join(root, file)) as f:
                        test = yaml.full_load(f)
                        for t in test['tests']:
                            title = t['test_title']
                            for s in t['stages']:
                                if 'stage' in s:
                                    if 'input' in s['stage']:
                                        if 'data' in s['stage']['input']:
                                            if len(s['stage']['input']['data']) > max_len:
                                                max_len = len(s['stage']['input']['data'])
                                                max_title = title
        print("Longest data: %d in test %s" % (max_len, max_title))
    except:
        print("Can't open files in given path!")
        print(sys.exc_info())
        sys.exit(1)
