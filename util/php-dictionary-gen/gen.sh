#!/bin/sh
git clone https://github.com/php/php-src
cd php-src
# Find PHP functions
grep -o --no-file -R 'ZEND_FUNCTION(.*)' | cut -f2 -d\( | cut -f1 -d\) | sort > input.txt
# Filter english word functions
python filter_dict.py input.txt
export GITHUB_TOKEN=...
# Write the dictionary FUNCTION_NAME: count
python bot.py out_filtered.txt
