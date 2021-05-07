import os, sys, re, json

try:
    import argparse, msc_pyparser
except:
    print(f"Error: missing modules.\nYou can install all dependences with: pip3 install -r requirements.txt")
    sys.exit(1)

parser = argparse.ArgumentParser(description="OWASP CRS Configuration Control")
parser.add_argument("--config", dest="config", help="OWASP ModSecurity CRS config files path", required=True)
parser.add_argument("--filter-rule-id", dest="filter_rule_id", help="Filter on ruleid (regex)", required=True)
parser.add_argument("--append-variable", dest="append_variable", help="Append var on SecRule (string)", action='append', required=False)
parser.add_argument("--remove-variable", dest="remove_variable", help="Remove var from SecRule (string)", action='append', required=False)
parser.add_argument("--replace-variable", dest="replace_variable", help="Replace var in SecRule (old,new) (string)", action='append', required=False)
parser.add_argument("--replace-variable-name", dest="replace_variable_name", help="Replace var name in SecRule (old,new) (string)", action='append', required=False)
parser.add_argument("--append-tag", dest="append_tag", help="Append tag on SecRule (string)", required=False)
parser.add_argument("--remove-tag", dest="remove_tag", help="Remove tag from SecRule (string)", required=False)
parser.add_argument("--rename-tag", dest="rename_tag", help="Rename tag on SecRule (old,new) (string)", required=False)
parser.add_argument("--sort-tags", dest="sort_tags", help="Sort tag list in SecRule", action="store_true", required=False)
parser.add_argument("--append-tfunc", dest="append_tfunc", help="Append transformation func on SecRule (example: urlDecodeUni) (string)", action='append', required=False)
parser.add_argument("--remove-tfunc", dest="remove_tfunc", help="Remove transformation func from SecRule (example: urlDecodeUni) (string)", action='append', required=False)
parser.add_argument("--replace-action", dest="replace_action", help="Replace action (example: 'severity:CRITICAL,severity:INFO') (string)", required=False)
parser.add_argument("--uncond-replace-action", dest="uncond_replace_action", help="Unconditional replace action (example: 'msg:foo bar') (string)", required=False)
parser.add_argument("--remove-action", dest="remove_action", help="Remove action from SecRule (string)", required=False)
parser.add_argument("--append-ctl", dest="append_ctl", help="Append ctl action on SecRule (string)", required=False)
parser.add_argument("--target-file", dest="target_file", help="Save changes in another file (string)", required=False)
parser.add_argument("--skip-chain", dest="skip_chain", help="Skip chained rules", action="store_true", required=False)
parser.add_argument("--dryrun", dest="dryrun", help="Show changes without write", action="store_true", required=False)
parser.add_argument("--silent", dest="silent", help="Do not output content file on dryrun", action="store_true", required=False)
parser.add_argument("--debug", dest="debug", help="Show debug messages", action="store_true", required=False)
parser.add_argument("--json", dest="output_json", help="Get all output in JSON format", action="store_true", required=False)
args = parser.parse_args()

def dprint(rule_id, action, message, indent):
    if not indent:
        indent=0

    prefix = "[*]"
    if indent > 0:
        prefix = "`"

    if not rule_id:
        rule_id = "chained"

    print(f'{" "*int(indent)}{prefix} \033[92m{rule_id}/{action}\033[0m: {message}')

def rules_get_id(mscline):
    if mscline["type"] == "SecRule":
        for act in mscline["actions"]:
            if act["act_name"] == "id":
                return int(act["act_arg"])
    return False

def rules_get_last_tag_line(mscline):
    last_tag_line = 0
    if mscline["type"] == "SecRule":
        for act in mscline["actions"]:
            if act["act_name"] == "tag":
                last_tag_line = act["lineno"]
    return last_tag_line

def rules_var_append(mscline, newvar, newvarpart, negated, counter):
    new_var_list = []
    if mscline["type"] == "SecRule":
        if "variables" in mscline:
            for v in mscline["variables"]:
                new_var_list.append(v)
            new_var_list.append({
                "variable": newvar,
                "variable_part": newvarpart,
                "quote_type": "no_quote",
                "negated": negated,
                "counter": counter
            })
            if args.debug:
                dprint(rules_get_id(mscline), "append-variable", f"Append variable {newvar}:{newvarpart}", 0)
    return new_var_list

