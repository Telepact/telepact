package io.github.brenbar.uapi.internal;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class GetMockUApiJson {
    public static String getMockUApiJson() {
        final var stream = Thread.currentThread().getContextClassLoader()
                .getResourceAsStream("mock-internal.uapi.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    };
}
