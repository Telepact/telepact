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
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchema;

public class SchemaIntrospection {
    public static List<Object> getIndexEntries(TelepactSchema telepactSchema, boolean includeInternal) {
        final var definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
        final var entries = new ArrayList<Object>();

        for (final var definition : definitions) {
            final var definitionMap = (Map<String, Object>) definition;
            final var schemaKey = getSchemaKey(definitionMap);
            if (!schemaKey.startsWith("fn.") || schemaKey.endsWith(".->")) {
                continue;
            }
            if (!includeInternal && schemaKey.endsWith("_")) {
                continue;
            }

            final var entry = new LinkedHashMap<String, Object>();
            entry.put("name", schemaKey);
            if (definitionMap.containsKey("///")) {
                entry.put("comment!", definitionMap.get("///"));
            }
            entries.add(entry);
        }

        return entries;
    }

    public static List<Object> getDefinitionClosure(
            TelepactSchema telepactSchema,
            String name,
            boolean includeInternal) {
        final var rootDefinition = getRootDefinition(telepactSchema, name, includeInternal);
        if (rootDefinition == null) {
            return List.of();
        }

        final Map<String, Map<String, Object>> definitionsByName = new LinkedHashMap<>();
        for (final var definition : telepactSchema.full) {
            final var definitionMap = (Map<String, Object>) definition;
            definitionsByName.put(getSchemaKey(definitionMap), definitionMap);
        }

        final Set<String> visited = new LinkedHashSet<>();
        visitDefinition(getSchemaKey(rootDefinition), definitionsByName, visited);

        final var closure = new ArrayList<Object>();
        for (final var definition : telepactSchema.full) {
            final var definitionMap = (Map<String, Object>) definition;
            if (visited.contains(getSchemaKey(definitionMap))) {
                closure.add(definition);
            }
        }

        return closure;
    }

    private static void visitDefinition(
            String schemaKey,
            Map<String, Map<String, Object>> definitionsByName,
            Set<String> visited) {
        if (visited.contains(schemaKey)) {
            return;
        }

        final var definition = definitionsByName.get(schemaKey);
        if (definition == null) {
            return;
        }

        visited.add(schemaKey);
        for (final var reference : getDefinitionReferences(definition, definitionsByName)) {
            visitDefinition(reference, definitionsByName, visited);
        }
    }

    private static Map<String, Object> getRootDefinition(
            TelepactSchema telepactSchema,
            String name,
            boolean includeInternal) {
        if (!includeInternal && name.endsWith("_")) {
            return null;
        }

        final var definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
        for (final var definition : definitions) {
            final var definitionMap = (Map<String, Object>) definition;
            if (getSchemaKey(definitionMap).equals(name)) {
                return definitionMap;
            }
        }

        return null;
    }

    private static Set<String> getDefinitionReferences(
            Map<String, Object> definition,
            Map<String, Map<String, Object>> definitionsByName) {
        final var references = new LinkedHashSet<String>();
        final var schemaKey = getSchemaKey(definition);

        for (final var entry : definition.entrySet()) {
            switch (entry.getKey()) {
                case "///":
                    break;
                case "_errors":
                    if (entry.getValue() instanceof String regexString) {
                        final var regex = Pattern.compile(regexString);
                        for (final var candidate : definitionsByName.keySet()) {
                            if (regex.matcher(candidate).matches()) {
                                references.add(candidate);
                            }
                        }
                    }
                    break;
                case "->":
                    references.addAll(getTypeExpressionReferences(entry.getValue(), definitionsByName));
                    break;
                default:
                    if (entry.getKey().equals(schemaKey)) {
                        references.addAll(getTypeExpressionReferences(entry.getValue(), definitionsByName));
                    }
                    break;
            }
        }

        return references;
    }

    private static Set<String> getTypeExpressionReferences(
            Object typeExpression,
            Map<String, Map<String, Object>> definitionsByName) {
        final var references = new LinkedHashSet<String>();

        if (typeExpression instanceof String typeString) {
            final var schemaKey = typeString.endsWith("?")
                    ? typeString.substring(0, typeString.length() - 1)
                    : typeString;
            if (definitionsByName.containsKey(schemaKey)) {
                references.add(schemaKey);
            }
            return references;
        }

        if (typeExpression instanceof List<?> list) {
            if (isUnionDefinition(list)) {
                for (final var tagDefinition : list) {
                    final var tagMap = (Map<String, Object>) tagDefinition;
                    for (final var entry : tagMap.entrySet()) {
                        if (entry.getKey().equals("///")) {
                            continue;
                        }
                        references.addAll(getTypeExpressionReferences(entry.getValue(), definitionsByName));
                    }
                }
            } else if (!list.isEmpty()) {
                references.addAll(getTypeExpressionReferences(list.get(0), definitionsByName));
            }
            return references;
        }

        if (typeExpression instanceof Map<?, ?> objectDefinition) {
            if (objectDefinition.size() == 1 && objectDefinition.containsKey("string")) {
                references.addAll(getTypeExpressionReferences(objectDefinition.get("string"), definitionsByName));
                return references;
            }

            for (final var value : objectDefinition.values()) {
                references.addAll(getTypeExpressionReferences(value, definitionsByName));
            }
        }

        return references;
    }

    private static boolean isUnionDefinition(List<?> typeExpression) {
        if (typeExpression.isEmpty()) {
            return false;
        }

        for (final var entry : typeExpression) {
            if (!(entry instanceof Map<?, ?> entryMap)) {
                return false;
            }

            var nonCommentKeys = 0;
            for (final var mapEntry : entryMap.entrySet()) {
                final var key = String.valueOf(mapEntry.getKey());
                if (key.equals("///")) {
                    continue;
                }
                if (!(mapEntry.getValue() instanceof Map<?, ?>)) {
                    return false;
                }
                nonCommentKeys += 1;
            }
            if (nonCommentKeys != 1) {
                return false;
            }
        }

        return true;
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
