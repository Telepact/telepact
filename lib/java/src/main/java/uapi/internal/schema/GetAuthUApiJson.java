package uapi.internal.schema;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class GetAuthUApiJson {

    public static String getAuthUApiJson() {
        final var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("auth.uapi.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    }

}
