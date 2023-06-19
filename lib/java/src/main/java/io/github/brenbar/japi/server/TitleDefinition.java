package io.github.brenbar.japi.server;

public record TitleDefinition(
        String name) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}
