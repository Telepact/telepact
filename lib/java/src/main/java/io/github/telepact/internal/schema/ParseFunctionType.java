package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.DerivePossibleSelects.derivePossibleSelect;
import static io.github.telepact.internal.schema.GetOrParseType.getOrParseType;
import static io.github.telepact.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.telepact.internal.schema.ParseStructType.parseStructType;
import static io.github.telepact.internal.schema.ParseUnionType.parseUnionType;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.VFn;
import io.github.telepact.internal.types.VSelect;
import io.github.telepact.internal.types.VStruct;
import io.github.telepact.internal.types.VUnion;

public class ParseFunctionType {

    static VFn parseFunctionType(
            List<Object> path,
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();

        VUnion callType = null;
        try {
            final VStruct argType = parseStructType(path, functionDefinitionAsParsedJson,
                    schemaKey, List.of("->", "_errors"), ctx);
            callType = new VUnion(schemaKey, Map.of(schemaKey, argType), Map.of(schemaKey, 0));
        } catch (TelepactSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        final var resultSchemaKey = "->";

        final List<Object> resPath = new ArrayList<>(path);

        VUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey(resultSchemaKey)) {
            parseFailures.add(new SchemaParseFailure(ctx.documentName, resPath, "RequiredObjectKeyMissing",
                    Map.of("key", resultSchemaKey)));
        } else {
            try {
                resultType = parseUnionType(path, functionDefinitionAsParsedJson,
                        resultSchemaKey, functionDefinitionAsParsedJson.keySet().stream().toList(), List.of("Ok_"),
                        ctx);
            } catch (TelepactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        final var errorsRegexKey = "_errors";

        final var regexPath = new ArrayList<>(path);
        regexPath.add(errorsRegexKey);

        String errorsRegex = null;
        if (functionDefinitionAsParsedJson.containsKey(errorsRegexKey) && !schemaKey.endsWith("_")) {
            parseFailures.add(new SchemaParseFailure(ctx.documentName, regexPath, "ObjectKeyDisallowed", Map.of()));
        } else {
            final Object errorsRegexInit = functionDefinitionAsParsedJson.getOrDefault(errorsRegexKey,
                    "^errors\\..*$");

            if (!(errorsRegexInit instanceof String)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(
                        ctx.documentName, regexPath, errorsRegexInit, "String");

                parseFailures
                        .addAll(thisParseFailures);
            } else {
                errorsRegex = (String) errorsRegexInit;
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }

        var fnSelectType = derivePossibleSelect(schemaKey, resultType);
        var selectType = (VSelect) getOrParseType(path, "_ext.Select_", ctx);
        selectType.possibleSelects.put(schemaKey, fnSelectType);

        return new VFn(schemaKey, callType, resultType, errorsRegex);
    }

}
