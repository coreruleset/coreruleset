#! /usr/bin/env python3

import sys
from spylls.hunspell import Dictionary

if len(sys.argv) != 2:
    print("Usage: python3 filter_dict.py <input.txt>")
    sys.exit(1)

f = open(sys.argv[1], "r")
lines = f.readlines()
f.close()

def get_dict(word):
    # en_US dictionary is distributed with spylls
    # See docs to load other dictionaries
    dictionary = Dictionary.from_files('en_US')

    return dictionary.lookup(word)

with open("out_filtered.txt", "a") as f:
    for l in lines:
        w = l.split(":")[0]
        word = w.strip()
        if not get_dict(word):
            print(l)
            f.write(l)
            f.flush()
