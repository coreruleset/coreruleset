#! /usr/bin/env python3

import sys
from spylls.hunspell import Dictionary

if len(sys.argv) != 2:
    print("Usage: python3 filter_dict.py <input.txt>")
    sys.exit(1)

f = open(sys.argv[1], "r")
lines = f.readlines()
f.close()

# en_US dictionary is distributed with spylls
# See docs to load other dictionaries
dictionary = Dictionary.from_files('en_US')

with open("out_filtered.txt", "a") as f:
    for l in lines:
        w = l.split(":")[0]
        word = w.strip()
        if dictionary.lookup(word):
            print(f"{word} found in dictionary, skipping.")
        else:
            print(f"adding {word}")
            f.write(l)
            f.flush()
