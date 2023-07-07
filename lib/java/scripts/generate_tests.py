from dataclasses import dataclass;

cases_filepath = "../../test/cases.txt"
test_filepath = "src/test/java/io/github/brenbar/japi/Tests.java"

cases_file = open(cases_filepath, "r")
test_file = open(test_filepath, "w")

@dataclass
class Case:
    name: str
    input: str
    output: str
    skip_binary: bool

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
        input = lines[0]
        output = lines[1]
        skip_binary = lines[2] == 'skipBinary' if lines[2:] else False

        case = Case('{}_{}'.format(current_test_name, counter), input, output, skip_binary)

        cases.append(case)

        counter += 1

test_file.write('''
package io.github.brenbar.japi;

import org.junit.jupiter.api.Test;

import java.io.*;

import static io.github.brenbar.japi.TestUtility.test;

public class Tests {

''')

for case in cases:
    print(case)
    test_file.write('''
    @Test
    public void test_{}() throws IOException {{
        var input = """
        {}
        """.trim();
        var expectedOutput = """
        {}
        """.trim();
        test(input, expectedOutput, {});
    }}
    '''.format(case.name, case.input, case.output, 'true' if case.skip_binary else 'false'))

test_file.write('''
}
''')