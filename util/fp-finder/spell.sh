#!/bin/bash

# This program uses WordNet to find English words. The WordNet license:

# WordNet Release 3.0 This software and database is being provided to you,
# the LICENSEE, by Princeton University under the following license.
# By obtaining, using and/or copying this software and database, you agree that you have read,
# understood, and will comply with these terms and conditions.: Permission to use, copy,
# modify and distribute this software and database and its documentation for any purpose and
# without fee or royalty is hereby granted, provided that you agree to comply with
# the following copyright notice and statements, including the disclaimer, and that the same
# appear on ALL copies of the software, database and documentation, including modifications
# that you make for internal use or for distribution.
# WordNet 3.0 Copyright 2006 by Princeton University.
# All rights reserved.
# THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS
# OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, PRINCETON UNIVERSITY
# MAKES NO REPRESENTATIONS OR WARRANTIES OF MERCHANT- ABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE
# OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT INFRINGE ANY THIRD
# PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS.
# The name of Princeton University or Princeton may not be used in advertising or publicity
# pertaining to distribution of the software and/or database. Title to copyright in this
# software, database and any associated documentation shall at all times remain with
# Princeton University and LICENSEE agrees to preserve same.

if ! command -v wn > /dev/null 2>&1; then
    cat <<EOF
This program requires WordNet to be installed. Aborting.

The WordNet shell utility 'wn' can be obtained via the package
manager of your choice (the package is usually called 'wordnet').
EOF

    exit 1
fi

check() {
    local datafile="${1}"
    local datafile_name="${datafile##*/}"

    if ! ${MACHINE_READABLE}; then
        echo "-> checking ${datafile_name}"
    fi

    for word in $(grep -E '^[a-z]+$' "${datafile}" | uniq | sort); do
        # wordnet exit code is equal to number of search results
        if ! wn "${word}"> /dev/null 2>&1;  then
            if ! ${MACHINE_READABLE}; then
                printf "   \`- found English word: "
            fi
            echo "${word}"
        fi
    done

    if ! ${MACHINE_READABLE}; then
        echo ""
    fi
}

usage() {
    cat <<EOF
usage: spell.sh [-mh] [file]
    Finds English words in files that contain word lists.

    The optional file argument is the path to a file you want to check. If omitted,
    all files with the .data suffix in the rules directory will be searched.

    -h, --help      Show this message and exit
    -m, --machine   Print machine readable output
EOF
}

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

RULES_DIR="${SCRIPT_DIR}/../../rules/"

MACHINE_READABLE=false

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    # shellcheck disable=SC2221,SC2222
    case $1 in
        -m|--machine)
        MACHINE_READABLE=true
        shift # past argument
        ;;
        -h|--help)
        usage
        exit 1
        ;;
        -*|--*)
        echo "Unknown option $1"
        usage
        exit 1
        ;;
        *)
        POSITIONAL_ARGS+=("$1") # save positional arg
        shift # past argument
        ;;
    esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters


if [ -n "${1}" ]; then
    check "${1}"
else
    for datafile in "${RULES_DIR}"*.data; do
        check "${datafile}"
    done
fi
