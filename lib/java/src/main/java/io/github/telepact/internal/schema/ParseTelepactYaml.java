//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;

import org.yaml.snakeyaml.LoaderOptions;
import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.constructor.SafeConstructor;

import io.github.telepact.internal.schema.DocumentLocators.DocumentLocator;

public class ParseTelepactYaml {
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    public static final class ParsedTelepactYaml {
        public final String canonicalJson;
        public final DocumentLocator locator;

        public ParsedTelepactYaml(String canonicalJson, DocumentLocator locator) {
            this.canonicalJson = canonicalJson;
            this.locator = locator;
        }
    }

    public static ParsedTelepactYaml parseTelepactYaml(String text) throws Exception {
        final var loaderOptions = new LoaderOptions();
        final var yaml = new Yaml(new SafeConstructor(loaderOptions));
        final var parsed = yaml.load(text);
        final var normalized = normalizeJsonCompatibleValue(parsed);
        if (!(normalized instanceof List<?> rootList)) {
            throw new IllegalArgumentException("Telepact YAML root must be a sequence");
        }

        return new ParsedTelepactYaml(
                OBJECT_MAPPER.writeValueAsString(rootList),
                BuildDocumentLocatorFromYamlAst.createDocumentLocatorFromYamlText(text));
    }

    private static Object normalizeJsonCompatibleValue(Object value) {
        if (value == null || value instanceof String || value instanceof Boolean
                || value instanceof Integer || value instanceof Long || value instanceof Short || value instanceof Byte) {
            return value;
        }

        if (value instanceof BigInteger bigInteger) {
            return bigInteger;
        }

        if (value instanceof Float floatValue) {
            if (!Float.isFinite(floatValue)) {
                throw new IllegalArgumentException("YAML values must be JSON-compatible");
            }
            return floatValue.doubleValue();
        }

        if (value instanceof Double doubleValue) {
            if (!Double.isFinite(doubleValue)) {
                throw new IllegalArgumentException("YAML values must be JSON-compatible");
            }
            return doubleValue;
        }

        if (value instanceof BigDecimal bigDecimal) {
            if (!Double.isFinite(bigDecimal.doubleValue())) {
                throw new IllegalArgumentException("YAML values must be JSON-compatible");
            }
            return bigDecimal;
        }

        if (value instanceof List<?> listValue) {
            final var normalized = new ArrayList<>();
            for (final var child : listValue) {
                normalized.add(normalizeJsonCompatibleValue(child));
            }
            return normalized;
        }

        if (value instanceof Map<?, ?> mapValue) {
            final var normalized = new LinkedHashMap<String, Object>();
            for (final var entry : mapValue.entrySet()) {
                if (!(entry.getKey() instanceof String stringKey)) {
                    throw new IllegalArgumentException("YAML values must be JSON-compatible");
                }
                normalized.put(stringKey, normalizeJsonCompatibleValue(entry.getValue()));
            }
            return normalized;
        }

        throw new IllegalArgumentException("YAML values must be JSON-compatible");
    }
}
