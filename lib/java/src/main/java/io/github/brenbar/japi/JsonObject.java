package io.github.brenbar.japi;

record JsonObject(TypeDeclaration nestedType) implements Type {
    @Override
    public String getName() {
        return "object";
    }
}