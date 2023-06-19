package io.github.brenbar.japi.server;

record JsonArray(TypeDeclaration nestedType) implements Type {
    @Override
    public String getName() {
        return "array";
    }
}