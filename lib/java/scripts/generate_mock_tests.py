from dataclasses import dataclass

cases_filepath = "../../test/mockCases.txt"
test_filepath = "src/test/java/io/github/brenbar/japi/GeneratedMockTests.java"

cases_file = open(cases_filepath, "r")
test_file = open(test_filepath, "w")


@dataclass
class Case:
    name: str
    argument: str
    result: str


cases_by_name = {}

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

        case = Case('{}_{}'.format(current_test_name, counter),
                    argument, result)

        cases = cases_by_name.setdefault(current_test_name, [])
        cases.append(case)

        counter += 1

test_file.write('''
package io.github.brenbar.japi;

import org.junit.jupiter.api.Test;

import java.io.*;

public class GeneratedMockTests {

''')

for name,cases in cases_by_name.items():
    print(name)
    print(cases)
    test_file.write('''
    @Test
    public void test_{}() throws IOException {{
        var server = TestUtility.generatedMockTestSetup();
    '''.format(name))

    for case in cases:
        test_file.write('''
        {{
            var argument = """
            {}
            """.trim();
            var expectedResult = """
            {}
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }}
        '''.format(case.argument, case.result))

    test_file.write('''
    }
    ''')

test_file.write('''
}
''')
