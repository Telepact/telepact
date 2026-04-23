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

public class GetIncrementalApiDefinitions {
    private static final List<String> ENTRYPOINT_PREFIXES = List.of("info.", "headers.", "errors.", "fn.");
    private static final List<String> CUSTOM_TYPE_PREFIXES = List.of("fn.", "struct.", "union.", "headers.", "errors.", "info.", "_ext.");

    public static List<Object> getApiEntrypointDefinitions(TelepactSchema telepactSchema, boolean includeInternal) {
        final var definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
        return definitions.stream()
                .filter(definition -> hasPrefix(
                        GetApiDefinitionsWithExamples.getSchemaKey((Map<String, Object>) definition),
                        ENTRYPOINT_PREFIXES))
                .toList();
    }

    public static List<Object> getApiDefinitionsBySchemaKey(
            TelepactSchema telepactSchema,
            String schemaKey,
            boolean includeInternal) {
        final var definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
        final var definitionsByKey = new LinkedHashMap<String, Map<String, Object>>();
        for (final var definition : definitions) {
            final var definitionMap = (Map<String, Object>) definition;
            definitionsByKey.put(GetApiDefinitionsWithExamples.getSchemaKey(definitionMap), definitionMap);
        }
        if (!definitionsByKey.containsKey(schemaKey)) {
            return null;
        }

        final var includedSchemaKeys = new LinkedHashSet<String>();
        final var pendingSchemaKeys = new ArrayList<String>(List.of(schemaKey));
        while (!pendingSchemaKeys.isEmpty()) {
            final var currentSchemaKey = pendingSchemaKeys.remove(pendingSchemaKeys.size() - 1);
            if (!includedSchemaKeys.add(currentSchemaKey)) {
                continue;
            }

            final var definitionMap = definitionsByKey.get(currentSchemaKey);
            if (definitionMap == null) {
                continue;
            }

            for (final var referencedSchemaKey : getReferencedSchemaKeys(definitionMap, definitionsByKey)) {
                if (!includedSchemaKeys.contains(referencedSchemaKey)) {
                    pendingSchemaKeys.add(referencedSchemaKey);
                }
            }
        }

        return definitions.stream()
                .filter(definition -> includedSchemaKeys.contains(
                        GetApiDefinitionsWithExamples.getSchemaKey((Map<String, Object>) definition)))
                .toList();
    }

    private static List<String> getReferencedSchemaKeys(
            Map<String, Object> definition,
            Map<String, Map<String, Object>> definitionsByKey) {
        final Set<String> references = new LinkedHashSet<>();
        for (final var entry : definition.entrySet()) {
            if (entry.getKey().equals("///") || entry.getKey().equals("_errors")) {
                continue;
            }
            collectReferencedSchemaKeys(entry.getValue(), definitionsByKey, references);
        }

        if (definition.get("_errors") instanceof String errorsRegex) {
            final var regex = Pattern.compile(errorsRegex);
            for (final var schemaKey : definitionsByKey.keySet()) {
                if (regex.matcher(schemaKey).matches()) {
                    references.add(schemaKey);
                }
            }
        }

        return references.stream().sorted().toList();
    }

    private static void collectReferencedSchemaKeys(
            Object value,
            Map<String, Map<String, Object>> definitionsByKey,
            Set<String> references) {
        if (value instanceof String stringValue) {
            final var schemaKey = stringValue.endsWith("?")
                    ? stringValue.substring(0, stringValue.length() - 1)
                    : stringValue;
            if (hasPrefix(schemaKey, CUSTOM_TYPE_PREFIXES) && definitionsByKey.containsKey(schemaKey)) {
                references.add(schemaKey);
            }
            return;
        }

        if (value instanceof List<?> listValue) {
            for (final var entry : listValue) {
                collectReferencedSchemaKeys(entry, definitionsByKey, references);
            }
            return;
        }

        if (value instanceof Map<?, ?> mapValue) {
            for (final var entry : mapValue.entrySet()) {
                if (String.valueOf(entry.getKey()).equals("///")) {
                    continue;
                }
                collectReferencedSchemaKeys(entry.getValue(), definitionsByKey, references);
            }
        }
    }

    private static boolean hasPrefix(String value, List<String> prefixes) {
        return prefixes.stream().anyMatch(value::startsWith);
    }
}
