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

cases = []

current_test_name = None
counter = 0

for l in cases_file:
    line = l.rstrip()

    if line.startswith('"'):
        current_test_name = line[1:-1]
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

test_file.write('''
package io.github.brenbar.japi;

import org.junit.jupiter.api.Test;

import java.io.*;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class Tests {

    Map<String, Object> handle(String functionName, Map<String, Object> headers, Map<String, Object> body) {
        return switch (functionName) {
            case "test" -> {
                if (headers.containsKey("output")) {
                    try {
                        var o = (Map<String, Object>) headers.get("output");
                        yield o;
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                } else {
                    yield Map.of();
                }
            }
            default -> throw new RuntimeException();
        };
    }

''')

for case in cases:
    print(case)
    test_file.write('''
    @Test
    public void test_{}() throws IOException {{
        var objectMapper = new ObjectMapper();
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "japi.json"));
        var defs = Parser.newJapiDescription(json);
        var processor = new Processor(this::handle, defs, (e) -> {{e.printStackTrace();}});
        var input = """
        {}
        """.trim();
        var expectedOutput = """
        {}
        """.trim();
        var output = processor.process(input);
        var expectedOutputJsonJava = objectMapper.readValue(expectedOutput, new TypeReference<List<Object>>(){{}});
        var outputJsonJava = objectMapper.readValue(output, new TypeReference<List<Object>>(){{}});
        assertEquals(expectedOutputJsonJava, outputJsonJava);
    }}

    '''.format(case.name, case.input, case.output)
    )

test_file.write('''
}
''')