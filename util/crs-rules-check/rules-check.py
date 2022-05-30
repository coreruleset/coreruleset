#!/usr/bin/env python3

import sys
import os
import glob
import msc_pyparser
import difflib
import argparse
import re

oformat = "native"

class Check(object):
    def __init__(self, data):

        # list available operators, actions, transformations and ctl args
        self.operators   = "beginsWith|containsWord|contains|detectSQLi|detectXSS|endsWith|eq|fuzzyHash|geoLookup|ge|gsbLookup|gt|inspectFile|ipMatch|ipMatchF|ipMatchFromFile|le|lt|noMatch|pmFromFile|pmf|pm|rbl|rsub|rx|streq|strmatch|unconditionalMatch|validateByteRange|validateDTD|validateHash|validateSchema|validateUrlEncoding|validateUtf8Encoding|verifyCC|verifyCPF|verifySSN|within".split("|")
        self.operatorsl  = [o.lower() for o in self.operators]
        self.actions     = "accuracy|allow|append|auditlog|block|capture|chain|ctl|deny|deprecatevar|drop|exec|expirevar|id|initcol|logdata|log|maturity|msg|multiMatch|noauditlog|nolog|pass|pause|phase|prepend|proxy|redirect|rev|sanitiseArg|sanitiseMatched|sanitiseMatchedBytes|sanitiseRequestHeader|sanitiseResponseHeader|setenv|setrsc|setsid|setuid|setvar|severity|skipAfter|skip|status|tag|t|ver|xmlns".split("|")
        self.actionsl    = [a.lower() for a in self.actions]
        self.transforms  = "base64DecodeExt|base64Decode|base64Encode|cmdLine|compressWhitespace|cssDecode|escapeSeqDecode|hexDecode|hexEncode|htmlEntityDecode|jsDecode|length|lowercase|md5|none|normalisePathWin|normalisePath|normalizePathWin|normalizePath|parityEven7bit|parityOdd7bit|parityZero7bit|removeCommentsChar|removeComments|removeNulls|removeWhitespace|replaceComments|replaceNulls|sha1|sqlHexDecode|trimLeft|trimRight|trim|uppercase|urlDecodeUni|urlDecode|urlEncode|utf8toUnicode".split("|")
        self.transformsl = [t.lower() for t in self.transforms]
        self.ctls        = "auditEngine|auditLogParts|debugLogLevel|forceRequestBodyVariable|hashEnforcement|hashEngine|requestBodyAccess|requestBodyLimit|requestBodyProcessor|responseBodyAccess|responseBodyLimit|ruleEngine|ruleRemoveById|ruleRemoveByMsg|ruleRemoveByTag|ruleRemoveTargetById|ruleRemoveTargetByMsg|ruleRemoveTargetByTag".split("|")
        self.ctlsl       = [c.lower() for c in self.ctls]

        # list the actions in expected order
        # see wiki: https://github.com/SpiderLabs/owasp-modsecurity-crs/wiki/Order-of-ModSecurity-Actions-in-CRS-rules
        # note, that these tokens are with lovercase here, but used only for to check the order
        self.ordered_actions = [
            "id",                   # 0
            "phase",                # 1
            "allow",
            "block",
            "deny",
            "drop",
            "pass",
            "proxy",
            "redirect",
            "status",
            "capture",              # 10
            "t",
            "log",
            "nolog",
            "auditlog",
            "noauditlog",
            "msg",
            "logdata",
            "tag",
            "sanitisearg",
            "sanitiserequestheader",    # 20
            "sanitisematched",
            "sanitisematchedbytes",
            "ctl",
            "ver",
            "severity",
            "multimatch",
            "initcol",
            "setenv",
            "setvar",
            "expirevar",            # 30
            "chain",
            "skip",
            "skipafter",
        ]

        self.data           = data  # holds the parsed data
        self.current_ruleid = 0     # holds the rule id
        self.curr_lineno    = 0     # current line number
        self.chained        = False # holds the chained flag
        self.caseerror      = []    # list of case mismatch errors
        self.orderacts      = []    # list of ordered action errors
        self.auditlogparts  = []    # list of wrong ctl:auditLogParts

    def store_error(self, msg):
        # store the error msg in the list
        self.caseerror.append({
                                'ruleid' : 0,
                                'line'   : self.curr_lineno,
                                'endLine': self.curr_lineno,
                                'message': msg
                            })

    def check_ignore_case(self):
        # check the ignore cases at operators, actions,
        # transformations and ctl arguments
        for d in self.data:
            if "actions" in d:
                aidx = 0        # index of action in list
                if self.chained == False:
                    self.current_ruleid = 0
                else:
                    self.chained = False

                while aidx < len(d['actions']):
                    a = d['actions'][aidx]  # 'a' is the action from the list

                    self.curr_lineno = a['lineno']
                    if a['act_name'] == "id":
                        self.current_ruleid = int(a['act_arg'])

                    if a['act_name'] == "chain":
                        self.chained = True

                    # check the action is valid
                    if a['act_name'].lower() not in self.actionsl:
                        self.store_error("Invalid action", a['act_name'])
                    # check the action case sensitive format
                    if self.actions[self.actionsl.index(a['act_name'].lower())] != a['act_name']:
                        self.store_error("Action case mismatch: %s" % a['act_name'])

                    if a['act_name'] == 'ctl':
                        # check the ctl argument is valid
                        if a['act_arg'].lower() not in self.ctlsl:
                            self.store_error("Invalid ctl", a['act_arg'])
                        # check the ctl argument case sensitive format
                        if self.ctls[self.ctlsl.index(a['act_arg'].lower())] != a['act_arg']:
                            self.store_error("Ctl case mismatch: %s" % a['act_arg'])
                    if a['act_name'] == 't':
                        # check the transform is valid
                        if a['act_arg'].lower() not in self.transformsl:
                            self.store_error("Invalid transform: %s" % a['act_arg'])
                        # check the transform case sensitive format
                        if self.transforms[self.transformsl.index(a['act_arg'].lower())] != a['act_arg']:
                            self.store_error("Transform case mismatch : %s" % a['act_arg'])
                    aidx += 1
            if "operator" in d and d["operator"] != "":
                self.curr_lineno = d['oplineno']
                # strip the operator
                op = d['operator'].replace("!", "").replace("@", "")
                # check the operator is valid
                if op.lower() not in self.operatorsl:
                    self.store_error("Invalid operator: %s" % d['operator'])
                # check the operator case sensitive format
                if self.operators[self.operatorsl.index(op.lower())] != op:
                    self.store_error("Operator case mismatch: %s" % d['operator'])
            else:
                if d['type'].lower() == "secrule":
                    self.curr_lineno = d['lineno']
                    self.store_error("Empty operator isn't allowed")
            if self.current_ruleid > 0:
                for e in self.caseerror:
                    e['ruleid'] = self.current_ruleid
                    e['message'] += " (rule: %d)" % (self.current_ruleid)

    def check_action_order(self):
        for d in self.data:
            if "actions" in d:
                aidx = 0        # stores the index of current action
                max_order = 0   # maximum position of read actions
                if self.chained == False:
                    self.current_ruleid = 0
                else:
                    self.chained = False

                while aidx < len(d['actions']):
                    # read the action into 'a'
                    a = d['actions'][aidx]

                    # get the 'id' of rule
                    self.curr_lineno = a['lineno']
                    if a['act_name'] == "id":
                        self.current_ruleid = int(a['act_arg'])

                    # check if chained
                    if a['act_name'] == "chain":
                        self.chained = True

                    # get the index of action from the ordered list
                    # above from constructor
                    try:
                        act_idx = self.ordered_actions.index(a['act_name'].lower())
                    except ValueError:
                        print("ERROR: '%s' not in actions list!" % (a['act_name']))
                        sys.exit(-1)

                    # if the index of current action is @ge than the previous
                    # max value, load it into max_order
                    if act_idx >= max_order:
                        max_order = act_idx
                    else:
                        # prevact is the previous action's position in list
                        # act_idx is the current action's position in list
                        # if the prev is @gt actually, means it's at wrong position
                        if self.ordered_actions.index(prevact) > act_idx:
                            self.orderacts.append({
                                'ruleid' : 0,
                                'line'   : a['lineno'],
                                'endLine': a['lineno'],
                                'message': "action '%s' at pos %d is wrong place against '%s' at pos %d" % (prevact, pidx, a['act_name'], aidx,)
                            })
                    prevact = a['act_name'].lower()
                    pidx = aidx
                    aidx += 1
                for a in self.orderacts:
                    if a['ruleid'] == 0:
                        a['ruleid'] = self.current_ruleid
                        a['message'] += " (rule: %d)" % (self.current_ruleid)

    def check_ctl_audit_log(self):
        for d in self.data:
            if "actions" in d:
                aidx = 0        # stores the index of current action
                max_order = 0   # maximum position of read actions
                if self.chained == False:
                    self.current_ruleid = 0
                else:
                    self.chained = False

                # collect ctl:auditLogParts action if exists
                auditlogparts = []

                while aidx < len(d['actions']):
                    # read the action into 'a'
                    a = d['actions'][aidx]

                    # get the 'id' of rule
                    self.curr_lineno = a['lineno']
                    if a['act_name'] == "id":
                        self.current_ruleid = int(a['act_arg'])

                    # check if chained
                    if a['act_name'] == "chain":
                        self.chained = True

                    # check if action is ctl:auditLogParts
                    if a['act_name'] == "ctl" and a['act_arg'] == "auditLogParts":
                        auditlogparts.append({
                                'ruleid' : 0,
                                'line'   : a['lineno'],
                                'endLine': a['lineno'],
                                'message': "action can only be placed in last part of a chained rule"
                        })

                    aidx += 1
                if self.chained == True and len(auditlogparts) > 0:
                    for a in auditlogparts:
                        a['ruleid'] = self.current_ruleid
                        a['message'] += " (rule: %d)" % (self.current_ruleid)
                        self.auditlogparts.append(a)

