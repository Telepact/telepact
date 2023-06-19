package io.github.brenbar.japi.server;

record JsonObject(TypeDeclaration nestedType) implements Type {
    @Override
    public String getName() {
        return "object";
    }
}