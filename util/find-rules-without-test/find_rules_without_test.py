#!/usr/bin/env python3

# This file helps to find the rules which does not have any test cases.
#
# You just have to pass the CORERULESET_ROOT as argument.
#
# At the end, the script will print the list of rules without any tests.
#
# Please note, that there are some exclusions:
# * only REQUEST-NNN rules are checked
# * there are some hardcoded exlucions:
#   * REQUEST-900-
#   * REQUEST-901-
#   * REQUEST-905-
#   * REQUEST-910-
#   * REQUEST-912.
#   * REQUEST-949-


import sys
import glob
import msc_pyparser

def find_ids(s, test_cases):
    """
        s: the parsed structure
        test_cases: all avaliable test cases
    """
    for i in s:
        # only SecRule counts
        if i['type'] == "SecRule":
            for a in i['actions']:
                # find the `id` action
                if a['act_name'] == "id":
                    # get the argument of the action
                    rid = int(a['act_arg']) # int
                    srid = a['act_arg']     # string
                    if (rid%1000) >= 100:   # skip the PL controll rules
                        # also skip these hardcoded rules
                        if srid[:3] not in ["900", "901", "905", "910", "912", "949"]:
                            # if there is no test cases, just print it
                            if rid not in test_cases:
                                print(rid)

if __name__ == "__main__":
    test_cases = {}
    if len(sys.argv) < 2:
        print("Argument missing!")
        print("Use: %s /path/to/coreruleset/" % (sys.argv[0]))
        sys.exit(1)
    # from argument, build the rules path and regression test paths
    crspath = sys.argv[1].rstrip("/") + "/rules/*.conf"
    testpath = sys.argv[1].rstrip("/") + "/tests/regression/tests/*"
    retval = 0
    # collect rules
    try:
        flist = glob.glob(crspath)
        flist.sort()
    except:
        print("Can't open files in given path!")
        print(sys.exc_info())
        sys.exit(1)

    # collect test cases
    try:
        tlist = glob.glob(testpath)
        tlist.sort()
    except:
        print("Can't open files in given path (%s)!" % (testpath))
        print(sys.exc_info())
        sys.exit(1)
    # find the yaml files with name REQUEST at the begin
    # collect them in a dictionary
    for t in tlist:
        tname = t.split("/")[-1]
        if tname[:7] == "REQUEST":
            testlist = glob.glob(t + "/*.yaml")
            testlist.sort()
            for tc in testlist:
                tcname = tc.split("/")[-1].split(".")[0]
                test_cases[int(tcname)] = 1

    # iterate the rule files
    for f in flist:
        fname = f.split("/")[-1]
        if fname[:7] == "REQUEST":
            try:
                with open(f, 'r') as inputfile:
                    data = inputfile.read()
            except:
                print("Can't open file: %s" % f)
                print(sys.exc_info())
                sys.exit(1)

            try:
                # make a structure
                mparser = msc_pyparser.MSCParser()
                mparser.parser.parse(data)
                # add the parsed structure to a function, which finds the 'id'-s,
                # and the collected test cases
                find_ids(mparser.configlines, test_cases)
            except:
                print("Can't parse config file: %s" % (f))
                print(sys.exc_info()[1])
                sys.exit(1)
    sys.exit(retval)
