package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseStructType.parseStructType;
import static uapi.internal.schema.ParseUnionType.parseUnionType;
import static uapi.internal.schema.GetOrParseType.getOrParseType;
import static uapi.internal.schema.DerivePossibleSelects.derivePossibleSelect;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UFn;
import uapi.internal.types.USelect;
import uapi.internal.types.UStruct;
import uapi.internal.types.UUnion;

public class ParseFunctionType {

    static UFn parseFunctionType(
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();

        UUnion callType = null;
        try {
            final UStruct argType = parseStructType(functionDefinitionAsParsedJson,
                    schemaKey, List.of("->", "_errors"), ctx);
            callType = new UUnion(schemaKey, Map.of(schemaKey, argType), Map.of(schemaKey, 0));
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        final var resultSchemaKey = "->";

        final List<Object> resPath = new ArrayList<>(ctx.path);

        UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey(resultSchemaKey)) {
            parseFailures.add(new SchemaParseFailure(ctx.documentName, resPath, "RequiredObjectKeyMissing",
                    Map.of("key", resultSchemaKey)));
        } else {
            try {
                resultType = parseUnionType(functionDefinitionAsParsedJson,
                        resultSchemaKey, functionDefinitionAsParsedJson.keySet().stream().toList(), List.of("Ok_"),
                        ctx);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        final var errorsRegexKey = "_errors";

        final var regexPath = new ArrayList<>(ctx.path);
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
            throw new UApiSchemaParseError(parseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }

        var fnSelectType = derivePossibleSelect(schemaKey, resultType);
        var selectType = (USelect) getOrParseType("_ext.Select_", ctx);
        selectType.possibleSelects.put(schemaKey, fnSelectType);

        return new UFn(schemaKey, callType, resultType, errorsRegex);
    }

}
