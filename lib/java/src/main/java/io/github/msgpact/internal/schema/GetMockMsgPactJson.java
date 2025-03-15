package io.github.msgpact.internal.schema;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class GetMockMsgPactJson {
    public static String getMockMsgPactJson() {
        final var stream = Thread.currentThread().getContextClassLoader()
                .getResourceAsStream("mock-internal.msgpact.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    };
}
