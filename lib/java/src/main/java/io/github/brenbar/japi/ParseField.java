package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class ParseField {
    static FieldNameAndFieldDeclaration parseField(
            Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions,
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isForUnion) {
        var regex = Pattern.compile("^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$");
        var matcher = regex.matcher(fieldDeclaration);
        matcher.find();

        String fieldName = matcher.group(1);

        boolean optional = matcher.group(2) != null;

        if (optional && isForUnion) {
            throw new JapiParseError("Union keys cannot be marked as optional");
        }

        String typeDeclarationString;
        try {
            typeDeclarationString = (String) typeDeclarationValue;
        } catch (ClassCastException e) {
            throw new JapiParseError("Type declarations should be strings");
        }

        var typeDeclaration = ParseType.parseType(japiAsJsonJava, parsedDefinitions, typeDeclarationString);

        return new FieldNameAndFieldDeclaration(fieldName, new FieldDeclaration(typeDeclaration, optional));
    }
}
