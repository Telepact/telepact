package io.github.brenbar.japi.server;

public record JsonObject(TypeDeclaration nestedType) implements Type {
    @Override
    public String getName() {
        return "object";
    }
}