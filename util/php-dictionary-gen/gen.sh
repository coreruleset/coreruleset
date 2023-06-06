#!/bin/sh

# check if GITHUB_TOKEN exists in env
if [ -z "$GITHUB_TOKEN" ]; then
    echo "This script needs the variable GITHUB_TOKEN exported with your token."
    exit 1
fi

git clone --depth 1 https://github.com/php/php-src
cd php-src
# Find PHP functions
grep -o --no-file -R 'ZEND_FUNCTION(.*)' | cut -f2 -d\( | cut -f1 -d\) | sort > input.txt
# Filter english word functions
./filter_dict.py input.txt
# Write the dictionary FUNCTION_NAME: count
./bot.py out_filtered.txt
