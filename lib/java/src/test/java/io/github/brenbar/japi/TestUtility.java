package io.github.brenbar.japi;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Client.Adapter;

public class TestUtility {

    private static Map<String, Object> handle(Context context, Map<String, Object> body) {
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

    public static void test(String input, String expectedOutput, boolean skipBinary) throws IOException {
        var objectMapper = new ObjectMapper();
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var processor = new Processor(json, TestUtility::handle).setOnError((e) -> e.printStackTrace())
                .setExtractContextProperties((h) -> h);
        var expectedOutputAsParsedJson = objectMapper.readValue(expectedOutput, new TypeReference<List<Object>>() {
        });

        // test json
        {
            var inputBytes = input.getBytes(StandardCharsets.UTF_8);
            System.out.println("--> %s".formatted(new String(inputBytes)));
            var outputBytes = processor.process(inputBytes);
            System.out.println("<-- %s".formatted(new String(outputBytes)));
            var outputAsParsedJson = objectMapper.readValue(outputBytes, new TypeReference<List<Object>>() {
            });
            assertEquals(expectedOutputAsParsedJson, outputAsParsedJson);
        }

        if (skipBinary) {
            return;
        }

        // test binary
        {
            Adapter adapter = (m, s) -> {
                return CompletableFuture.supplyAsync(() -> {
                    var inputBytes = s.serialize(m);
                    System.out.println("--> %s".formatted(new String(inputBytes)));
                    var outputBytes = processor.process(inputBytes);
                    System.out.println("<-- %s".formatted(new String(outputBytes)));
                    List<Object> output;
                    try {
                        output = s.deserialize(outputBytes);
                    } catch (DeserializationError e1) {
                        throw new RuntimeException(e1);
                    }
                    return output;
                });
            };
            var client = new Client(adapter).setForceSendJsonDefault(false).setUseBinaryDefault(true);
            client.submit(new Request("_ping", Map.of())); // warmup
            var inputAsParsedJson = objectMapper.readValue(input, new TypeReference<List<Object>>() {
            });

            if (expectedOutput.startsWith("[\"error.")) {
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

}
