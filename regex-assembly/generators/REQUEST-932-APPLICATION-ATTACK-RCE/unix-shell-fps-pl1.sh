#!/bin/bash
NL=$'\n'
original="$(grep -vE '^[#$]' regex-assembly/exclude/unix-shell-fps-pl1.ra)"
rest="$(grep -vE '^[#$]' regex-assembly/include/unix-shell-4andup.ra)"
english_upto3="$(crs-toolchain util fp-finder -m -e regex-assembly/include/unix-shell-upto3.ra)"
strip suffixes from words for fp-finder
english_rest="$(crs-toolchain util fp-finder -m -e -s '[@~]' regex-assembly/include/unix-shell-4andup.ra)"
result=""
function update_existing {
  if [ -z "${1}" ]; then
    return
  fi
  while read -r oword; do
    found=0
    while read -r eword; do
      if grep -qE "^${eword}[@~]?$" <<<"${oword}"; then
        result="${result}${eword}${NL}"
        result="${result}${eword}@${NL}"
        result="${result}${eword}~${NL}"
        found=1
        break
      fi
    done <<<"${1}"
    if [ ${found} -eq 0 ]; then
      result="${result}${oword}${NL}"
    fi
  done <<<"${original}"
}
function add_new {
  if [ -z "${1}" ]; then
    return
  fi
  while read -r eword; do
    if ! grep -qE "^${eword}[@~]?" <<<"${original}"; then
      result="${result}${eword}${NL}"
      result="${result}${eword}@${NL}"
      result="${result}${eword}~${NL}"
    fi
  done <<<"${1}"
}
update_existing "${english_upto3}"
update_existing "${english_rest}"
add_new "${english_upto3}"
add_new "${english_rest}"

body_start=$(grep -n -E -m 1 '^[^#$]' regex-assembly/exclude/unix-shell-fps-pl1.ra | cut -d: -f1)
ed -s regex-assembly/exclude/unix-shell-fps-pl1.ra <<EOF
$((body_start - 1)),\$d
w
q
EOF
echo "${result}" | sort | uniq >> regex-assembly/exclude/unix-shell-fps-pl1.ra
