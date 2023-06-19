package io.github.brenbar.japi;

import java.util.Map;

record Japi(Map<String, Object> original, Map<String, Definition> parsed) {
}