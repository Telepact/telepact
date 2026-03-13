//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal;

import java.util.ArrayList;
import java.util.Base64;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import io.github.telepact.RandomGenerator;
import io.github.telepact.TelepactSchema;
import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TType;

public class GetApiDefinitionsWithExamples {
    private static final int EXAMPLE_COLLECTION_LENGTH = 2;

    public static List<Object> getApiDefinitionsWithExamples(TelepactSchema telepactSchema, boolean includeInternal) {
        final var definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
        final var defaultFnScope = getDefaultFnScope(telepactSchema.parsed);

        return definitions.stream()
                .map(definition -> addExamplesToDefinition((Map<String, Object>) definition, telepactSchema, defaultFnScope))
                .collect(Collectors.toList());
    }

    private static Map<String, Object> addExamplesToDefinition(
            Map<String, Object> definition,
            TelepactSchema telepactSchema,
            String defaultFnScope) {
        final var schemaKey = getSchemaKey(definition);
        final var clonedDefinition = new LinkedHashMap<String, Object>(definition);

        if (schemaKey.startsWith("info.")) {
            clonedDefinition.put("example", Map.of());
            return clonedDefinition;
        }

        final var randomGenerator = new RandomGenerator(EXAMPLE_COLLECTION_LENGTH, EXAMPLE_COLLECTION_LENGTH);

        if (schemaKey.startsWith("fn.")) {
            final var ctx = new GenerateContext(true, false, true, schemaKey, randomGenerator);
            clonedDefinition.put("inputExample",
                    normalizeExampleValue(
                            telepactSchema.parsed.get(schemaKey).generateRandomValue(null, false, List.of(), ctx)));
            clonedDefinition.put("outputExample",
                    normalizeExampleValue(
                            telepactSchema.parsed.get(schemaKey + ".->").generateRandomValue(null, false, List.of(), ctx)));
            return clonedDefinition;
        }

        if (schemaKey.startsWith("headers.")) {
            final var ctx = new GenerateContext(true, false, true, defaultFnScope, randomGenerator);
            clonedDefinition.put("inputExample", generateHeaderExample(
                    (Map<String, Object>) definition.getOrDefault(schemaKey, Map.of()),
                    telepactSchema.parsedRequestHeaders,
                    ctx));
            clonedDefinition.put("outputExample", generateHeaderExample(
                    (Map<String, Object>) definition.getOrDefault("->", Map.of()),
                    telepactSchema.parsedResponseHeaders,
                    ctx));
            return clonedDefinition;
        }

        if (schemaKey.startsWith("errors.")) {
            final var ctx = new GenerateContext(true, false, true, defaultFnScope, randomGenerator);
            clonedDefinition.put("example",
                    generateRawUnionExample((List<Object>) definition.get(schemaKey), telepactSchema, ctx));
            return clonedDefinition;
        }

        final var ctx = new GenerateContext(true, false, true, defaultFnScope, randomGenerator);
        clonedDefinition.put("example",
                normalizeExampleValue(
                        telepactSchema.parsed.get(schemaKey).generateRandomValue(null, false, List.of(), ctx)));
        return clonedDefinition;
    }

    private static Map<String, Object> generateHeaderExample(
            Map<String, Object> headerDefinition,
            Map<String, TFieldDeclaration> parsedHeaders,
            GenerateContext ctx) {
        final var example = new LinkedHashMap<String, Object>();
        final var headerNames = new ArrayList<>(headerDefinition.keySet());
        headerNames.sort(Comparator.naturalOrder());

        for (final var headerName : headerNames) {
            example.put(
                    headerName,
                    normalizeExampleValue(
                            parsedHeaders.get(headerName).typeDeclaration.generateRandomValue(null, false, ctx)));
        }

        return example;
    }

    private static Map<String, Object> generateRawUnionExample(
            List<Object> unionDefinition,
            TelepactSchema telepactSchema,
            GenerateContext ctx) {
        final var tags = unionDefinition.stream()
                .map(tagDefinition -> {
                    final var tagMap = (Map<String, Object>) tagDefinition;
                    return tagMap.entrySet().stream()
                            .filter(entry -> !entry.getKey().equals("///"))
                            .findFirst()
                            .orElseThrow();
                })
                .sorted(Map.Entry.comparingByKey())
                .toList();
        final var tag = tags.get(ctx.randomGenerator.nextIntWithCeiling(tags.size()));
        return Map.of(tag.getKey(), generateRawStructExample((Map<String, Object>) tag.getValue(), telepactSchema, ctx));
    }

