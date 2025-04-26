#!/bin/bash
set -euo pipefail

restricted_file_path="../../rules/restricted-files.data"
restricted_upload_path="../../rules/restricted-upload.data"

# Check if crs-toolchain command exists
if ! command -v crs-toolchain &> /dev/null; then
  echo "Error: crs-toolchain is not available or not executable."
  exit 1
fi

# Find the first non-comment line number
body_start=$(grep -n -E -m 1 '^[^#]' "$restricted_upload_path" | cut -d: -f1)

# If there is any non-comment line, remove everything from it to the end
ed -s "$restricted_upload_path" <<EOF
$((body_start)),\$d
w
q
EOF

tmpfile="$(mktemp)"

# Extract the last segment after the last slash '/' of non-comment lines
# Keep only words longer than 3 characters
awk ' !/^#/ && NF {
 n = split($0, segments, "/");
 word = segments[n];
 if (length(word) > 3) print word
}' "$restricted_file_path" | sort | uniq > "$tmpfile"

# Run the fp-finder tool to filter words not in the English dictionary
crs-toolchain util fp-finder "$tmpfile" -e english-extended.txt >> "$restricted_upload_path"

# Clean up temporary file
rm -f "$tmpfile"
