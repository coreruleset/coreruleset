import requests
import urllib.parse
import time
import os
import sys

if len(sys.argv) != 2:
    print("Usage: python3 bot.py <input.txt>")
    sys.exit(1)

lines = open(sys.argv[1]).readlines()
token = os.environ.get("GITHUB_TOKEN", None)
if token is None:
    raise Exception("Please set GITHUB_TOKEN environment variable")

def search(q):
    encoded = q + "(+language:php"
    res = requests.get("https://api.github.com/search/code?q=%s&type=Code&per_page=1" % encoded,
                       headers={
                        "X-GitHub-Api-Version": "2022-11-28",
                        "Accept": "application/vnd.github+json",
                        "Authorization": "Bearer " + token
                        })
    if res.status_code != 200:
        # we retry until it works:
        print("Retrying %s" % q)
        return search(q)
    return res.json().get("total_count", 0)

# open out.txt to write
f = open("out.txt", "a")
for line in lines:
    q = line.strip()
    out = "%s: %d" % (q, search(q))
    print(out)
    # write to f
    f.write(out + "\n")
    f.flush()
    time.sleep(6)