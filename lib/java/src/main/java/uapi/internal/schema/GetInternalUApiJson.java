package uapi.internal.schema;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class GetInternalUApiJson {
    public static String getInternalUApiJson() {
        final var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("internal.uapi.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    };
}
