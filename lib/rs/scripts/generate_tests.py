from dataclasses import dataclasses;

cases_filepath = "../../test/cases.txt"
test_filepath = "tests/cases.rs"

cases_file = open(cases_filepath, "r")
test_file = open(test_filepath, "w")

@dataclasses
class Case:
    name: str
    input: str
    output: str

cases = []

current_test_name = None
counter = 0

for l in cases_file:
    line = l.rstrip()

    if line.startswith('"'):
        current_test_name = line
        counter = 1
    elif line == '':
        continue
    elif line.startswith('['):
        lines = line.split('|')
        input = lines[0]
        output = lines[1]

        case = Case('{}_{}'.format(current_test_name, counter), input, output)

        cases.append(case)

        counter += 1

test_file.write('')

for case in cases:

    
