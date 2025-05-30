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

package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.telepact.internal.schema.ParseStructFields.parseStructFields;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TStruct;
import io.github.telepact.internal.types.TUnion;

public class ParseUnionType {
    static TUnion parseUnionType(
            List<Object> path,
            Map<String, Object> unionDefinitionAsPseudoJson, String schemaKey,
            List<String> ignoreKeys, List<String> requiredKeys,
            ParseContext ctx) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();

        final var otherKeys = new HashSet<>(unionDefinitionAsPseudoJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");
        for (final var ignoreKey : ignoreKeys) {
            otherKeys.remove(ignoreKey);
        }

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = new ArrayList<>(path);
                loopPath.add(k);

                parseFailures.add(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectKeyDisallowed", Map.of()));
            }
        }

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(schemaKey);

        final Object defInit = unionDefinitionAsPseudoJson.get(schemaKey);

        if (!(defInit instanceof List)) {
            final List<SchemaParseFailure> finalParseFailures = getTypeUnexpectedParseFailure(ctx.documentName,
                    thisPath,
                    defInit, "Array");

            parseFailures.addAll(finalParseFailures);
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }
        final List<Object> definition2 = (List<Object>) defInit;

        final List<Map<String, Object>> definition = new ArrayList<>();
        int index = -1;
        for (final var element : definition2) {
            index += 1;

            final List<Object> loopPath = new ArrayList<>(thisPath);
            loopPath.add(index);

            if (!(element instanceof Map)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName,
                        loopPath,
                        element, "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            definition.add((Map<String, Object>) element);
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }

        if (definition.isEmpty()) {
            parseFailures.add(new SchemaParseFailure(ctx.documentName, thisPath, "EmptyArrayDisallowed", Map.of()));
        } else {
            outerLoop: for (final var requiredKey : requiredKeys) {
                for (final var element : definition) {
                    final var map = (Map<String, Object>) element;
                    final var tagKeys = new HashSet<>(map.keySet());
                    tagKeys.remove("///");
                    if (tagKeys.contains(requiredKey)) {
                        continue outerLoop;
                    }
                }

                final List<Object> branchPath = new ArrayList<>(thisPath);
                branchPath.add(0);

                parseFailures
                        .add(new SchemaParseFailure(ctx.documentName, branchPath, "RequiredObjectKeyMissing",
                                Map.of("key", requiredKey)));
            }
        }

        final var tags = new HashMap<String, TStruct>();
        final var tagIndices = new HashMap<String, Integer>();

        for (int i = 0; i < definition.size(); i++) {
            final var element = definition.get(i);

            final List<Object> loopPath = new ArrayList<>(thisPath);
            loopPath.add(i);

            final var mapInit = (Map<String, Object>) element;
            final var map = new HashMap<>(mapInit);
            map.remove("///");
            final var keys = new ArrayList<>(map.keySet());

            final var regexString = "^([A-Z][a-zA-Z0-9_]*)$";

            final var matches = keys.stream().filter(k -> k.matches(regexString)).toList();
            if (matches.size() != 1) {
                parseFailures.add(
                        new SchemaParseFailure(ctx.documentName, loopPath,
                                "ObjectKeyRegexMatchCountUnexpected",
                                Map.of("regex", regexString, "actual",
                                        matches.size(), "expected", 1, "keys", keys)));
                continue;
            }
            if (map.size() != 1) {
                parseFailures.add(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectSizeUnexpected",
                        Map.of("expected", 1, "actual", map.size())));
                continue;
            }

            final var entry = map.entrySet().stream().findAny().get();
            final var unionTag = entry.getKey();

            final List<Object> unionKeyPath = new ArrayList<>(loopPath);
            unionKeyPath.add(unionTag);

            if (!(entry.getValue() instanceof Map)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName,
                        unionKeyPath,
                        entry.getValue(), "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }
            final Map<String, Object> unionTagStruct = (Map<String, Object>) entry.getValue();

            final Map<String, TFieldDeclaration> fields;
            try {
                final var isHeader = false;
                fields = parseStructFields(unionKeyPath, unionTagStruct, isHeader, ctx);
            } catch (TelepactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            final var unionStruct = new TStruct("%s.%s".formatted(schemaKey, unionTag), fields);

            tags.put(unionTag, unionStruct);
            tagIndices.put(unionTag, i);
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }

        return new TUnion(schemaKey, tags, tagIndices);
    }
}
