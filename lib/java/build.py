import shutil
import subprocess
import os
from dataclasses import dataclass


def generate_tests():

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


def generate_binary_exact_tests():

    cases_filepath = "../../test/binary/invalidBinaryCases.txt"
    test_filepath = "src/test/java/io/github/brenbar/japi/GeneratedBinaryExactTests.java"

    cases_file = open(cases_filepath, "r")
    test_file = open(test_filepath, "w")

    @dataclass
    class Case:
        name: str
        argument: str
        result: str

    cases = []

    current_test_name = 'binary'
    counter = 0

    for l in cases_file:
        line = l.rstrip()

        if line == '':
            continue
        elif line.__contains__('|'):
            lines = line.split('|')
            argument = bytes(lines[0], 'utf-8').decode('unicode_escape')
            result = lines[1]

            argument_as_bytes = ", ".join(
                ['(byte) {}'.format(hex(ord(x))) for x in argument])

            result_as_bytes = ", ".join(
                ['(byte) {}'.format(hex(ord(x))) for x in result])

            case = Case('{}_{}'.format(current_test_name, counter),
                        argument_as_bytes, result_as_bytes)

            cases.append(case)

            counter += 1

    test_file.write('''
    package io.github.brenbar.japi;

    import org.junit.jupiter.api.Test;

    import java.io.*;

    public class GeneratedBinaryExactTests {

    ''')

    for case in cases:
        print(case)

        test_file.write('''
        @Test
        public void testBinary_{}() throws IOException {{
            var argument = new byte[] {{
            {}
            }};
            var expectedResult = new byte[] {{
            {}
            }};
            TestUtility.testBinaryExact(argument, expectedResult);
        }}
        '''.format(case.name, case.argument, case.result))

    test_file.write('''
    }
    ''')


def generate_mock_invalid_tests():

    cases_filepath = "../../test/mockInvalidStubCases.txt"
    test_filepath = "src/test/java/io/github/brenbar/japi/GeneratedMockInvalidStubTests.java"

    cases_file = open(cases_filepath, "r")
    test_file = open(test_filepath, "w")

    @dataclass
    class Case:
        name: str
        argument: str
        result: str

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

            case = Case('{}_{}'.format(current_test_name, counter),
                        argument, result)

            cases.append(case)

            counter += 1

    test_file.write('''
    package io.github.brenbar.japi;

    import org.junit.jupiter.api.Test;

    import java.io.*;

    public class GeneratedMockInvalidStubTests {

    ''')

    for case in cases:
        print(case)
        test_file.write('''
        @Test
        public void test_{}() throws IOException {{
            var server = TestUtility.generatedMockTestSetup();
            var argument = """
            {}
            """.trim();
            var expectedResult = """
            {}
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);;
        }}
        '''.format(case.name, case.argument, case.result))

    test_file.write('''
    }
    ''')


def generate_mock_tests():
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

    for name, cases in cases_by_name.items():
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


if not os.path.exists('src/main/resources'):
    os.makedirs('src/main/resources')
shutil.copyfile('../../common/internal.japi.json',
                'src/main/resources/internal.japi.json')
shutil.copyfile('../../common/mock-internal.japi.json',
                'src/main/resources/mock-internal.japi.json')

generate_tests()
generate_binary_exact_tests()
generate_mock_tests()
generate_mock_invalid_tests()
subprocess.run(['mvn', 'verify', '-DskipTests'])
