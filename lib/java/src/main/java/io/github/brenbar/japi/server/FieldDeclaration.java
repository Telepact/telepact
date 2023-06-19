package io.github.brenbar.japi.server;

public record FieldDeclaration(
        TypeDeclaration typeDeclaration,
        boolean optional) {
}