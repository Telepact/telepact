package io.github.brenbar.japi;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

import org.junit.jupiter.api.Test;

public class MockTests {

    @Test
    public void testGeneratedValues() throws IOException {
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "calculator.japi.json"));
        var processor = new MockProcessor(json);
        processor.processor.setOnError((e) -> {
            e.printStackTrace();
        });
        processor.resetRandomSeed(0L);
        var client = new Client((m, s) -> {
            return CompletableFuture.supplyAsync(() -> {
                try {
                    return s.deserialize(processor.process(s.serialize(m)));
                } catch (DeserializationError e) {
                    throw new RuntimeException(e);
                }
            });
        });

        client.submit(new Request("saveVariable", Map.of("name", "a", "value", 10)));

        var result = client.submit(new Request("compute",
                Map.ofEntries(
                        Map.entry("x", Map.of("variable", Map.of("value", "a"))),
                        Map.entry("y", Map.of("constant", Map.of("value", 2))))));

        // This is the value per the given random seed
        assertEquals(0.730967787376657, result.get("result"));
    }
}
