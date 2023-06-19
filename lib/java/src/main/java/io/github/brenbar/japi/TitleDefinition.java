package io.github.brenbar.japi;

record TitleDefinition(
        String name) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}