    private static Map<String, Object> generateRawStructExample(
            Map<String, Object> structDefinition,
            TelepactSchema telepactSchema,
            GenerateContext ctx) {
        final var example = new LinkedHashMap<String, Object>();
        final var fieldNames = new ArrayList<>(structDefinition.keySet());
        fieldNames.sort(Comparator.naturalOrder());

        for (final var fieldName : fieldNames) {
            final var optional = fieldName.endsWith("!");
            if (optional) {
                if (!ctx.includeOptionalFields
                        || (ctx.randomizeOptionalFields && ctx.randomGenerator.nextBoolean())) {
                    continue;
                }
            } else if (!ctx.alwaysIncludeRequiredFields && ctx.randomGenerator.nextBoolean()) {
                continue;
            }

            example.put(fieldName, generateRawTypeExample(structDefinition.get(fieldName), telepactSchema, ctx));
        }

        return example;
    }

    private static Object generateRawTypeExample(
            Object typeExpression,
            TelepactSchema telepactSchema,
            GenerateContext ctx) {
        if (typeExpression instanceof String) {
            final var typeString = (String) typeExpression;
            final var nullable = typeString.endsWith("?");
            final var nonNullableTypeExpression = nullable ? typeString.substring(0, typeString.length() - 1) : typeString;
            if (nullable && ctx.randomGenerator.nextBoolean()) {
                return null;
            }

            return switch (nonNullableTypeExpression) {
                case "boolean" -> ctx.randomGenerator.nextBoolean();
                case "integer" -> ctx.randomGenerator.nextInt();
                case "number" -> ctx.randomGenerator.nextDouble();
                case "string" -> ctx.randomGenerator.nextString();
                case "any" -> {
                    final var selectType = ctx.randomGenerator.nextIntWithCeiling(3);
                    if (selectType == 0) {
                        yield ctx.randomGenerator.nextBoolean();
                    } else if (selectType == 1) {
                        yield ctx.randomGenerator.nextInt();
                    } else {
                        yield ctx.randomGenerator.nextString();
                    }
                }
                case "bytes" -> Base64.getEncoder().encodeToString(ctx.randomGenerator.nextBytes());
                default -> normalizeExampleValue(
                        telepactSchema.parsed.get(nonNullableTypeExpression).generateRandomValue(null, false, List.of(), ctx));
            };
        }

        if (typeExpression instanceof List) {
            final var nestedType = ((List<Object>) typeExpression).get(0);
            final var length = ctx.randomGenerator.nextCollectionLength();
            final var example = new ArrayList<Object>(length);
            for (int i = 0; i < length; i += 1) {
                example.add(generateRawTypeExample(nestedType, telepactSchema, ctx));
            }
            return example;
        }

        if (typeExpression instanceof Map) {
            final var objectDefinition = (Map<String, Object>) typeExpression;
            if (objectDefinition.size() == 1 && objectDefinition.containsKey("string")) {
                final var length = ctx.randomGenerator.nextCollectionLength();
                final var example = new LinkedHashMap<String, Object>();
                for (int i = 0; i < length; i += 1) {
                    example.put(
                            ctx.randomGenerator.nextString(),
                            generateRawTypeExample(objectDefinition.get("string"), telepactSchema, ctx));
                }
                return example;
            }
        }

        return null;
    }

    private static Object normalizeExampleValue(Object value) {
        if (value instanceof byte[]) {
            return Base64.getEncoder().encodeToString((byte[]) value);
        }

        if (value instanceof List) {
            return ((List<?>) value).stream().map(GetApiDefinitionsWithExamples::normalizeExampleValue).toList();
        }

        if (value instanceof Map) {
            final var normalized = new LinkedHashMap<String, Object>();
            for (final var entry : ((Map<?, ?>) value).entrySet()) {
                normalized.put(String.valueOf(entry.getKey()), normalizeExampleValue(entry.getValue()));
            }
            return normalized;
        }

        return value;
    }

    private static String getDefaultFnScope(Map<String, TType> parsedTypes) {
        final var nonInternalFunctions = parsedTypes.keySet().stream()
                .filter(schemaKey -> schemaKey.startsWith("fn."))
                .filter(schemaKey -> !schemaKey.endsWith(".->"))
                .filter(schemaKey -> !schemaKey.endsWith("_"))
                .sorted()
                .toList();
        if (!nonInternalFunctions.isEmpty()) {
            return nonInternalFunctions.get(0);
        }

        final var allFunctions = parsedTypes.keySet().stream()
                .filter(schemaKey -> schemaKey.startsWith("fn."))
                .filter(schemaKey -> !schemaKey.endsWith(".->"))
                .sorted()
                .toList();
        if (!allFunctions.isEmpty()) {
            return allFunctions.get(0);
        }

        return "fn.ping_";
    }

    private static String getSchemaKey(Map<String, Object> definition) {
        for (final var key : definition.keySet()) {
            if (!key.equals("///") && !key.equals("->") && !key.equals("_errors")) {
                return key;
            }
        }

        throw new IllegalArgumentException("Schema entry has no schema key: " + definition);
    }
}
