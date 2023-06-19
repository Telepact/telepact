package io.github.brenbar.japi.server;

import java.util.Map;

public record Struct(String name, Map<String, FieldDeclaration> fields) implements Type {
    @Override
    public String getName() {
        return name;
    }
}