import os
import sys

if len(sys.argv) != 2:
    print("Usage: python3 filter_dict.py <input.txt>")
    sys.exit(1)

f = open(sys.argv[1], "r")
lines = f.readlines()
f.close()

def get_dict(word):
    # run `dict word` and return True if it worked
    # we ignore stderr
    res = os.system("dict %s > /dev/null 2>&1" % word)
    return res == 0

with open("out_filtered.txt", "a") as f:
    for l in lines:
        w = l.split(":")[0]
        word = w.strip()
        if not get_dict(word):
            print(l)
            f.write(l)
            f.flush()
