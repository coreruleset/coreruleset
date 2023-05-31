#!/bin/sh
git clone --depth 1 https://github.com/php/php-src
cd php-src
# Find PHP functions
grep -o --no-file -R 'ZEND_FUNCTION(.*)' | cut -f2 -d\( | cut -f1 -d\) | sort > input.txt
# Filter english word functions
./filter_dict.py input.txt
export GITHUB_TOKEN=...
# Write the dictionary FUNCTION_NAME: count
./bot.py out_filtered.txt
