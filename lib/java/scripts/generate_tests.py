from dataclasses import dataclass

cases_filepath = "../../test/cases.txt"
test_filepath = "src/test/java/io/github/brenbar/japi/GeneratedTests.java"

cases_file = open(cases_filepath, "r")
test_file = open(test_filepath, "w")


@dataclass
class Case:
    name: str
    argument: str
    result: str
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
        argument = lines[0]
        result = lines[1]
        skip_binary = lines[2] == 'skipBinary' if lines[2:] else False

        case = Case('{}_{}'.format(current_test_name, counter),
                    argument, result, skip_binary)

        cases.append(case)

        counter += 1

test_file.write('''
package io.github.brenbar.japi;

import org.junit.jupiter.api.Test;

import java.io.*;

public class GeneratedTests {

''')

for case in cases:
    print(case)
    test_file.write('''
    @Test
    public void test_{}() throws IOException {{
        var argument = """
        {}
        """.trim();
        var expectedResult = """
        {}
        """.trim();
        TestUtility.test(argument, expectedResult);
    }}
    '''.format(case.name, case.argument, case.result))

    if case.skip_binary:
        continue

    test_file.write('''
    @Test
    public void testBinary_{}() throws IOException {{
        var argument = """
        {}
        """.trim();
        var expectedResult = """
        {}
        """.trim();
        TestUtility.testBinary(argument, expectedResult);
    }}
    '''.format(case.name, case.argument, case.result))


test_file.write('''
}
''')
