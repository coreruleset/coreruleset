#!/bin/bash

if ! command -v spell > /dev/null 2>&1; then
    echo "This program requires spell to be installed. Aborting"
    exit 1
fi

check() {
    local datafile="${1}"
    local datafile_name="${datafile##*/}"

    if ! ${MACHINE_READABLE}; then
        echo "-> checking ${datafile_name}"
    fi

    for word in $(grep -E '^[a-z]+$' "${datafile}" | uniq | sort); do
        IS_NOT_ENGLISH=$(echo "${word}" | spell | wc -l)
        if [ "${IS_NOT_ENGLISH}" -lt 1 ]; then
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
usage: spell.sh [-ph] [file]
    Finds English words in files that contain word lists.

    The optional file argument is the path to a file you want to check. If omitted,
    all files with the .data suffix in the rules directory will be searched.

    -h, --help     \tShow this message and exit
    -m, --machine\tPrint machine readable output
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
