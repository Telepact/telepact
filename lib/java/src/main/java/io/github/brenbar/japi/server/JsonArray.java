package io.github.brenbar.japi.server;

public record JsonArray(TypeDeclaration nestedType) implements Type {
    @Override
    public String getName() {
        return "array";
    }
}