def rules_var_remove(mscline, var, varpart, negated, counter):
    new_var_list = []
    if mscline["type"] == "SecRule":
        if "variables" in mscline:
            for v in mscline["variables"]:
                if v["variable"] != var or v["variable_part"] != varpart or v["negated"] != negated or v["counter"] != counter:
                    new_var_list.append(v)
                else:
                    if args.debug:
                        dprint(rules_get_id(mscline), "remove-variable", f"Removed variable {var}:{varpart} negated:{negated} counter:{counter}", 0)
    return new_var_list

def rules_var_replace(mscline, newvar, newvarpart, newnegated, newcounter, oldvar, oldvarpart, oldnegated, oldcounter):
    new_var_list = []
    if mscline["type"] == "SecRule":
        if "variables" in mscline:
            for v in mscline["variables"]:
                if v["variable"] == oldvar and v["variable_part"] == oldvarpart and v["negated"] == oldnegated and v["counter"] == oldcounter:
                    new_var_list.append({
                        "variable": newvar,
                        "variable_part": newvarpart,
                        "quote_type": "no_quote",
                        "negated": newnegated,
                        "counter": newcounter
                    })
                    if args.debug:
                        dprint(rules_get_id(mscline), "replace-variable", f"Replaced variable {oldvar}:{oldvarpart} negated:{oldnegated} counter:{oldcounter} with {newvar}:{newvarpart} negated:{newnegated} counter:{newcounter}", 0)
                else:
                    new_var_list.append(v)
    return new_var_list

def rules_var_replace_name(mscline, newvar, oldvar):
    new_var_list = []
    if mscline["type"] == "SecRule":
        if "variables" in mscline:
            for v in mscline["variables"]:
                if v["variable"] == oldvar:
                    new_var_list.append({
                        "variable": newvar,
                        "variable_part": v["variable_part"],
                        "quote_type": "no_quote",
                        "negated": v["negated"],
                        "counter": v["counter"]
                    })
                    if args.debug:
                        dprint(rules_get_id(mscline), "replace-variable-name", f"Replaced variable name for {oldvar}:{v['variable_part']} with {newvar}", 0)
                else:
                    new_var_list.append(v)
    return new_var_list

def rules_tag_append(mscline, newtag, last_tag_line):
    new_act_list = []
    increment_lineno = False
    if mscline["type"] == "SecRule":
        for act in mscline["actions"]:
            if act["act_name"] == "id":
                current_rule_id = act["act_arg"]
            if act["act_name"] == "tag":
                if act["lineno"] == last_tag_line:
                    new_act_list.append(act)
                    last_tag_line += 1
                    new_act_list.append({
                        'act_name': 'tag',
                        'lineno': last_tag_line,
                        'act_quote': 'quotes',
                        'act_arg': newtag,
                        'act_arg_val': '',
                        'act_arg_val_param': '',
                        'act_arg_val_param_val': ''
                    })
                    if args.debug:
                        dprint(current_rule_id, "append-tag", f"append tag {newtag} on line {last_tag_line}", 0)
                    increment_lineno = True
                else:
                    new_act_list.append(act)
            else:
                if increment_lineno:
                    last_tag_line += 1
                    act["lineno"] = last_tag_line
                new_act_list.append(act)
    return new_act_list

def rules_tag_remove(mscline, tag):
    new_act_list = []
    if mscline["type"] == "SecRule":
        for act in mscline["actions"]:
            if act["act_name"] == "id":
                current_rule_id = act["act_arg"]
            if act["act_name"] == "tag":
                if act["act_arg"] != tag:
                    new_act_list.append(act)
                else:
                    if args.debug:
                        dprint(current_rule_id, "remove-tag", f"remove tag {tag} on line {act['lineno']}", 0)
            else:
                new_act_list.append(act)

    return new_act_list

def rules_has_tfunc(mscline):
    if "actions" in mscline:
        for act in mscline["actions"]:
            if act["act_name"] == "t":
                return True
    return False

