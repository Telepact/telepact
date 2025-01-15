package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseStructFields.parseStructFields;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UStruct;
import uapi.internal.types.UType;
import uapi.internal.types.UUnion;

public class ParseUnionType {
    static UUnion parseUnionType(
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
                final List<Object> loopPath = new ArrayList<>(ctx.path);
                loopPath.add(k);

                parseFailures.add(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectKeyDisallowed", Map.of()));
            }
        }

        final List<Object> thisPath = new ArrayList<>(ctx.path);
        thisPath.add(schemaKey);

        final Object defInit = unionDefinitionAsPseudoJson.get(schemaKey);

        if (!(defInit instanceof List)) {
            final List<SchemaParseFailure> finalParseFailures = getTypeUnexpectedParseFailure(ctx.documentName,
                    thisPath,
                    defInit, "Array");

            parseFailures.addAll(finalParseFailures);
            throw new UApiSchemaParseError(parseFailures, ctx.uApiSchemaDocumentNamesToJson);
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
            throw new UApiSchemaParseError(parseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }

        if (definition.isEmpty()) {
            parseFailures.add(new SchemaParseFailure(ctx.documentName, thisPath, "EmptyArrayDisallowed", Map.of()));
        } else {
            outerLoop: for (final var requiredKey : requiredKeys) {
                for (final var element : definition) {
                    final var map = (Map<String, Object>) element;
                    final var caseKeys = new HashSet<>(map.keySet());
                    caseKeys.remove("///");
                    if (caseKeys.contains(requiredKey)) {
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

        final var cases = new HashMap<String, UStruct>();
        final var caseIndices = new HashMap<String, Integer>();

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
            final var unionCase = entry.getKey();

            final List<Object> unionKeyPath = new ArrayList<>(loopPath);
            unionKeyPath.add(unionCase);

            if (!(entry.getValue() instanceof Map)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName,
                        unionKeyPath,
                        entry.getValue(), "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }
            final Map<String, Object> unionCaseStruct = (Map<String, Object>) entry.getValue();

            final Map<String, UFieldDeclaration> fields;
            try {
                fields = parseStructFields(unionCaseStruct,
                        ctx.copyWithNewPath(unionKeyPath));
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            final var unionStruct = new UStruct("%s.%s".formatted(schemaKey, unionCase), fields);

            cases.put(unionCase, unionStruct);
            caseIndices.put(unionCase, i);
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }

        return new UUnion(schemaKey, cases, caseIndices);
    }
}
