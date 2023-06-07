#!/bin/bash

# This script finds common English words in .data files (if no argument provided).
# Or it finds english words in the provided input file (one argument).

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
RULES_DIR="${SCRIPT_DIR}/../../rules/"

# If no argument provided:
if [ $# -eq 0 ]
  then
    for datafile in "$RULES_DIR"*.data; do
      DATAFILE_NAME=${datafile##*/}
      echo "-> checking ${DATAFILE_NAME}"
      for word in $(grep -E '^[a-z]+$' "${datafile}" | uniq | sort); do
        IS_NOT_ENGLISH=$(echo "${word}" | spell | wc -l)
        if [ "${IS_NOT_ENGLISH}" -lt 1 ]; then
            echo "   \`- found English word: ${word}"
        fi
      done
    echo ""
  done
# If argument provided, check this file:
else
  datafile=$SCRIPT_DIR/../../$1
  DATAFILE_NAME=${datafile##*/}
  for word in $(grep -E '[a-z]+$' "${datafile}" | grep -vE [#@\\] | uniq | sort); do
    IS_NOT_ENGLISH=$(echo "${word}" | spell | wc -l)
    if [ "${IS_NOT_ENGLISH}" -lt 1 ]; then
      echo "   \`- found English word: ${word}"
    fi
  done
  echo ""
fi