def rules_tag_rename(mscline, oldtag, newtag):
    new_act_list = []
    if mscline["type"] == "SecRule":
        for act in mscline["actions"]:
            if act["act_name"] == "id":
                current_rule_id = act["act_arg"]
            if act["act_name"] == "tag":
                if act["act_arg"] == oldtag:
                    act["act_arg"] = newtag
                    if args.debug:
                        dprint(current_rule_id, "rename-tag", f"rename tag {oldtag} to {newtag} on line {act['lineno']}", 0)
                new_act_list.append(act)
            else:
                new_act_list.append(act)
    return new_act_list

def rules_tag_sort(mscline):
    new_act_list = []
    tags = []
    found_tag = False
    last_lineno = 0
    if mscline["type"] == "SecRule":
        for act in mscline["actions"]:
            if act["act_name"] == "tag":
                tags.append(act["act_arg"])

        for act in mscline["actions"]:
            if act["act_name"] == "tag":
                found_tag = True
                last_lineno = act["lineno"]
                break
            else:
                new_act_list.append(act)

        sorted_tags = sorted(tags, key=str.lower)
        for st in sorted_tags:
            new_act_list.append({
                'act_name': 'tag',
                'lineno': last_lineno,
                'act_quote': 'quotes',
                'act_arg': st,
                'act_arg_val': '',
                'act_arg_val_param': '',
                'act_arg_val_param_val': ''
            })
            last_lineno += 1

        found_tag = False
        for act in mscline["actions"]:
            if act["act_name"] == "tag":
                found_tag = True
            else:
                if found_tag:
                    new_act_list.append(act)
                    #act["lineno"] += 1
                
    return new_act_list

def rules_tfunc_append(mscline, tfunc):
    new_act_list = []
    found_t = False
    found_msg = False
    increment_lineno = False
    last_lineno = 0
    if mscline["type"] == "SecRule":
        if rules_has_tfunc(i):
            for act in mscline["actions"]:
                if act["act_name"] == "t":
                    found_t = True
                    last_lineno = act["lineno"]
                    new_act_list.append(act)
                else:
                    if found_t:
                        new_act_list.append({
                            'act_name': 't', 
                            'lineno': last_lineno, 
                            'act_quote': 'no_quote', 
                            'act_arg': tfunc, 
                            'act_arg_val': '', 
                            'act_arg_val_param': '', 
                            'act_arg_val_param_val': ''
                        })
                        new_act_list.append(act)
                        found_t = False
                    else:
                        new_act_list.append(act)
        else:
            increment_lineno = True
            for act in mscline["actions"]:
                if act["act_name"] == "msg":
                    found_msg = True
                    new_act_list.append({
                            'act_name': 't', 
                            'lineno': act["lineno"], 
                            'act_quote': 'no_quote', 
                            'act_arg': tfunc, 
                            'act_arg_val': '', 
                            'act_arg_val_param': '', 
                            'act_arg_val_param_val': ''
                    })
                    act["lineno"] += 1
                    new_act_list.append(act)
                else:
                    new_act_list.append(act)
    return new_act_list, increment_lineno

def rules_tfunc_remove(mscline, tfunc):
    new_act_list = []
    found_t = False
    decrement_lineno = False
    if mscline["type"] == "SecRule":
        if rules_has_tfunc(i):
            for act in mscline["actions"]:
                if act["act_name"] == "t":
                    if act["act_arg"] != tfunc:
                        new_act_list.append(act)
                else:
                    new_act_list.append(act)
        else:
            return mscline["actions"],False
        
        for act in new_act_list:
            if act["act_name"] == "t":
                found_t = True
        if found_t:
            decrement_lineno = True

    return new_act_list, decrement_lineno

def replace_action(mscline, from_actname,from_actvalue,to_actname,to_actvale):
    new_act_list = []
    if "actions" in mscline:
        for act in mscline["actions"]:
            if act["act_name"] == from_actname and act["act_arg"] == from_actvalue:
                act["act_name"] = to_actname
                act["act_arg"] = to_actvale
                new_act_list.append(act)
            else:
                new_act_list.append(act)
    return new_act_list

def uncond_replace_action(mscline, actname, actvalue):
    new_act_list = []
    if "actions" in mscline:
        for act in mscline["actions"]:
            if act["act_name"] == actname:
                act["act_arg"] = actvalue
                new_act_list.append(act)
            else:
                new_act_list.append(act)
    return new_act_list

