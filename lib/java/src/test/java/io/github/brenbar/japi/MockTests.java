package io.github.brenbar.japi;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

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
                var processor = new MockServer(json);
                processor.processor.setOnError((Throwable e) -> {
                        e.printStackTrace();
                });
                processor.resetRandomSeed(0L);
                var client = new Client((m, s) -> {
                        return CompletableFuture.supplyAsync(() -> s.deserialize(processor.process(s.serialize(m))));
                });

                client.submit(new Request("saveVariables", Map.of("variables", Map.of("a", 10))));

                var result = client.submit(new Request("compute",
                                Map.ofEntries(
                                                Map.entry("x", Map.of("variable", Map.of("value", "a"))),
                                                Map.entry("y", Map.of("constant", Map.of("value", 2))),
                                                Map.entry("op", Map.of("add", Map.of())))));

                // This is the value per the given random seed
                assertEquals(0.730967787376657, result.get("result"));
        }

        @Test
        public void testMocking() throws IOException {
                var json = Files.readString(FileSystems.getDefault().getPath("../../test", "calculator.japi.json"));
                var mock = new MockServer(json);
                mock.processor.setOnError((Throwable e) -> {
                        e.printStackTrace();
                });
                mock.resetRandomSeed(0L);
                var client = new Client((m, s) -> {
                        return CompletableFuture.supplyAsync(() -> s.deserialize(mock.process(s.serialize(m))));
                });

                mock.createStub(new MockStub("fn.compute", Map.ofEntries(
                                Map.entry("x", Map.of("variable",
                                                Map.of("value", "a"))),
                                Map.entry("y", Map.of("constant", Map.of("value", 2))),
                                Map.entry("op", Map.of("add", Map.of()))),
                                Map.of("result", 5)));

                client.submit(new Request("saveVariables", Map.of("variables", Map.of("a", 10))));

                var result = client.submit(new Request("compute",
                                Map.ofEntries(
                                                Map.entry("x", Map.of("variable", Map.of("value", "a"))),
                                                Map.entry("y", Map.of("constant", Map.of("value", 2))),
                                                Map.entry("op", Map.of("add", Map.of())))));

                assertEquals(5, result.get("result"));

                client.submit(new Request("exportVariables", Map.of()));
                client.submit(new Request("exportVariables", Map.of()));
                client.submit(new Request("exportVariables", Map.of()));

                var e1 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(new MockVerification("fn.saveVariables",
                                                Map.of("variables", Map.of("b", 10)))));
                assertEquals("""
                                No matching invocations.
                                Wanted exact match:
                                saveVariables({variables={b=10}})
                                Available:
                                saveVariables({variables={a=10}})
                                """, e1.getMessage());
                var e2 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(new MockVerification("fn.saveVariables",
                                                Map.of("variables", Map.of("a", 0)))));
                assertEquals("""
                                No matching invocations.
                                Wanted exact match:
                                saveVariables({variables={a=0}})
                                Available:
                                saveVariables({variables={a=10}})
                                """, e2.getMessage());

                mock.verify(new MockVerification("fn.saveVariables", Map.of("variables", Map.of("a", 10))));

                var e3 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(new MockVerification("fn.compute",
                                                Map.of("x", Map.of("variable", Map.of("value", "b"))))));
                assertEquals("""
                                No matching invocations.
                                Wanted partial match:
                                compute({x={variable={value=b}}})
                                Available:
                                compute({x={variable={value=a}}, y={constant={value=2}}, op={add={}}})
                                """, e3.getMessage());
                var e4 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(new MockVerification("compute",
                                                Map.of("x", Map.of("variable", Map.of("val", "a"))))));
                assertEquals("""
                                No matching invocations.
                                Wanted partial match:
                                compute({x={variable={val=a}}})
                                Available:
                                compute({x={variable={value=a}}, y={constant={value=2}}, op={add={}}})
                                """, e4.getMessage());

                mock.verify(new MockVerification("fn.compute", Map.of("x", Map.of("variable", Map.of("value", "a")))));

                var e5 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(
                                                new MockVerification("exportVariables", Map.of()).setVerificationTimes(
                                                                new MockVerification.ExactNumberOfTimes(2))));
                assertEquals("""
                                Wanted exactly 2 partial matches, but found 3.
                                Query:
                                exportVariables({})
                                """, e5.getMessage());

                mock.verify(new MockVerification("fn.exportVariables", Map.of())
                                .setVerificationTimes(new MockVerification.ExactNumberOfTimes(3)));

                mock.verifyNoMoreInteractions();
        }
}
