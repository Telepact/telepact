package io.github.brenbar.japi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class Parser {

    public static Japi newJapi(String japiAsJson) {
        var parsedDefinitions = new HashMap<String, Definition>();

        var objectMapper = new ObjectMapper();
        Map<String, List<Object>> japiAsJsonJava;
        try {
            japiAsJsonJava = objectMapper.readValue(japiAsJson, new TypeReference<>() {
            });

            for (var entry : japiAsJsonJava.entrySet()) {
                var definitionKey = entry.getKey();
                if (!parsedDefinitions.containsValue(definitionKey)) {
                    var definition = ParseDefinition.parseDefinition(japiAsJsonJava, parsedDefinitions, definitionKey);
                    parsedDefinitions.put(definitionKey, definition);
                }
            }
        } catch (IOException e) {
            throw new JapiParseError("Document root must be an object");
        }

        return new Japi((Map<String, Object>) (Object) japiAsJsonJava, parsedDefinitions);
    }

}