def remove_action(mscline, actname):
    new_act_list = []
    if "actions" in mscline:
        for act in mscline["actions"]:
            if act["act_name"] != actname:
                new_act_list.append(act)

    return new_act_list

def rule_ctl_append(mscline, arg, val, param, paramval):
    new_act_list = []
    increment_lineno = False
    ver_found = False
    if mscline["type"] == "SecRule":
        for act in mscline["actions"]:
            last_line = act["lineno"]
            if act["act_name"] == "ver":
                ver_found = True
                new_act_list.append({
                    "act_name": "ctl",
                    "lineno": last_line,
                    "act_quote": "no_quote",
                    "act_arg": arg,
                    "act_arg_val": val,
                    "act_arg_val_param": param,
                    "act_arg_val_param_val": paramval
                })
                increment_lineno = True

            if increment_lineno:
                act["lineno"] += 1

            new_act_list.append(act)

        if not ver_found:
            last_line += 1
            new_act_list.append({
                "act_name": "ctl",
                "lineno": last_line,
                "act_quote": "no_quote",
                "act_arg": arg,
                "act_arg_val": val,
                "act_arg_val_param": param,
                "act_arg_val_param_val": paramval
            })
    return new_act_list

def parse_var(variable):
    negated,counter = False,False
    if variable[0:1] == "!":
        negated = True
    if variable[0:1] == "&":
        counter = True
    m = re.match('^([!&]*)([^:]+):(.+)$', variable)
    if m:
        newvar = m.group(2)
        newvarpart = m.group(3)
    else:
        newvar = variable
        newvarpart = ""
    return {
        "variable": newvar,
        "variable_part": newvarpart,
        "quote_type": "no_quote",
        "negated": negated,
        "counter": counter
    }

