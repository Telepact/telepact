package io.github.msgpact.internal.schema;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class GetAuthMsgPactJson {

    public static String getAuthMsgPactJson() {
        final var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("auth.msgpact.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    }

}
