package io.github.msgpact.internal.schema;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class GetInternalMsgPactJson {
    public static String getInternalMsgPactJson() {
        final var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("internal.msgpact.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    };
}