with open(args.config) as file:
    data = file.read()

    mparser = msc_pyparser.MSCParser()
    mparser.parser.parse(data, debug = False)

    increment_lineno = False
    decrement_lineno = False

    l = 0
    last_rule_id = 0
    for i in mparser.configlines:
        if "chained" in mparser.configlines[l] and mparser.configlines[l]["chained"] and args.skip_chain:
            continue

        rule_id = rules_get_id(i)
        if not rule_id:
            rule_id = last_rule_id

        main_lineno = 0

        if increment_lineno:
            if "lineno" in i:
                main_lineno = i["lineno"]
                mparser.configlines[l]["lineno"] += 1

            if "oplineno" in i:
                mparser.configlines[l]["oplineno"] += 1

            act_n = 0
            if "actions" in i:
                for act in i["actions"]:
                    if act["lineno"] != main_lineno:
                        mparser.configlines[l]["actions"][act_n]["lineno"] += 1
                    else:
                        mparser.configlines[l]["actions"][act_n]["lineno"] = mparser.configlines[l]["lineno"]
                    act_n += 1
        
        if decrement_lineno:
            if "lineno" in i:
                main_lineno = i["lineno"]
                mparser.configlines[l]["lineno"] -= 1

            if "oplineno" in i:
                mparser.configlines[l]["oplineno"] -= 1

            act_n = 0
            if "actions" in i:
                for act in i["actions"]:
                    if act["lineno"] != main_lineno:
                        mparser.configlines[l]["actions"][act_n]["lineno"] -= 1
                    else:
                        mparser.configlines[l]["actions"][act_n]["lineno"] = mparser.configlines[l]["lineno"]
                    act_n += 1

        if args.filter_rule_id:
            if re.match(args.filter_rule_id, str(rule_id)) is None:
                l += 1
                continue

        if "chained" in mparser.configlines[l] and mparser.configlines[l]["chained"]:
            last_rule_id = rule_id

        if args.append_tag:
            last_tag_line = rules_get_last_tag_line(mparser.configlines[l])
            new_act = rules_tag_append(mparser.configlines[l], args.append_tag, last_tag_line)
            if len(new_act) > 0:
                    mparser.configlines[l]["actions"] = new_act
                    increment_lineno = True

        if args.remove_tag:
            new_act = rules_tag_remove(mparser.configlines[l], args.remove_tag)
            mparser.configlines[l]["actions"] = new_act
            #decrement_lineno = True
        
        if args.rename_tag:
            m = re.match('^([^,]+),(.+)$', args.rename_tag)
            if m:
                new_act = rules_tag_rename(i, m.group(1), m.group(2))
                mparser.configlines[l]["actions"] = new_act

        if args.append_tfunc:
            if type(args.append_tfunc) is list:
                for atfunc in args.append_tfunc:
                    new_act,increment_lineno = rules_tfunc_append(mparser.configlines[l], atfunc)
                    mparser.configlines[l]["actions"] = new_act
        
        if args.remove_tfunc:
            if type(args.remove_tfunc) is list:
                for rtfunc in args.remove_tfunc:
                    new_act,decrement_lineno = rules_tfunc_remove(mparser.configlines[l], rtfunc)
                    mparser.configlines[l]["actions"] = new_act

        if args.replace_action:
            m = re.match('^([^:]+):([^,]+),([^:]+):(.+)$', args.replace_action)
            if m:
                new_act = replace_action(i, m.group(1), m.group(2), m.group(3), m.group(4))
                mparser.configlines[l]["actions"] = new_act
        
        if args.uncond_replace_action:
            m = re.match('^([^:]+):(.+)$', args.uncond_replace_action)
            if m:
                new_act = uncond_replace_action(i, m.group(1), m.group(2))
                mparser.configlines[l]["actions"] = new_act

        if args.remove_action:
            new_act = remove_action(i, args.remove_action)
            mparser.configlines[l]["actions"] = new_act
            #decrement_lineno = True
        
        if args.append_variable:
            if type(args.append_variable) is list:
                for nv in args.append_variable:
                    newvar = parse_var(nv)
                    mparser.configlines[l]["variables"] = rules_var_append(mparser.configlines[l], newvar["variable"], newvar["variable_part"], newvar["negated"], newvar["counter"])

        if args.remove_variable:
            if type(args.remove_variable) is list:
                for nv in args.remove_variable:
                    var = parse_var(nv)
                    mparser.configlines[l]["variables"] = rules_var_remove(mparser.configlines[l], var["variable"], var["variable_part"], var["negated"], var["counter"])

        if args.replace_variable:
            if type(args.replace_variable) is list:
                for nv_tosplit in args.replace_variable:
                    newvar,oldvar = nv_tosplit.split(",")
                    ov = parse_var(newvar)
                    nv = parse_var(oldvar)

                    mparser.configlines[l]["variables"] = rules_var_replace(
                        mparser.configlines[l],
                        nv["variable"],
                        nv["variable_part"],
                        nv["negated"],
                        nv["counter"],
                        ov["variable"],
                        ov["variable_part"],
                        ov["negated"],
                        ov["counter"]
                    )

        if args.replace_variable_name:
            if type(args.replace_variable_name) is list:
                for nv_tosplit in args.replace_variable_name:
                    oldvar,newvar = nv_tosplit.split(",")
                    mparser.configlines[l]["variables"] = rules_var_replace_name(mparser.configlines[l], newvar, oldvar)

        if args.append_ctl:
            m = re.match('^([^=]+)=([^;]+)(;[^:]+:.+|)$', args.append_ctl)
            if m:
                arg = m.group(1)
                val = m.group(2)
            
                mp = re.match('^;([^:]+):(.+)$', m.group(3))
                if mp:
                    param = mp.group(1)
                    paramval = mp.group(2)
                else:
                    param,paramval = "",""

            new_act = rule_ctl_append(mparser.configlines[l], arg, val, param, paramval)
            if len(new_act) > 0:
                mparser.configlines[l]["actions"] = new_act
                increment_lineno = True

        if args.sort_tags:
            new_act = rules_tag_sort(mparser.configlines[l])
            mparser.configlines[l]["actions"] = new_act

        l += 1
    
    mwriter = msc_pyparser.MSCWriter(mparser.configlines)
    mwriter.generate()
    
    if args.dryrun:
        if args.output_json:
            print(json.dumps(mparser.configlines, indent=4))
        else:
            if not args.silent:
                print("\n".join(mwriter.output))
    else:
        if args.target_file:
            f = open(args.target_file, 'w')
        else:
            f = open(args.config, 'w')
        f.write("\n".join(mwriter.output))
        f.close()
