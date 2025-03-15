package io.github.msgpact;

import static io.github.msgpact.internal.schema.CreateMockMsgPactSchemaFromJsonDocuments.createMockMsgPactSchemaFromFileJsonMap;
import static io.github.msgpact.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.List;
import java.util.Map;

import io.github.msgpact.internal.types.VFieldDeclaration;
import io.github.msgpact.internal.types.VType;

/**
 * A parsed msgPact schema.
 */
public class MockMsgPactSchema {

    public final List<Object> original;
    public final Map<String, VType> parsed;
    public final Map<String, VFieldDeclaration> parsedRequestHeaders;
    public final Map<String, VFieldDeclaration> parsedResponseHeaders;

    public MockMsgPactSchema(List<Object> original,
            Map<String, VType> parsed,
            Map<String, VFieldDeclaration> parsedRequestHeaders,
            Map<String, VFieldDeclaration> parsedResponseHeaders) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    public static MockMsgPactSchema fromJson(String json) {
        return createMockMsgPactSchemaFromFileJsonMap(Map.of("auto_", json));
    }

    public static MockMsgPactSchema fromFileJsonMap(Map<String, String> fileJsonMap) {
        return createMockMsgPactSchemaFromFileJsonMap(fileJsonMap);
    }

    public static MockMsgPactSchema fromDirectory(String directory) {
        final var map = getSchemaFileMap(directory);
        return createMockMsgPactSchemaFromFileJsonMap(map);
    }
}
