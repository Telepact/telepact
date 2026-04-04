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

import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { TType } from '../types/TType.js';
import { TObject } from '../types/TObject.js';
import { TArray } from '../types/TArray.js';
import { TBoolean } from '../types/TBoolean.js';
import { TInteger } from '../types/TInteger.js';
import { TNumber } from '../types/TNumber.js';
import { TString } from '../types/TString.js';
import { TAny } from '../types/TAny.js';
import { TBytes } from '../types/TBytes.js';
import { parseFunctionErrorsRegex, parseFunctionResultType } from '../../internal/schema/ParseFunctionType.js';
import { parseStructType } from '../../internal/schema/ParseStructType.js';
import { parseUnionType } from '../../internal/schema/ParseUnionType.js';
import { TSelect } from '../types/TSelect.js';
import { TMockCall } from '../types/TMockCall.js';
import { TMockStub } from '../types/TMockStub.js';
import { ParseContext } from '../../internal/schema/ParseContext.js';
import { TStruct } from '../types/TStruct.js';
import { TUnion } from '../types/TUnion.js';

export function getOrParseType(path: any[], typeName: string, ctx: ParseContext): TType {
    if (ctx.failedTypes.has(typeName)) {
        throw new TelepactSchemaParseError([], ctx.telepactSchemaDocumentNamesToJson);
    }

    const existingType = ctx.parsedTypes[typeName];
    if (existingType !== undefined) {
        return existingType;
    }

    const regexString = `^(boolean|integer|number|string|any|bytes)|((fn|(union|struct|_ext))\\.([a-zA-Z_]\\w*))$`;
    const regex = new RegExp(regexString);

    const matcher = typeName.match(regex);
    if (!matcher) {
        throw new TelepactSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, path, 'StringRegexMatchFailed', { regex: regexString })],
            ctx.telepactSchemaDocumentNamesToJson,
        );
    }

    const standardTypeName = matcher[1];
    if (standardTypeName) {
        return (
            {
                boolean: new TBoolean(),
                integer: new TInteger(),
                number: new TNumber(),
                string: new TString(),
                bytes: new TBytes(),
            }[standardTypeName] || new TAny()
        );
    }

    const customTypeName = matcher[2];
    const thisIndex = ctx.schemaKeysToIndex[customTypeName];
    const thisDocumentName = ctx.schemaKeysToDocumentName[customTypeName];
    if (thisIndex === undefined) {
        throw new TelepactSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, path, 'TypeUnknown', { name: customTypeName })],
            ctx.telepactSchemaDocumentNamesToJson,
        );
    }
    const definition = ctx.telepactSchemaDocumentNamesToPseudoJson[thisDocumentName][thisIndex] as {
        [key: string]: object;
    };

    let type: TType;
    try {
        if (customTypeName.startsWith('struct')) {
            const placeholder = new TStruct(customTypeName, {});
            type = placeholder;
            ctx.parsedTypes[customTypeName] = type;
            const parsedType = parseStructType(
                [thisIndex],
                definition,
                customTypeName,
                [],
                ctx.copy({ documentName: thisDocumentName }),
            );
            placeholder.fields = parsedType.fields;
        } else if (customTypeName.startsWith('union')) {
            const placeholder = new TUnion(customTypeName, {}, {});
            type = placeholder;
            ctx.parsedTypes[customTypeName] = type;
            const parsedType = parseUnionType(
                [thisIndex],
                definition,
                customTypeName,
                [],
                [],
                ctx.copy({ documentName: thisDocumentName }),
            );
            placeholder.tags = parsedType.tags;
            placeholder.tagIndices = parsedType.tagIndices;
        } else if (customTypeName.startsWith('fn')) {
            const placeholder = new TUnion(customTypeName, {}, {});
            type = placeholder;
            ctx.parsedTypes[customTypeName] = type;
            const argType = parseStructType(
                [thisIndex],
                definition,
                customTypeName,
                ['->', '_errors'],
                ctx.copy({ documentName: thisDocumentName }),
            );
            placeholder.tags[customTypeName] = argType;
            placeholder.tagIndices[customTypeName] = 0;

            const resultType = parseFunctionResultType(
                [thisIndex],
                definition,
                customTypeName,
                ctx.copy({ documentName: thisDocumentName }),
            );

            ctx.parsedTypes[customTypeName + '.->'] = resultType;

            const errorsRegex = parseFunctionErrorsRegex(
                [thisIndex],
                definition,
                customTypeName,
                ctx.copy({ documentName: thisDocumentName }),
            );

            ctx.fnErrorRegexes[customTypeName] = errorsRegex;
        } else {
            const possibleTypeExtension = {
                '_ext.Select_': new TSelect(),
                '_ext.Call_': new TMockCall(ctx.parsedTypes),
                '_ext.Stub_': new TMockStub(ctx.parsedTypes),
            }[customTypeName];
            if (!possibleTypeExtension) {
                throw new TelepactSchemaParseError(
                    [
                        new SchemaParseFailure(ctx.documentName, [thisIndex], 'TypeExtensionImplementationMissing', {
                            name: customTypeName,
                        }),
                    ],
                    ctx.telepactSchemaDocumentNamesToJson,
                );
            }
            type = possibleTypeExtension;

            ctx.parsedTypes[customTypeName] = type;
        }


        return type;
    } catch (e) {
        if (e instanceof TelepactSchemaParseError) {
            ctx.allParseFailures.push(...e.schemaParseFailures);
            ctx.failedTypes.add(customTypeName);
            throw new TelepactSchemaParseError([], ctx.telepactSchemaDocumentNamesToJson);
        }
        throw e;
    }
}
