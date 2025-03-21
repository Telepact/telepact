package io.github.telepact.internal.schema;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class GetInternalTelepactJson {
    public static String getInternalTelepactJson() {
        final var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("internal.telepact.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    };
}
