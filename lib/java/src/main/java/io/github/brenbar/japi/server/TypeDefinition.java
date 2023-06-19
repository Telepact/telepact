package io.github.brenbar.japi.server;

public record TypeDefinition(
        String name,
        Type type) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}