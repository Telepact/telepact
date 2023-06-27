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
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class Tests {

    Map<String, Object> handle(Context context, Map<String, Object> body) {
        return switch (context.functionName) {
            case "test" -> {
                var error = context.properties.keySet().stream().filter(k -> k.startsWith("error.")).findFirst();
                if (context.properties.containsKey("output")) {
                    try {
                        var o = (Map<String, Object>) context.properties.get("output");
                        yield o;
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                } else if (error.isPresent()) {
                    try {
                        var e = (Map<String, Object>) context.properties.get(error.get());
                        throw new JApiError(error.get(), e);
                    } catch (ClassCastException e) {
                        throw new RuntimeException(e);
                    }
                } else {
                    yield Map.of();
                }
            }
            default -> throw new RuntimeException();
        };
    }

    private void test(String input, String expectedOutput) throws IOException {
        var objectMapper = new ObjectMapper();
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var processor = new Processor(json, this::handle).setOnError((e) -> e.printStackTrace())
                .setExtractContextProperties((h) -> h);
        var expectedOutputAsParsedJson = objectMapper.readValue(expectedOutput, new TypeReference<List<Object>>() {
        });

        // test json
        {
            var output = processor.process(input.getBytes(StandardCharsets.UTF_8));
            var outputAsParsedJson = objectMapper.readValue(output, new TypeReference<List<Object>>() {
            });
            assertEquals(expectedOutputAsParsedJson, outputAsParsedJson);
        }

        // test binary
        {
            var client = new SyncClient(
                    (m) -> {
                        System.out.println(new String(m));
                        var result = processor.process(m);
                        System.out.println(new String(result));
                        return CompletableFuture.completedFuture(result);
                    }).setForceSendJson(false).setUseBinary(true);
            client.submit(new Request("_ping", Map.of())); // warmup
            var inputAsParsedJson = objectMapper.readValue(input, new TypeReference<List<Object>>() {
            });

            if (expectedOutput.startsWith("[\\"error.")) {
                var e = assertThrows(JApiError.class,
                        () -> client.submit(new Request(((String) inputAsParsedJson.get(0)).substring(9),
                                (Map<String, Object>) inputAsParsedJson.get(2)).addHeaders(
                                        (Map<String, Object>) inputAsParsedJson.get(1))));
                assertEquals(expectedOutputAsParsedJson.get(0), e.target);
                assertEquals(expectedOutputAsParsedJson.get(2), e.body);
            } else {
                var outputAsParsedJson = client.submit(new Request(((String) inputAsParsedJson.get(0)).substring(9),
                        (Map<String, Object>) inputAsParsedJson.get(2)).addHeaders(
                                (Map<String, Object>) inputAsParsedJson.get(1)));
                assertEquals(expectedOutputAsParsedJson.get(2), outputAsParsedJson);
            }
        }
    }

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
        test(input, expectedOutput);
    }}
    '''.format(case.name, case.input, case.output))

test_file.write('''
}
''')