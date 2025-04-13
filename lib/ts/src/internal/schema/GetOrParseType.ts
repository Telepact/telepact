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

import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { TType } from '../types/TType';
import { TObject } from '../types/TObject';
import { TArray } from '../types/TArray';
import { TBoolean } from '../types/TBoolean';
import { TInteger } from '../types/TInteger';
import { TNumber } from '../types/TNumber';
import { TString } from '../types/TString';
import { TAny } from '../types/TAny';
import { TBytes } from '../types/TBytes';
import { parseFunctionErrorsRegex, parseFunctionResultType } from '../../internal/schema/ParseFunctionType';
import { parseStructType } from '../../internal/schema/ParseStructType';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { TSelect } from '../types/TSelect';
import { TMockCall } from '../types/TMockCall';
import { TMockStub } from '../types/TMockStub';
import { ParseContext } from '../../internal/schema/ParseContext';
import { TUnion } from '../types/TUnion';

export function getOrParseType(path: any[], typeName: string, ctx: ParseContext): TType {
    if (ctx.failedTypes.has(typeName)) {
        throw new TelepactSchemaParseError([], ctx.telepactSchemaDocumentNamesToJson);
    }

    const existingType = ctx.parsedTypes[typeName];
    if (existingType !== undefined) {
        return existingType;
    }

    const regexString = `^(boolean|integer|number|string|any|bytes|array|object)|((fn|(union|struct|_ext))\\.([a-zA-Z_]\\w*))$`;
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
                array: new TArray(),
                object: new TObject(),
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
            type = parseStructType(
                [thisIndex],
                definition,
                customTypeName,
                [],
                ctx.copy({ documentName: thisDocumentName }),
            );

            ctx.parsedTypes[customTypeName] = type;
        } else if (customTypeName.startsWith('union')) {
            type = parseUnionType(
                [thisIndex],
                definition,
                customTypeName,
                [],
                [],
                ctx.copy({ documentName: thisDocumentName }),
            );

            ctx.parsedTypes[customTypeName] = type;
        } else if (customTypeName.startsWith('fn')) {
            const argType = parseStructType([thisIndex], definition, customTypeName, ['->', '_errors'], ctx.copy({ documentName: thisDocumentName }));
            type = new TUnion(customTypeName, { [customTypeName]: argType }, { [customTypeName]: 0 });

            ctx.parsedTypes[customTypeName] = type;

            const resultType = parseFunctionResultType([thisIndex],
                definition,
                customTypeName,
                ctx.copy({ documentName: thisDocumentName }));
            
            ctx.parsedTypes[customTypeName + '.->'] = resultType;

            const errorsRegex = parseFunctionErrorsRegex([thisIndex],
                definition,
                customTypeName,
                ctx.copy({ documentName: thisDocumentName }));

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
