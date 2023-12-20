import shutil
import subprocess
import os
import itertools
import json

cases_filepath = "test/mockCases.txt"

cases_file = open(cases_filepath, "r")

cases = []

current_test_name = None
counter = 0

for l in cases_file:
    line = l.rstrip()

    if line == '':
        continue
    if not line.__contains__('|'):
        current_test_name = line[1:-1]
        counter = 1
    elif line.__contains__('|'):
        lines = line.split('|')
        try:
            argument = json.loads(lines[0])
            result = json.loads(lines[1])
        except:
            continue

        skip_binary = lines[2] == 'skipBinary' if lines[2:] else False

        if skip_binary:
            cases.append([current_test_name, argument, result, skip_binary])
        else:
            cases.append([current_test_name, argument, result])

        counter += 1


def keyfunc(e):
    return e[0]


sorted = {k: list(map(lambda e: e[1:], list(v)))
          for k, v in itertools.groupby(cases, key=keyfunc)}

# print(sorted)
print('cases = {')
for k, v in sorted.items():
    print("    '{}': [".format(k))
    for e in v:
        print('        {},'.format(e))
    print("    ],".format(k))

print('}')
