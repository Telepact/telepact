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
                processor.server.setOnError((Throwable e) -> {
                        e.printStackTrace();
                });
                processor.resetRandomSeed(0L);
                var client = new Client((m, s) -> {
                        return CompletableFuture.supplyAsync(() -> s.deserialize(processor.process(s.serialize(m))));
                })
                                .setTimeoutMsDefault(600000);

                client.submit(new Request("fn.saveVariables", Map.of("variables", Map.of("a", 10))));

                var result = client.submit(new Request("fn.compute",
                                Map.ofEntries(
                                                Map.entry("x", Map.of("variable", Map.of("name", "a"))),
                                                Map.entry("y", Map.of("constant", Map.of("value", 2))),
                                                Map.entry("op", Map.of("add", Map.of())))));

                // This is the value per the given random seed
                assertEquals(Map.of("ok", Map.of("result", 0.24053641567148587)), result);
        }

        @Test
        public void testMocking() throws IOException {
                var json = Files.readString(FileSystems.getDefault().getPath("../../test", "calculator.japi.json"));
                var mock = new MockServer(json);
                mock.server.setOnError((Throwable e) -> {
                        e.printStackTrace();
                });
                mock.resetRandomSeed(0L);
                var client = new Client((m, s) -> {
                        return CompletableFuture.supplyAsync(() -> s.deserialize(mock.process(s.serialize(m))));
                })
                                .setTimeoutMsDefault(600000);

                mock.createStub(new MockStub("fn.compute", Map.ofEntries(
                                Map.entry("x", Map.of("variable",
                                                Map.of("name", "a"))),
                                Map.entry("y", Map.of("constant", Map.of("value", 2))),
                                Map.entry("op", Map.of("add", Map.of()))),
                                Map.of("ok", Map.of("result", 5))));

                client.submit(new Request("fn.saveVariables", Map.of("variables", Map.of("a", 10))));

                var result = client.submit(new Request("fn.compute",
                                Map.ofEntries(
                                                Map.entry("x", Map.of("variable", Map.of("name", "a"))),
                                                Map.entry("y", Map.of("constant", Map.of("value", 2))),
                                                Map.entry("op", Map.of("add", Map.of())))));

                assertEquals(Map.of("ok", Map.of("result", 5)), result);

                client.submit(new Request("fn.exportVariables", Map.of()));
                client.submit(new Request("fn.exportVariables", Map.of()));
                client.submit(new Request("fn.exportVariables", Map.of()));

                var e1 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(new MockVerification("fn.saveVariables",
                                                Map.of("variables", Map.of("b", 10)))));
                assertEquals("""
                                No matching invocations.
                                Wanted exact match:
                                fn.saveVariables({variables={b=10}})
                                Available:
                                fn.saveVariables({variables={a=10}})
                                """, e1.getMessage());
                var e2 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(new MockVerification("fn.saveVariables",
                                                Map.of("variables", Map.of("a", 0)))));
                assertEquals("""
                                No matching invocations.
                                Wanted exact match:
                                fn.saveVariables({variables={a=0}})
                                Available:
                                fn.saveVariables({variables={a=10}})
                                """, e2.getMessage());

                mock.verify(new MockVerification("fn.saveVariables", Map.of("variables", Map.of("a", 10))));

                var e3 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(new MockVerification("fn.compute",
                                                Map.of("x", Map.of("variable", Map.of("name", "b"))))
                                                .setAllowArgumentPartialMatch(true)));
                assertEquals("""
                                No matching invocations.
                                Wanted partial match:
                                fn.compute({x={variable={name=b}}})
                                Available:
                                fn.compute({op={add={}}, x={variable={name=a}}, y={constant={value=2}}})
                                """, e3.getMessage());
                var e4 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(new MockVerification("fn.compute",
                                                Map.of("x", Map.of("variable", Map.of("namo", "a"))))
                                                .setAllowArgumentPartialMatch(true)));
                assertEquals("""
                                No matching invocations.
                                Wanted partial match:
                                fn.compute({x={variable={namo=a}}})
                                Available:
                                fn.compute({op={add={}}, x={variable={name=a}}, y={constant={value=2}}})
                                """, e4.getMessage());

                mock.verify(new MockVerification("fn.compute", Map.of("x", Map.of("variable", Map.of("name", "a"))))
                                .setAllowArgumentPartialMatch(true));

                var e5 = assertThrows(
                                AssertionError.class,
                                () -> mock.verify(
                                                new MockVerification("fn.exportVariables", Map.of())
                                                                .setVerificationTimes(
                                                                                new MockVerification.ExactNumberOfTimes(
                                                                                                2))
                                                                .setAllowArgumentPartialMatch(true)));
                assertEquals("""
                                Wanted exactly 2 partial matches, but found 3.
                                Query:
                                fn.exportVariables({})
                                """, e5.getMessage());

                mock.verify(new MockVerification("fn.exportVariables", Map.of())
                                .setVerificationTimes(new MockVerification.ExactNumberOfTimes(3)));

                mock.verifyNoMoreInteractions();
        }
}
