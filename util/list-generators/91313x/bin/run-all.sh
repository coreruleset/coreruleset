#!/bin/bash
#
# OWASP ModSecurity Core Rule Set helper script
#
# This script is used to retrieve the online lists and create the data files for the
# 91313x rule family.
#

ERROR=0

DEST_FOLDER=../../../rules

function break_on_error {
        if [ $1 -ne 0 ]; then
                echo "FAILED. This is fatal. Aborting"
                exit 1
        fi
}

echo -n "Retrieving full list of user-agents ... "
./bin/retrieve-full-UA-list.sh > user-agents-automated-agents.src
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"

echo -n "Retrieving list of good bots ... "
./bin/retrieve-mitchellkrogza-good-bots.sh > acceptable-bots-mitchellkrogza.src
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"

echo -n "Creating list of non-acceptable automated user-agents ... "
./bin/create-user-agents-security-scanners.sh > $DEST_FOLDER/user-agents-security-scanners.data
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"

echo -n "Creating list of user-agents associated with security-scanners ... "
./bin/create-user-agents-non-acceptable-automated-agents.sh > $DEST_FOLDER/user-agents-non-acceptable-automated-agents.data
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"

echo -n "Creating list of automated user-agents ... "
./bin/create-user-agents-automated-agents.sh > $DEST_FOLDER/user-agents-automated-agents.data
ERROR=$(($ERROR|$?))    # logical OR
break_on_error $ERROR
echo "done"
