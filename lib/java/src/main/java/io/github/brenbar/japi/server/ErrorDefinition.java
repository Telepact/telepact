package io.github.brenbar.japi.server;

import java.util.Map;

record ErrorDefinition(
        String name,
        Map<String, FieldDeclaration> fields) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}