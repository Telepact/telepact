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

import static io.github.telepact.internal.schema.DerivePossibleSelects.derivePossibleSelect;
import static io.github.telepact.internal.schema.GetOrParseType.getOrParseType;
import static io.github.telepact.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.telepact.internal.schema.ParseStructType.parseStructType;
import static io.github.telepact.internal.schema.ParseUnionType.parseUnionType;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.TSelect;
import io.github.telepact.internal.types.TStruct;
import io.github.telepact.internal.types.TUnion;

public class ParseFunctionType {

    static TUnion parseFunctionResultType(
            List<Object> path,
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();

        final var resultSchemaKey = "->";

        final List<Object> resPath = new ArrayList<>(path);

        TUnion resultType = null;
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


        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }

        var fnSelectType = derivePossibleSelect(schemaKey, resultType);
        var selectType = (TSelect) getOrParseType(path, "_ext.Select_", ctx);
        selectType.possibleSelects.put(schemaKey, fnSelectType);

        return resultType;
    }

    static String parseFunctionErrorsRegex(
            List<Object> path,
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();


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

        return errorsRegex;
    }    

}