def errmsg(msg):
    if oformat == "github":
        print("::error %s" % (msg))
    else:
        print(msg)

def errmsgf(msg):
    if oformat == "github":
        print("::error%sfile={file},line={line},endLine={endLine},title={title}::{message}".format(**msg) % (msg['indent']*" "))
    else:
        print("%sfile={file}, line={line}, endLine={endLine}, title={title}: {message}".format(**msg) % (msg['indent']*" "))

def msg(msg):
    if oformat == "github":
        print("::debug %s" % (msg))
    else:
        print(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CRS Rules Check tool")
    parser.add_argument("-o", "--output", dest="output", help="Output format native[default]|github", required=False)
    parser.add_argument("-r", "--rules", metavar='/path/to/coreruleset/*.conf', type=str,
                            nargs='*', help='Directory path to CRS rules', required=True)
    args = parser.parse_args()

    crspath = args.rules

    if args.output is not None:
        if args.output not in ["native", "github"]:
            print("--output can be one of the 'native' or 'github'. Default value is 'native'")
            sys.exit(1)
    oformat = args.output

    retval = 0
    try:
        flist = crspath
        flist.sort()
    except:
        errmsg("Can't open files in given path!")
        sys.exit(1)

    if len(flist) == 0:
        errmsg("List of files is empty!")
        sys.exit(1)

    for f in flist:
        try:
            with open(f, 'r') as inputfile:
                data = inputfile.read()
        except:
            errmsg("Can't open file: %s" % f)
            sys.exit(1)

        ### check file syntax
        msg("Config file: %s" % (f))
        try:
            mparser = msc_pyparser.MSCParser()
            mparser.parser.parse(data)
            msg(" Parsing ok.")
        except Exception as e:
            err = e.args[1]
            if err['cause'] == "lexer":
                cause = "Lexer"
            else:
                cause = "Parser"
            errmsg("Can't parse config file: %s" % (f))
            errmsgf({
                'indent' : 2,
                'file'   : f,
                'title'  : "%s error" % (cause),
                'line'   : err['line'],
                'endLine': err['line'],
                'message': "can't parse file"})
            retval = 1
            continue

        c = Check(mparser.configlines)

        ### check case usings
        c.check_ignore_case()
        if len(c.caseerror) == 0:
            msg(" Ignore case check ok.")
        else:
            errmsg(" Ignore case check found error(s)")
            for a in c.caseerror:
                a['indent'] = 2
                a['file']   = f
                a['title']  = "Case check"
                errmsgf(a)
                retval = 1

        ### check action's order
        c.check_action_order()
        if len(c.orderacts) == 0:
            msg(" Action order check ok.")
        else:
            errmsg(" Action order check found error(s)")
            for a in c.orderacts:
                a['indent'] = 2
                a['file']   = f
                a['title']  = 'Action order check'
                errmsgf(a)
                retval = 1

        ### make a diff to check the indentations
        try:
            with open(f, 'r') as fp:
                fromlines = fp.readlines()
        except:
            errmsg("  Can't open file for indent check: %s" % (f))
            retval = 1
        # virtual output
        mwriter = msc_pyparser.MSCWriter(mparser.configlines)
        mwriter.generate()
        #mwriter.output.append("")
        output = []
        for l in mwriter.output:
            if l == "\n":
                output.append("\n")
            else:
                output += [l + "\n" for l in l.split("\n")]

        diff = difflib.unified_diff(fromlines, output)
        if fromlines == output:
            msg(" Indentation check ok.")
        else:
            errmsg(" Indentation check found error(s)")
            retval = 1
        for d in diff:
            d = d.strip("\n")
            r = re.match("^@@ -(\d+),(\d+) \+\d+,\d+ @@$", d)
            if r:
                line1, line2 = [int(i) for i in r.groups()]
                e = {
                    'indent' : 2,
                    'file'   : f,
                    'title'  : "Indentation error",
                    'line'   : line1,
                    'endLine': line1+line2,
                    'message': "an indetation error has found"
                }
                errmsgf(e)
            errmsg(d.strip("\n"))

        ### check `ctl:auditLogParts=+E` right place in chained rules
        c.check_ctl_audit_log()
        if len(c.auditlogparts) == 0:
            msg(" 'ctl:auditLogParts' actions are in right place.")
        else:
            errmsg(" Found 'ctl:auditLogParts' action is in wrong place.")
            for a in c.auditlogparts:
                a['indent'] = 2
                a['file']   = f
                a['title']  = "'ctl:auditLogParts' action in wrong place"
                errmsgf(a)
                retval = 1

    sys.exit(retval)
