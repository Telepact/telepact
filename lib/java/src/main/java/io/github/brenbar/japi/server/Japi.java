package io.github.brenbar.japi.server;

import java.util.Map;

record Japi(Map<String, Object> original, Map<String, Definition> parsed) {
}