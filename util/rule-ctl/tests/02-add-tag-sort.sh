#!/bin/bash

MY_PATH="`dirname \"$0\"`"
FILELEN=$[$(cat $MY_PATH/rules.conf | wc -l)+0]

python3 $MY_PATH/../rule-ctl.py \
    --append-tag foo \
    --sort-tag \
    --config $MY_PATH/rules.conf --filter-rule-id ^12 --debug --target-file $MY_PATH/results.conf

RESLEN=$[$(cat $MY_PATH/results.conf | wc -l)+0]

if [[ $[$FILELEN+2] -eq $RESLEN ]]; then
    echo "[*] Test passed."
    exit 0
else
    echo "[!] Failed: orig file len $[$FILELEN+2] / destination file len ${RESLEN}"
    exit 2
fi
