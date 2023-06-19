package io.github.brenbar.japi.server;

record TitleDefinition(
        String name) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}
