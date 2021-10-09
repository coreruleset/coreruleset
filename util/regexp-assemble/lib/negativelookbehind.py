#!/usr/bin/env python

import sys
import fileinput

#
# This script generates regular expressions that behave like negative lookbehinds without using negative lookbehinds.
# For example an alternative to "(?<!a[bB]c|1234)" would be "(?:(?:^|[^c4])|(?:^|[^bB])c|(?:^|[^3])4|(?:^|[^a])[bB]c|(?:^|[^2])34|(?:^|[^1])234)".
# More explanation here: http://allanrbo.blogspot.com/2020/01/alternative-to-negative-lookbehinds-in.html
#
# Input (stdin or arg): a file where each line corresponds to an alternative-group in a negative lookbehind.
#   Example to generate a regex equivalent to "(?<!a[bB]c|1234)":
#     a[bB]c
#     1234
# Output: A regular expression corresponding to the negative lookbehind.
#


# Process lines from input file, or if not specified, standard input
negativePrefixes = []
for line in fileinput.input():
    line = line.rstrip()
    if line != "":
      negativePrefixes.append(line)

def removeDuplicateChars(s):
  return "".join([c for i,c in enumerate(s) if c not in s[:i]])

def removeChars(s, charsToRemove):
  return "".join([c for i,c in enumerate(s) if c not in charsToRemove])

# Split into arrays of strings. Each string is either a single char, or a char class.
negativePrefixesSplit = []
for np in negativePrefixes:
  npSplit = []
  curCc = ""
  inCc = False
  for c in np:
    if c == "[":
      inCc = True
    elif c == "]":
      npSplit.append(removeDuplicateChars(curCc))
      curCc = ""
      inCc = False
    else:
      if inCc:  
        if c in "-\\":
          raise "Only really simply char classes are currently supported. No ranges or escapes, sorry."
        curCc += c
      else:
        npSplit.append(c)
  negativePrefixesSplit.append(npSplit)

allexprs = []

class Expr():
  pass

suffixLength = 0
while True:
  suffixes = []
  for np in negativePrefixesSplit:
    if suffixLength < len(np):
      suffixes.append(np[len(np)-suffixLength-1:])

  if len(suffixes) == 0:
    break

  exprs = []
  for suffix in suffixes:
    curChar = suffix[0]
    remainder = suffix[1:]
    expr = Expr()
    expr.curChar = curChar
    expr.remainder = remainder
    exprs.append(expr)

  # Is the remainder a subset of any other suffixes remainders?
  for i in range(len(exprs)):
    e1 = exprs[i]
    for j in range(len(exprs)):
      e2 = exprs[j]
      isSubset = True
      for k in range(len(e1.remainder)):
        if not set(e1.remainder[k]).issubset(set(e2.remainder[k])):
          isSubset = False
          break
      if isSubset:
        if e1.curChar == e2.curChar:
          e1.remainder = e2.remainder
          continue

        e1.curChar += e2.curChar
        e1.curChar = removeDuplicateChars(e1.curChar)
        for k in range(len(e1.remainder)):
          if len(set(e2.remainder[k]) - set(e1.remainder[k])) > 0:
            charsInCommon = "".join(set(e2.remainder[k]) & set(e1.remainder[k]))
            e2.remainder[k] = removeChars(e2.remainder[k], charsInCommon)

  # Remove duplicate expressions
  exprsFiltered = []
  for i in range(len(exprs)):
    e1 = exprs[i]
    alreadyExists = False
    for j in range(len(exprs)):
      if i == j:
        break

      e2 = exprs[j]

      sameC = set(e1.curChar) == set(e2.curChar)
      sameR = True
      for k in range(len(e1.remainder)):
        if set(e1.remainder[k]) != set(e2.remainder[k]):
          sameR = False
          break
      if sameC and sameR:
        alreadyExists = True
        break

    if not alreadyExists:
      exprsFiltered.append(e1)

  allexprs.extend(exprsFiltered)

  suffixLength += 1
  continue

out = "(?:\n"
for i in range(len(allexprs)):
  e = allexprs[i]
  out += ("(?:^|[^" + e.curChar + "])")
  for c in e.remainder:
    if len(c) > 1:
      out += "[" + c + "]"
    else:
      out += c
  if i != len(allexprs)-1:
    out += "|"
  out += "\n"
out += ")"

if len(sys.argv) > 1 and sys.argv[1] == '-h':
  print("Human readable:")
  print(out)
  print()
else:
  print(out.replace("\n",""))
