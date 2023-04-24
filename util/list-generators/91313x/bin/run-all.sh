#!/bin/bash
#
# OWASP ModSecurity Core Rule Set helper script
#
# This script is used to retrieve the online lists and create the data files for the
# 91313x rule family.
#

ERROR=0

function break_on_error {
        if [ $1 -ne 0 ]; then
                echo
                echo "FAILED. This is fatal. Aborting"
                exit 1
        fi
}

echo -n "Retrieving full list of user-agents ... "
./bin/retrieve-full-UA-list.sh
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"

echo -n "Retrieving list of good bots ... "
./bin/retrieve-mitchellkrogza-good-bots.sh
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"

echo -n "Creating list of user-agents associated with security-scanners ... "
./bin/create-user-agents-non-acceptable-automated-agents.sh
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"

echo -n "Creating list of non-acceptable automated user-agents ... "
./bin/create-user-agents-security-scanners.sh
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"

echo -n "Creating list of automated user-agents ... "
./bin/create-user-agents-automated-agents.sh
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"
