package io.github.brenbar.japi.server;

import java.util.Map;

public interface Handler {

    Map<String, Object> handle(String functionName, Map<String, Object> headers, Map<String, Object> input);
}
