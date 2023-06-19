package io.github.brenbar.japi.server;

import java.util.Map;

public record Japi(Map<String, Object> original, Map<String, Definition> parsed) {
}