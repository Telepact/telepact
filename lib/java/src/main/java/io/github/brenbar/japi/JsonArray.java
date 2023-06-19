package io.github.brenbar.japi;

record JsonArray(TypeDeclaration nestedType) implements Type {
    @Override
    public String getName() {
        return "array";
    }
}