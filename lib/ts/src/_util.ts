import { _RandomGenerator } from './_RandomGenerator';
import {
    _BinaryEncoder,
    _BinaryEncoderUnavailableError,
    _BinaryEncoding,
    _BinaryEncodingMissing,
    _InvalidMessage,
    _InvalidMessageBody,
    _MockInvocation,
    _MockStub,
    _SchemaParseFailure,
    _UAny,
    _UArray,
    _UBoolean,
    _UError,
    _UFieldDeclaration,
    _UFn,
    _UGeneric,
    _UHeaders,
    _UInteger,
    _UNumber,
    _UObject,
    _UString,
    _UStruct,
    _UType,
    _UTypeDeclaration,
    _UUnion,
    _ValidationFailure,
} from './_utilTypes';
import { UApiSchemaParseError } from './UApiSchemaParseError';
import { UApiSchema } from './UApiSchema';
import crc32 from 'crc-32';
import { Message } from './Message';
import { SerializationImpl } from './SerializationImpl';
import { SerializationError } from './SerializationError';
import { Serializer } from './Serializer';
import { UApiError } from './UApiError';
import internalUApi from '../inc/internal.uapi.json';
import mockInternalUApi from '../inc/mock-internal.uapi.json';
import { addExtension } from 'msgpackr';
import { ClientBinaryStrategy } from './ClientBinaryStrategy';

export const _ANY_NAME: Readonly<string> = 'Any';
export const _ARRAY_NAME: Readonly<string> = 'Array';
export const _BOOLEAN_NAME: Readonly<string> = 'Boolean';
export const _FN_NAME: Readonly<string> = 'Object';
export const _INTEGER_NAME: Readonly<string> = 'Integer';
export const _MOCK_CALL_NAME: Readonly<string> = '_ext._Call';
export const _MOCK_STUB_NAME: Readonly<string> = '_ext._Stub';
export const _NUMBER_NAME: Readonly<string> = 'Number';
export const _OBJECT_NAME: Readonly<string> = 'Object';
export const _STRING_NAME: Readonly<string> = 'String';
export const _STRUCT_NAME: Readonly<string> = 'Object';
export const _UNION_NAME: Readonly<string> = 'Object';
export const _SELCT_NAME: Readonly<string> = 'Object';

export function getInternalUApiJson(): string {
    return JSON.stringify(internalUApi);
}

export function getMockUApiJson(): string {
    return JSON.stringify(mockInternalUApi);
}

export function asInt(object: any): number {
    if (object === null || object === undefined || !Number.isInteger(object)) {
        throw new Error('ClassCastException');
    }
    return object as number;
}

export function asString(object: any): string {
    if (object === null || object === undefined || typeof object !== 'string') {
        throw new Error('ClassCastException');
    }
    return object as string;
}

export function asList(object: any): any[] {
    if (object === null || object === undefined || !Array.isArray(object)) {
        throw new Error('ClassCastException');
    }
    return object as any[];
}

export function asMap(object: any): Record<string, any> {
    if (object === null || object === undefined || typeof object !== 'object' || Array.isArray(object)) {
        throw new Error('ClassCastException');
    }
    return object as Record<string, any>;
}

export function offsetSchemaIndex(
    initialFailures: _SchemaParseFailure[],
    offset: number,
    schemaKeysToIndex: Record<string, number>
): _SchemaParseFailure[] {
    const finalList: _SchemaParseFailure[] = [];

    const indexToSchemaKey = Object.entries(schemaKeysToIndex).reduce(
        (m, [k, v]) => m.set(v, k),
        new Map<number, string>()
    );

    for (const f of initialFailures) {
        const reason = f.reason;
        const path = f.path;
        const data: Record<string, any> = f.data;
        const newPath = [...path];
        (newPath[0] as number) -= offset;

        let finalData: Record<string, any>;
        if (reason === 'PathCollision') {
            const otherNewPath = [...data['other']];
            (otherNewPath[0] as number) -= offset;
            finalData = { other: otherNewPath };
        } else {
            finalData = data;
        }

        const schemaKey = indexToSchemaKey.get(newPath[0]) ?? null;

        finalList.push({ path: newPath, reason, data: finalData, key: schemaKey });
    }

    return finalList;
}

export function findSchemaKey(definition: Record<string, any>, index: number): string {
    const regex = '^((fn|errors|info|headers)|((struct|union|_ext)(<[0-2]>)?))\\..*';
    const matches: string[] = [];

    for (const e of Object.keys(definition)) {
        if (e.match(regex)) {
            matches.push(e);
        }
    }

    const result = matches[0];

    if (matches.length === 1 && result != undefined) {
        return result;
    } else {
        throw new UApiSchemaParseError([
            new _SchemaParseFailure(
                [index],
                'ObjectKeyRegexMatchCountUnexpected',
                {
                    regex: regex,
                    actual: matches.length,
                    expected: 1,
                },
                null
            ),
        ]);
    }
}

export function findMatchingSchemaKey(schemaKeys: Set<string>, schemaKey: string): string | null {
    for (const k of schemaKeys) {
        const splitK = k.split('.')[1];
        const splitSchemaKey = schemaKey.split('.')[1];
        if (splitK === splitSchemaKey) {
            return k;
        }
    }
    return null;
}

export function getTypeUnexpectedParseFailure(path: any[], value: any, expectedType: string): _SchemaParseFailure[] {
    const actualType = getType(value);
    const data = {
        actual: { [actualType]: {} },
        expected: { [expectedType]: {} },
    };
    return [{ path, reason: 'TypeUnexpected', data, key: null }];
}

export function prepend(value: any, original: any[]): any[] {
    const newList = [...original];
    newList.unshift(value);
    return newList;
}

export function append(original: any[], value: any): any[] {
    const newList = [...original];
    newList.push(value);
    return newList;
}

export function parseTypeDeclaration(
    path: any[],
    typeDeclarationArray: any[],
    thisTypeParameterCount: number,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): _UTypeDeclaration {
    if (typeDeclarationArray.length === 0) {
        throw new UApiSchemaParseError([new _SchemaParseFailure(path, 'EmptyArrayDisallowed', {}, null)]);
    }

    const basePath = path.concat([0]);
    const baseType = typeDeclarationArray[0];

    let rootTypeString: string;
    try {
        rootTypeString = asString(baseType);
    } catch (e) {
        const thisParseFailures = getTypeUnexpectedParseFailure(basePath, baseType, 'String');
        throw new UApiSchemaParseError(thisParseFailures);
    }

    const regexString = '^(.+?)(\\?)?$';
    const regex = new RegExp(regexString);

    const matcher = rootTypeString.match(regex);
    if (!matcher) {
        throw new UApiSchemaParseError([
            new _SchemaParseFailure(
                basePath,
                'StringRegexMatchFailed',
                {
                    regex: regexString,
                },
                null
            ),
        ]);
    }

    const typeName = matcher[1];
    const nullable = matcher[2] !== undefined;

    const type = getOrParseType(
        basePath,
        typeName!,
        thisTypeParameterCount,
        uApiSchemaPseudoJson,
        schemaKeysToIndex,
        parsedTypes,
        typeExtensions,
        allParseFailures,
        failedTypes
    );

    if (type instanceof _UGeneric && nullable) {
        throw new UApiSchemaParseError([
            new _SchemaParseFailure(
                basePath,
                'StringRegexMatchFailed',
                {
                    regex: '^(.+?)[^\\?]$',
                },
                null
            ),
        ]);
    }

    const givenTypeParameterCount = typeDeclarationArray.length - 1;
    if (type.getTypeParameterCount() !== givenTypeParameterCount) {
        throw new UApiSchemaParseError([
            new _SchemaParseFailure(
                path,
                'ArrayLengthUnexpected',
                {
                    actual: typeDeclarationArray.length,
                    expected: type.getTypeParameterCount() + 1,
                },
                null
            ),
        ]);
    }

    const parseFailures: _SchemaParseFailure[] = [];
    const typeParameters: _UTypeDeclaration[] = [];
    const givenTypeParameters = typeDeclarationArray.slice(1);

    let index = 0;
    for (const e of givenTypeParameters) {
        index += 1;
        const loopPath = append(path, index);

        let l;
        try {
            l = asList(e);
        } catch (e1) {
            const thisParseFailures = getTypeUnexpectedParseFailure(loopPath, e, 'Array');

            parseFailures.push(...thisParseFailures);
            continue;
        }

        let typeParameterTypeDeclaration: _UTypeDeclaration;
        try {
            typeParameterTypeDeclaration = parseTypeDeclaration(
                loopPath,
                l,
                thisTypeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes
            );

            typeParameters.push(typeParameterTypeDeclaration);
        } catch (e2) {
            if (e2 instanceof UApiSchemaParseError) {
                parseFailures.push(...e2.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length !== 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    return new _UTypeDeclaration(type, nullable, typeParameters);
}

export function getOrParseType(
    path: any[],
    typeName: string,
    thisTypeParameterCount: number,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): _UType {
    if (failedTypes.has(typeName)) {
        throw new UApiSchemaParseError([]);
    }

    const existingType = parsedTypes[typeName];
    if (existingType !== undefined) {
        return existingType;
    }

    let genericRegex: string;
    if (thisTypeParameterCount > 0) {
        genericRegex = `|(T.([%s]))`.replace(
            '%s',
            thisTypeParameterCount > 1 ? '0-%d'.replace('%d', String(thisTypeParameterCount - 1)) : '0'
        );
    } else {
        genericRegex = '';
    }

    const regexString =
        `^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)%s)$`.replace(
            '%s',
            genericRegex
        );
    const regex = new RegExp(regexString);

    const matcher = typeName.match(regex);
    if (!matcher) {
        throw new UApiSchemaParseError([
            new _SchemaParseFailure(
                path,
                'StringRegexMatchFailed',
                {
                    regex: regexString,
                },
                null
            ),
        ]);
    }

    const standardTypeName = matcher[1];
    if (standardTypeName !== undefined) {
        switch (standardTypeName) {
            case 'boolean':
                return new _UBoolean();
            case 'integer':
                return new _UInteger();
            case 'number':
                return new _UNumber();
            case 'string':
                return new _UString();
            case 'array':
                return new _UArray();
            case 'object':
                return new _UObject();
            default:
                return new _UAny();
        }
    }

    if (thisTypeParameterCount > 0) {
        const genericParameterIndexString = matcher[9];
        if (genericParameterIndexString !== undefined) {
            const genericParameterIndex = parseInt(genericParameterIndexString);
            return new _UGeneric(genericParameterIndex);
        }
    }

    const customTypeName: string = matcher[2]!;

    const index = schemaKeysToIndex[customTypeName];
    if (index === undefined) {
        throw new UApiSchemaParseError([
            new _SchemaParseFailure(
                path,
                'TypeUnknown',
                {
                    name: customTypeName,
                },
                null
            ),
        ]);
    }
    const definition = uApiSchemaPseudoJson[index];

    const typeParameterCountString = matcher[6];
    const typeParameterCount = typeParameterCountString !== undefined ? parseInt(typeParameterCountString) : 0;

    try {
        let type;
        if (customTypeName.startsWith('struct')) {
            type = parseStructType(
                [index],
                definition,
                customTypeName,
                [],
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes
            );
        } else if (customTypeName.startsWith('union')) {
            type = parseUnionType(
                [index],
                definition,
                customTypeName,
                [],
                [],
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes
            );
        } else if (customTypeName.startsWith('fn')) {
            type = parseFunctionType(
                [index],
                definition,
                customTypeName,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes
            );
        } else {
            type = typeExtensions[customTypeName];
            if (type === undefined) {
                throw new UApiSchemaParseError([
                    new _SchemaParseFailure(
                        [index],
                        'TypeExtensionImplementationMissing',
                        {
                            name: customTypeName,
                        },
                        null
                    ),
                ]);
            }
        }

        parsedTypes[customTypeName] = type;

        return type;
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            allParseFailures.push(...e.schemaParseFailures);
            failedTypes.add(customTypeName);
        } else {
            throw e;
        }
        throw new UApiSchemaParseError([]);
    }
}

export function parseStructType(
    path: any[],
    structDefinitionAsPseudoJson: { [key: string]: any },
    schemaKey: string,
    ignoreKeys: string[],
    typeParameterCount: number,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): _UStruct {
    const parseFailures: _SchemaParseFailure[] = [];
    const otherKeys = new Set(Object.keys(structDefinitionAsPseudoJson));
    otherKeys.delete(schemaKey);
    otherKeys.delete('///');
    otherKeys.delete('ignoreIfDuplicate');
    for (const ignoreKey of ignoreKeys) {
        otherKeys.delete(ignoreKey);
    }
    if (otherKeys.size > 0) {
        for (const k of otherKeys) {
            const loopPath = append(path, k);
            parseFailures.push(new _SchemaParseFailure(loopPath, 'ObjectKeyDisallowed', {}, null));
        }
    }
    const thisPath = append(path, schemaKey);
    const defInit = structDefinitionAsPseudoJson[schemaKey];
    let definition: Record<string, any> | undefined = undefined;
    try {
        definition = asMap(defInit);
    } catch (e) {
        const branchParseFailures = getTypeUnexpectedParseFailure(thisPath, defInit, 'Object');
        parseFailures.push(...branchParseFailures);
    }
    if (parseFailures.length > 0 || definition === undefined) {
        throw new UApiSchemaParseError(parseFailures);
    }
    const fields = parseStructFields(
        definition,
        thisPath,
        typeParameterCount,
        uApiSchemaPseudoJson,
        schemaKeysToIndex,
        parsedTypes,
        typeExtensions,
        allParseFailures,
        failedTypes
    );
    return new _UStruct(schemaKey, fields, typeParameterCount);
}

export function parseUnionType(
    path: any[],
    unionDefinitionAsPseudoJson: Record<string, any>,
    schemaKey: string,
    ignoreKeys: string[],
    requiredKeys: string[],
    typeParameterCount: number,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): _UUnion {
    const parseFailures: _SchemaParseFailure[] = [];
    const otherKeys = new Set(Object.keys(unionDefinitionAsPseudoJson));
    otherKeys.delete(schemaKey);
    otherKeys.delete('///');
    for (const ignoreKey of ignoreKeys) {
        otherKeys.delete(ignoreKey);
    }
    if (otherKeys.size > 0) {
        for (const k of otherKeys) {
            const loopPath = append(path, k);
            parseFailures.push(new _SchemaParseFailure(loopPath, 'ObjectKeyDisallowed', {}, null));
        }
    }
    const thisPath = append(path, schemaKey);
    const defInit = unionDefinitionAsPseudoJson[schemaKey];
    let definition: Record<string, any>;
    try {
        definition = asMap(defInit);
    } catch (e) {
        const finalParseFailures = getTypeUnexpectedParseFailure(thisPath, defInit, 'Object');
        parseFailures.push(...finalParseFailures);
        throw new UApiSchemaParseError(parseFailures);
    }
    if (Object.keys(definition).length === 0 && requiredKeys.length === 0) {
        parseFailures.push(new _SchemaParseFailure(thisPath, 'EmptyObjectDisallowed', {}, null));
    } else {
        for (const requiredKey of requiredKeys) {
            if (!definition.hasOwnProperty(requiredKey)) {
                const branchPath = append(thisPath, requiredKey);
                parseFailures.push(new _SchemaParseFailure(branchPath, 'RequiredObjectKeyMissing', {}, null));
            }
        }
    }

    const cases: Record<string, _UStruct> = {};

    for (const [unionCase, value] of Object.entries(definition)) {
        const unionKeyPath = append(thisPath, unionCase);
        const regexString = '^(_?[A-Z][a-zA-Z0-9_]*)$';
        const regex = new RegExp(regexString);
        if (!regex.test(unionCase)) {
            parseFailures.push(
                new _SchemaParseFailure(
                    unionKeyPath,
                    'KeyRegexMatchFailed',
                    {
                        regex: regexString,
                    },
                    null
                )
            );
            continue;
        }
        let unionCaseStruct: Record<string, any>;
        try {
            unionCaseStruct = asMap(value);
        } catch (e) {
            const thisParseFailures = getTypeUnexpectedParseFailure(unionKeyPath, value, 'Object');
            parseFailures.push(...thisParseFailures);
            continue;
        }
        let fields: Record<string, _UFieldDeclaration>;
        try {
            fields = parseStructFields(
                unionCaseStruct,
                unionKeyPath,
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes
            );
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
            continue;
        }
        const unionStruct = new _UStruct(`${schemaKey}.${unionCase}`, fields, typeParameterCount);
        cases[unionCase] = unionStruct;
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }
    return new _UUnion(schemaKey, cases, typeParameterCount);
}

export function parseStructFields(
    referenceStruct: Record<string, any>,
    path: any[],
    typeParameterCount: number,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): Record<string, _UFieldDeclaration> {
    const parseFailures: _SchemaParseFailure[] = [];
    const fields: Record<string, _UFieldDeclaration> = {};
    for (const [structEntryKey, structEntryValue] of Object.entries(referenceStruct)) {
        const fieldDeclaration = structEntryKey;
        for (const existingField in fields) {
            const existingFieldNoOpt = existingField.split('!')[0];
            const fieldNoOpt = fieldDeclaration.split('!')[0];
            if (fieldNoOpt === existingFieldNoOpt) {
                const finalPath = append(path, fieldDeclaration);
                const finalOtherPath = append(path, existingField);
                parseFailures.push(
                    new _SchemaParseFailure(
                        finalPath,
                        'PathCollision',
                        {
                            other: finalOtherPath,
                        },
                        null
                    )
                );
            }
        }
        const typeDeclarationValue = structEntryValue;
        let parsedField: _UFieldDeclaration;
        try {
            parsedField = parseField(
                path,
                fieldDeclaration,
                typeDeclarationValue,
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes
            );
            const fieldName = parsedField.fieldName;
            fields[fieldName] = parsedField;
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }
    return fields;
}

export function parseField(
    path: any[],
    fieldDeclaration: string,
    typeDeclarationValue: any,
    typeParameterCount: number,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): _UFieldDeclaration {
    const regexString = '^(_?[a-z][a-zA-Z0-9_]*)(!)?$';
    const regex = new RegExp(regexString);

    const matcher = fieldDeclaration.match(regex);
    if (!matcher) {
        const finalPath = append(path, fieldDeclaration);
        throw new UApiSchemaParseError([
            new _SchemaParseFailure(
                finalPath,
                'KeyRegexMatchFailed',
                {
                    regex: regexString,
                },
                null
            ),
        ]);
    }

    const fieldName = matcher[0];
    const optional = matcher[2] !== undefined;
    const thisPath = append(path, fieldName);

    let typeDeclarationArray;
    try {
        typeDeclarationArray = asList(typeDeclarationValue);
    } catch (e) {
        throw new UApiSchemaParseError(getTypeUnexpectedParseFailure(thisPath, typeDeclarationValue, 'Array'));
    }

    const typeDeclaration = parseTypeDeclaration(
        thisPath,
        typeDeclarationArray,
        typeParameterCount,
        uApiSchemaPseudoJson,
        schemaKeysToIndex,
        parsedTypes,
        typeExtensions,
        allParseFailures,
        failedTypes
    );

    return { fieldName, typeDeclaration, optional };
}

export function applyErrorToParsedTypes(
    error: _UError,
    parsedTypes: Record<string, _UType>,
    schemaKeysToIndex: Record<string, number>
): void {
    const errorName = error.name;
    const errorIndex = schemaKeysToIndex[errorName];

    const parseFailures: _SchemaParseFailure[] = [];
    for (const [key, parsedType] of Object.entries(parsedTypes)) {
        if (!(parsedType instanceof _UFn)) {
            continue;
        }
        const f = parsedType;

        const fnName = f.name;

        const regex = new RegExp(f.errorsRegex);
        const matcher = errorName.match(regex);
        if (!matcher) {
            continue;
        }

        const fnResult = f.result;
        const fnResultCases = fnResult.cases;
        const errorFnResult = error.errors;
        const errorFnResultCases = errorFnResult.cases;

        for (const [errorResultKey, errorResultField] of Object.entries(errorFnResultCases)) {
            const newKey = errorResultKey;
            if (fnResultCases.hasOwnProperty(newKey)) {
                const otherPathIndex = schemaKeysToIndex[fnName];
                parseFailures.push(
                    new _SchemaParseFailure(
                        [errorIndex, errorName, '->', newKey],
                        'PathCollision',
                        {
                            other: [otherPathIndex, '->', newKey],
                        },
                        null
                    )
                );
            }
            fnResultCases[newKey] = errorResultField;
        }
    }

    if (parseFailures.length !== 0) {
        throw new UApiSchemaParseError(parseFailures);
    }
}

export function parseErrorType(
    errorDefinitionAsParsedJson: Record<string, any>,
    schemaKey: string,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): _UError {
    const index = schemaKeysToIndex[schemaKey];
    const basePath = [index];

    const parseFailures: _SchemaParseFailure[] = [];

    const otherKeys = new Set(Object.keys(errorDefinitionAsParsedJson));

    otherKeys.delete(schemaKey);
    otherKeys.delete('///');

    if (otherKeys.size > 0) {
        for (const k of otherKeys) {
            const loopPath = append(basePath, k);

            parseFailures.push(new _SchemaParseFailure(loopPath, 'ObjectKeyDisallowed', {}, null));
        }
    }

    const defInit = errorDefinitionAsParsedJson[schemaKey];
    const thisPath = append(basePath, schemaKey);

    let def;
    try {
        def = asMap(defInit);
    } catch (e) {
        const thisParseFailures = getTypeUnexpectedParseFailure(thisPath, defInit, 'Object');

        parseFailures.push(...thisParseFailures);
        throw new UApiSchemaParseError(parseFailures);
    }

    const resultSchemaKey = '->';
    const errorPath = append(thisPath, resultSchemaKey);

    if (!def.hasOwnProperty(resultSchemaKey)) {
        parseFailures.push(new _SchemaParseFailure(errorPath, 'RequiredObjectKeyMissing', {}, null));
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    const error = parseUnionType(
        thisPath,
        def,
        resultSchemaKey,
        [],
        [],
        0,
        uApiSchemaPseudoJson,
        schemaKeysToIndex,
        parsedTypes,
        typeExtensions,
        allParseFailures,
        failedTypes
    );

    return { name: schemaKey, errors: error };
}

export function parseHeadersType(
    headersDefinitionAsParsedJson: Record<string, any>,
    schemaKey: string,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): _UHeaders {
    const index = schemaKeysToIndex[schemaKey];
    const path = [index];

    const parseFailures: _SchemaParseFailure[] = [];
    const typeParameterCount = 0;

    let requestHeadersStruct: _UStruct | null = null;
    try {
        requestHeadersStruct = parseStructType(
            path,
            headersDefinitionAsParsedJson,
            schemaKey,
            ['->'],
            typeParameterCount,
            uApiSchemaPseudoJson,
            schemaKeysToIndex,
            parsedTypes,
            typeExtensions,
            allParseFailures,
            failedTypes
        );
        for (const key in requestHeadersStruct.fields) {
            const field = requestHeadersStruct.fields[key];
            if (field.optional) {
                const thisPath = append(append(path, schemaKey), key);
                const regexString = '^(_?[a-z][a-zA-Z0-9_]*)$';
                parseFailures.push(
                    new _SchemaParseFailure(
                        thisPath,
                        'KeyRegexMatchFailed',
                        {
                            regex: regexString,
                        },
                        null
                    )
                );
            }
        }
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    const resultSchemaKey = '->';
    const resPath = append(path, resultSchemaKey);

    let responseHeadersStruct: _UStruct | null = null;
    if (!headersDefinitionAsParsedJson.hasOwnProperty(resultSchemaKey)) {
        parseFailures.push(new _SchemaParseFailure(resPath, 'RequiredObjectKeyMissing', {}, null));
    } else {
        try {
            responseHeadersStruct = parseStructType(
                path,
                headersDefinitionAsParsedJson,
                resultSchemaKey,
                [schemaKey],
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes
            );
            for (const key in responseHeadersStruct.fields) {
                const field = responseHeadersStruct.fields[key];
                if (field.optional) {
                    const thisPath = append(append(path, '->'), key);
                    const regexString = '^(_?[a-z][a-zA-Z0-9_]*)$';
                    parseFailures.push(
                        new _SchemaParseFailure(
                            thisPath,
                            'KeyRegexMatchFailed',
                            {
                                regex: regexString,
                            },
                            null
                        )
                    );
                }
            }
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length !== 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    return new _UHeaders(schemaKey, requestHeadersStruct!.fields, responseHeadersStruct!.fields);
}

export function parseFunctionType(
    path: any[],
    functionDefinitionAsParsedJson: Record<string, any>,
    schemaKey: string,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: Record<string, number>,
    parsedTypes: Record<string, _UType>,
    typeExtensions: Record<string, _UType>,
    allParseFailures: _SchemaParseFailure[],
    failedTypes: Set<string>
): _UFn {
    const parseFailures: _SchemaParseFailure[] = [];
    const typeParameterCount = 0;

    let callType: _UUnion | null = null;
    try {
        const argType = parseStructType(
            path,
            functionDefinitionAsParsedJson,
            schemaKey,
            ['->', 'errors'],
            typeParameterCount,
            uApiSchemaPseudoJson,
            schemaKeysToIndex,
            parsedTypes,
            typeExtensions,
            allParseFailures,
            failedTypes
        );
        callType = new _UUnion(schemaKey, { [schemaKey]: argType }, typeParameterCount);
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    const resultSchemaKey = '->';
    const resPath = append(path, resultSchemaKey);

    let resultType = null;
    if (!functionDefinitionAsParsedJson.hasOwnProperty(resultSchemaKey)) {
        parseFailures.push(new _SchemaParseFailure(resPath, 'RequiredObjectKeyMissing', {}, null));
    } else {
        try {
            resultType = parseUnionType(
                path,
                functionDefinitionAsParsedJson,
                resultSchemaKey,
                Object.keys(functionDefinitionAsParsedJson),
                ['Ok'],
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes
            );
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    const errorsRegexKey = 'errors';
    const regexPath = append(path, errorsRegexKey);

    let errorsRegex = null;
    if (functionDefinitionAsParsedJson.hasOwnProperty(errorsRegexKey) && !schemaKey.startsWith('fn._')) {
        parseFailures.push(new _SchemaParseFailure(regexPath, 'ObjectKeyDisallowed', {}, null));
    } else {
        let errorsRegexInit = functionDefinitionAsParsedJson[errorsRegexKey];
        if (errorsRegexInit === undefined) {
            errorsRegexInit = '^errors\\..*$';
        }
        try {
            errorsRegex = asString(errorsRegexInit);
        } catch (e) {
            const thisParseFailures = getTypeUnexpectedParseFailure(regexPath, errorsRegexInit, 'String');

            parseFailures.push(...thisParseFailures);
        }
    }

    if (parseFailures.length !== 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    return new _UFn(schemaKey, callType!, resultType!, errorsRegex);
}

export function newUApiSchema(uApiSchemaJson: string, typeExtensions: Record<string, _UType>): UApiSchema {
    let uApiSchemaPseudoJsonInit: any;
    try {
        uApiSchemaPseudoJsonInit = JSON.parse(uApiSchemaJson);
    } catch (e) {
        throw new UApiSchemaParseError([new _SchemaParseFailure([], 'JsonInvalid', {}, null)], e as Error);
    }

    let uApiSchemaPseudoJson: Array<any>;
    try {
        uApiSchemaPseudoJson = asList(uApiSchemaPseudoJsonInit);
    } catch (e) {
        const thisParseFailures = getTypeUnexpectedParseFailure([], uApiSchemaPseudoJsonInit, 'Array');
        throw new UApiSchemaParseError(thisParseFailures, e as Error);
    }

    return parseUApiSchema(uApiSchemaPseudoJson, typeExtensions, 0);
}

export function extendUApiSchema(
    first: UApiSchema,
    secondUApiSchemaJson: string,
    secondTypeExtensions: Record<string, _UType>
): UApiSchema {
    let secondUApiSchemaPseudoJsonInit: any;
    try {
        secondUApiSchemaPseudoJsonInit = JSON.parse(secondUApiSchemaJson);
    } catch (e) {
        throw new UApiSchemaParseError([new _SchemaParseFailure([], 'JsonInvalid', {}, null)], e as Error);
    }

    let secondUApiSchemaPseudoJson: any[];
    try {
        secondUApiSchemaPseudoJson = asList(secondUApiSchemaPseudoJsonInit);
    } catch (e) {
        const thisParseFailure: _SchemaParseFailure[] = getTypeUnexpectedParseFailure(
            [],
            secondUApiSchemaPseudoJsonInit,
            'Array'
        );
        throw new UApiSchemaParseError(thisParseFailure, e as Error);
    }

    const firstOriginal: any[] = first.original;
    const firstTypeExtensions: Record<string, _UType> = first.typeExtensions;

    const original: any[] = [...firstOriginal, ...secondUApiSchemaPseudoJson];

    const typeExtensions: Record<string, _UType> = {
        ...firstTypeExtensions,
        ...secondTypeExtensions,
    };

    return parseUApiSchema(original, typeExtensions, firstOriginal.length);
}

export function parseUApiSchema(
    uApiSchemaPseudoJson: any[],
    typeExtensions: Record<string, _UType>,
    pathOffset: number
): UApiSchema {
    const parsedTypes: Record<string, _UType> = {};
    const parseFailures: _SchemaParseFailure[] = [];
    const failedTypes: Set<string> = new Set();
    const schemaKeysToIndex: Record<string, number> = {};
    const schemaKeys: Set<string> = new Set();

    let index = -1;
    for (const definition of uApiSchemaPseudoJson) {
        index += 1;

        const loopPath = [index];

        let def: Record<string, any>;
        try {
            def = asMap(definition);
        } catch (e) {
            const thisParseFailures = getTypeUnexpectedParseFailure(loopPath, definition, 'Object');
            parseFailures.push(...thisParseFailures);
            continue;
        }

        let schemaKey: string;
        try {
            schemaKey = findSchemaKey(def, index);
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
            continue;
        }

        const ignoreIfDuplicate: boolean = def['ignoreIfDuplicate'] ?? false;
        const matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
        if (matchingSchemaKey) {
            if (!ignoreIfDuplicate) {
                const otherPathIndex = schemaKeysToIndex[matchingSchemaKey];
                const finalPath = append(loopPath, schemaKey);

                parseFailures.push(
                    new _SchemaParseFailure(
                        finalPath,
                        'PathCollision',
                        {
                            other: [otherPathIndex, matchingSchemaKey],
                        },
                        null
                    )
                );
            }
            continue;
        }

        schemaKeys.add(schemaKey);
        schemaKeysToIndex[schemaKey] = index;
    }

    if (parseFailures.length > 0) {
        const offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex);
        throw new UApiSchemaParseError(offsetParseFailures);
    }

    const errorKeys: Set<string> = new Set();
    const headerKeys: Set<string> = new Set();
    const rootTypeParameterCount = 0;

    for (const schemaKey of schemaKeys) {
        if (schemaKey.startsWith('info.')) {
            continue;
        } else if (schemaKey.startsWith('errors.')) {
            errorKeys.add(schemaKey);
            continue;
        } else if (schemaKey.startsWith('headers.')) {
            headerKeys.add(schemaKey);
            continue;
        }

        const thisIndex = schemaKeysToIndex[schemaKey];

        try {
            getOrParseType(
                [thisIndex],
                schemaKey,
                rootTypeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                parseFailures,
                failedTypes
            );
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        const offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex);
        throw new UApiSchemaParseError(offsetParseFailures);
    }

    for (const errorKey of errorKeys) {
        const thisIndex: number = schemaKeysToIndex[errorKey]!;
        const def = uApiSchemaPseudoJson[thisIndex] as Map<string, any>;

        try {
            const error = parseErrorType(
                def,
                errorKey,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                parseFailures,
                failedTypes
            );
            applyErrorToParsedTypes(error, parsedTypes, schemaKeysToIndex);
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    const requestHeaders: Record<string, _UFieldDeclaration> = {};
    const responseHeaders: Record<string, _UFieldDeclaration> = {};

    for (const headerKey of headerKeys) {
        const thisIndex: number = schemaKeysToIndex[headerKey]!;
        const def = uApiSchemaPseudoJson[thisIndex] as Map<string, any>;

        try {
            const headersType = parseHeadersType(
                def,
                headerKey,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                parseFailures,
                failedTypes
            );
            Object.assign(requestHeaders, headersType.requestHeaders);
            Object.assign(responseHeaders, headersType.responseHeaders);
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        const offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex);
        throw new UApiSchemaParseError(offsetParseFailures);
    }

    return new UApiSchema(uApiSchemaPseudoJson, parsedTypes, requestHeaders, responseHeaders, typeExtensions);
}

const PACKED_BYTE: number = 17;
const UNDEFINED_BYTE: number = 18;

class MsgpackPacked {
    toString() {
        return 'PACKED';
    }
}
const MSGPACK_PACKED_EXT = {
    Class: MsgpackPacked,
    type: PACKED_BYTE,
    pack(instance: MsgpackPacked) {
        return Buffer.from([]);
    },
    unpack(buffer: Buffer) {
        return new MsgpackPacked();
    },
};
addExtension(MSGPACK_PACKED_EXT);

class MsgpackUndefined {
    toString() {
        return 'UNDEFINED';
    }
}
const MSGPACK_UNDEFINED_EXT = {
    Class: MsgpackUndefined,
    type: UNDEFINED_BYTE,
    pack(instance: MsgpackUndefined) {
        return Buffer.from([]);
    },
    unpack(buffer: Buffer) {
        return new MsgpackUndefined();
    },
};
addExtension(MSGPACK_UNDEFINED_EXT);

class _BinaryPackNode {
    public value: number;
    public nested: Map<number, _BinaryPackNode>;

    constructor(value: number, nested: Map<number, _BinaryPackNode>) {
        this.value = value;
        this.nested = nested;
    }
}

export function packBody(body: Map<any, any>): Map<any, any> {
    const result: Map<any, any> = new Map();

    for (const [key, value] of body.entries()) {
        const packedValue = pack(value);
        result.set(key, packedValue);
    }

    return result;
}

export function pack(value: any): any {
    if (Array.isArray(value)) {
        return packList(value);
    } else if (value instanceof Map) {
        const newMap: Map<any, any> = new Map();

        for (const [key, val] of value.entries()) {
            newMap.set(key, pack(val));
        }

        return newMap;
    } else {
        return value;
    }
}

class CannotPack extends Error {}

export function packList(list: any[]): any[] {
    if (list.length === 0) {
        return list;
    }

    const packedList: any[] = [];
    const header: any[] = [];

    packedList.push(new MsgpackPacked());

    header.push(null);

    packedList.push(header);

    const keyIndexMap: Map<number, _BinaryPackNode> = new Map();
    try {
        for (const e of list) {
            if (e instanceof Map) {
                const row = packMap(e, header, keyIndexMap);

                packedList.push(row);
            } else {
                // This list cannot be packed, abort
                throw new CannotPack();
            }
        }
        return packedList;
    } catch (ex) {
        const newList: any[] = [];
        for (const e of list) {
            newList.push(pack(e));
        }
        return newList;
    }
}

export function packMap(m: Map<any, any>, header: any[], keyIndexMap: Map<number, _BinaryPackNode>): any[] {
    const row: any[] = [];
    for (const [key, value] of m.entries()) {
        if (typeof key === 'string') {
            throw new CannotPack();
        }

        const keyIndex = keyIndexMap.get(key);

        let finalKeyIndex: _BinaryPackNode;
        if (keyIndex === undefined) {
            finalKeyIndex = new _BinaryPackNode(header.length - 1, new Map());

            if (value instanceof Map) {
                header.push([key]);
            } else {
                header.push(key);
            }

            keyIndexMap.set(key, finalKeyIndex);
        } else {
            finalKeyIndex = keyIndex;
        }

        const keyIndexValue: number = finalKeyIndex.value;
        const keyIndexNested: Map<number, _BinaryPackNode> = finalKeyIndex.nested;

        let packedValue: any;
        if (value instanceof Map && value !== null) {
            const nestedHeader: any[] = header[keyIndexValue + 1];
            if (!Array.isArray(nestedHeader)) {
                // No nesting available, so the data structure is inconsistent
                throw new CannotPack();
            }
            packedValue = packMap(value, nestedHeader, keyIndexNested);
        } else {
            if (Array.isArray(header[keyIndexValue + 1])) {
                throw new CannotPack();
            }

            packedValue = pack(value);
        }

        while (row.length < keyIndexValue) {
            row.push(new MsgpackUndefined());
        }

        if (row.length === keyIndexValue) {
            row.push(packedValue);
        } else {
            row[keyIndexValue] = packedValue;
        }
    }
    return row;
}

export function unpackBody(body: Map<any, any>): Map<any, any> {
    const result: Map<any, any> = new Map();

    for (const [key, value] of body.entries()) {
        const unpackedValue = unpack(value);
        result.set(key, unpackedValue);
    }

    return result;
}

export function unpack(value: any): any {
    if (Array.isArray(value)) {
        return unpackList(value);
    } else if (value instanceof Map) {
        const newMap: Map<any, any> = new Map();

        for (const [key, val] of value.entries()) {
            newMap.set(key, unpack(val));
        }

        return newMap;
    } else {
        return value;
    }
}

export function unpackList(list: any[]): any[] {
    if (list.length === 0) {
        return list;
    }

    if (!(list[0] instanceof MsgpackPacked)) {
        const newList: any[] = [];
        for (const e of list) {
            newList.push(unpack(e));
        }
        return newList;
    }

    const unpackedList: any[] = [];
    const headers: any[] = list[1];

    for (let i = 2; i < list.length; i += 1) {
        const row: any[] = list[i];
        const m = unpackMap(row, headers);

        unpackedList.push(m);
    }

    return unpackedList;
}

export function unpackMap(row: any[], header: any[]): Map<any, any> {
    const finalMap = new Map<any, any>();

    for (let j = 0; j < row.length; j += 1) {
        const key = header[j + 1];
        const value = row[j];

        if (value instanceof MsgpackUndefined) {
            continue;
        }

        if (Array.isArray(key)) {
            const nestedHeader = key as any[];
            const nestedRow = value as any[];
            const m = unpackMap(nestedRow, nestedHeader);
            const i = nestedHeader[0] as number;
            finalMap.set(i, m);
        } else {
            const unpackedValue = unpack(value);
            finalMap.set(key, unpackedValue);
        }
    }

    return finalMap;
}

function convertMapsToObjects(value: any): any {
    if (value instanceof Map) {
        const newObj: Record<string, any> = {};
        for (const [key, val] of value.entries()) {
            newObj[key] = convertMapsToObjects(val);
        }
        return newObj;
    } else if (Array.isArray(value)) {
        const newList: any[] = [];
        for (const val of value) {
            const newVal = convertMapsToObjects(val);
            newList.push(newVal);
        }
        return newList;
    } else if (typeof value == 'object' && value !== null) {
        const newObj: Record<string, any> = {};
        for (const [key, val] of Object.entries(value)) {
            newObj[key] = convertMapsToObjects(val);
        }
    } else {
        return value;
    }
}

export function serverBinaryEncode(message: any[], binaryEncoder: _BinaryEncoding): any[] {
    const headers: Record<string, any> = message[0];
    const messageBody: Record<string, any> = message[1];
    const clientKnownBinaryChecksums = headers['_clientKnownBinaryChecksums'] as number[];
    delete headers['_clientKnownBinaryChecksums'];

    if (!clientKnownBinaryChecksums || !clientKnownBinaryChecksums.includes(binaryEncoder.checksum)) {
        headers['_enc'] = binaryEncoder.encodeMap;
    }

    headers['_bin'] = [binaryEncoder.checksum];
    const encodedMessageBody = encodeBody(messageBody, binaryEncoder);

    let finalEncodedMessageBody: Map<string, any>;
    if (headers['_pac'] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    return [headers, finalEncodedMessageBody];
}

export function serverBinaryDecode(message: any[], binaryEncoder: _BinaryEncoding): any[] {
    const headers = message[0] as Map<string, any>;
    const encodedMessageBody = message[1] as Map<any, any>;
    const clientKnownBinaryChecksums = headers.get('_bin') as number[];
    const binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums[0];

    if (binaryChecksumUsedByClientOnThisMessage !== binaryEncoder.checksum) {
        throw new _BinaryEncoderUnavailableError();
    }

    let finalEncodedMessageBody: Map<any, any>;
    if (headers.get('_pac') === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}

export function clientBinaryEncode(
    message: any[],
    recentBinaryEncoders: Map<number, _BinaryEncoding>,
    binaryChecksumStrategy: ClientBinaryStrategy
): any[] {
    const headers = message[0] as Record<string, any>;
    const messageBody = message[1] as Record<string, any>;
    const forceSendJson = headers['_forceSendJson'];

    headers['_bin'] = binaryChecksumStrategy.getCurrentChecksums();

    if (forceSendJson === true) {
        throw new _BinaryEncoderUnavailableError();
    }

    if (recentBinaryEncoders.size > 1) {
        throw new _BinaryEncoderUnavailableError();
    }

    const binaryEncoder = [...recentBinaryEncoders.values()][0];

    if (!binaryEncoder) {
        throw new _BinaryEncoderUnavailableError();
    }

    const encodedMessageBody = encodeBody(messageBody, binaryEncoder);

    let finalEncodedMessageBody: Map<any, any>;
    if (headers['_pac'] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    return [headers, finalEncodedMessageBody];
}

export function clientBinaryDecode(
    message: any[],
    recentBinaryEncoders: Map<number, _BinaryEncoding>,
    binaryChecksumStrategy: ClientBinaryStrategy
): any[] {
    const headers = message[0] as Map<string, any>;
    const encodedMessageBody = message[1] as Map<any, any>;
    const binaryChecksums = headers.get('_bin') as number[];
    const binaryChecksum = binaryChecksums[0]!;

    if (headers.has('_enc')) {
        const binaryEncoding = headers.get('_enc') as Map<string, number>;
        const newBinaryEncoder = new _BinaryEncoding(binaryEncoding, binaryChecksum);
        recentBinaryEncoders.set(binaryChecksum, newBinaryEncoder);
    }

    binaryChecksumStrategy.update(binaryChecksum);
    const newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

    for (const [key, value] of recentBinaryEncoders) {
        if (!newCurrentChecksumStrategy.includes(key)) {
            recentBinaryEncoders.delete(key);
        }
    }

    const binaryEncoder = recentBinaryEncoders.get(binaryChecksum)!;

    let finalEncodedMessageBody: Map<any, any>;
    if (headers.get('_pac') === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}

export function encodeBody(messageBody: Record<string, any>, binaryEncoder: _BinaryEncoding): Map<any, any> {
    return encodeKeys(messageBody, binaryEncoder);
}

export function decodeBody(encodedMessageBody: Map<any, any>, binaryEncoder: _BinaryEncoding): Record<string, any> {
    return decodeKeys(encodedMessageBody, binaryEncoder);
}

export function encodeKeys(given: any, binaryEncoder: _BinaryEncoding): any {
    if (given === null || given === undefined) {
        return given;
    } else if (typeof given === 'object' && !Array.isArray(given)) {
        const newMap = new Map<any, any>();

        for (const [key, value] of Object.entries(given)) {
            const finalKey = binaryEncoder.encodeMap.has(key) ? binaryEncoder.encodeMap.get(key) : key;
            const encodedValue = encodeKeys(value, binaryEncoder);

            newMap.set(finalKey, encodedValue);
        }

        return newMap;
    } else if (Array.isArray(given)) {
        return given.map((value) => encodeKeys(value, binaryEncoder));
    } else {
        return given;
    }
}

export function decodeKeys(given: any, binaryEncoder: _BinaryEncoding): any {
    if (given instanceof Map) {
        const newMap: { [key: string]: any } = {};

        for (const [key, value] of given.entries()) {
            const finalKey = typeof key === 'string' ? key : binaryEncoder.decodeMap.get(key);

            if (finalKey === undefined) {
                throw new _BinaryEncodingMissing(key);
            }

            const decodedValue = decodeKeys(value, binaryEncoder);
            newMap[finalKey] = decodedValue;
        }

        return newMap;
    } else if (Array.isArray(given)) {
        return given.map((value) => decodeKeys(value, binaryEncoder));
    } else {
        return given;
    }
}

export function constructBinaryEncoding(uApiSchema: UApiSchema): _BinaryEncoding {
    const allKeys: Set<string> = new Set<string>();
    for (const [key, value] of Object.entries(uApiSchema.parsed)) {
        allKeys.add(key);

        if (value instanceof _UStruct) {
            const structFields: Record<string, _UFieldDeclaration> = value.fields;
            Object.keys(structFields).forEach((structFieldKey) => {
                allKeys.add(structFieldKey);
            });
        } else if (value instanceof _UUnion) {
            const unionCases: Record<string, _UStruct> = value.cases;
            for (const [caseKey, struct] of Object.entries(unionCases)) {
                allKeys.add(caseKey);
                const structFields: Record<string, _UFieldDeclaration> = struct.fields;
                Object.keys(structFields).forEach((structFieldKey) => {
                    allKeys.add(structFieldKey);
                });
            }
        } else if (value instanceof _UFn) {
            const fnCall: _UUnion = value.call;
            const fnCallCases: Record<string, _UStruct> = fnCall.cases;
            const fnResult: _UUnion = value.result;
            const fnResultCases: Record<string, _UStruct> = fnResult.cases;

            for (const [callKey, callStruct] of Object.entries(fnCallCases)) {
                allKeys.add(callKey);
                const structFields: Record<string, _UFieldDeclaration> = callStruct.fields;
                Object.keys(structFields).forEach((structFieldKey) => {
                    allKeys.add(structFieldKey);
                });
            }

            for (const [resultKey, resultStruct] of Object.entries(fnResultCases)) {
                allKeys.add(resultKey);
                const structFields: Record<string, _UFieldDeclaration> = resultStruct.fields;
                Object.keys(structFields).forEach((structFieldKey) => {
                    allKeys.add(structFieldKey);
                });
            }
        }
    }

    const sortedAllKeys = Array.from(allKeys).sort();

    let i = 0;
    const binaryEncodingMap = new Map<string, number>();
    sortedAllKeys.forEach((key) => {
        binaryEncodingMap.set(key, i);
        i += 1;
    });
    const finalString = Array.from(sortedAllKeys).join('\n');

    const checksum = createChecksum(finalString);
    return new _BinaryEncoding(binaryEncodingMap, checksum);
}

export function createChecksum(value: string): number {
    const checksum = crc32.str(value);
    // Convert the checksum to a signed 32-bit integer
    return checksum >>> 0; // Using zero-fill right shift to convert to unsigned
}

export function serialize(message: Message, binaryEncoder: _BinaryEncoder, serializer: SerializationImpl): Uint8Array {
    const headers: Record<string, any> = message.header;

    let serializeAsBinary = false;
    if (headers.hasOwnProperty('_binary')) {
        serializeAsBinary = headers['_binary'] === true;
        delete headers['_binary'];
    }

    const messageAsPseudoJson: any[] = [message.header, message.body];

    try {
        if (serializeAsBinary) {
            try {
                const encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                return serializer.toMsgPack(encodedMessage);
            } catch (e) {
                console.log(e);
                // We can still submit as json
                return serializer.toJson(messageAsPseudoJson);
            }
        } else {
            return serializer.toJson(messageAsPseudoJson);
        }
    } catch (e) {
        throw new SerializationError(e as Error);
    }
}

export function deserialize(
    messageBytes: Uint8Array,
    serializer: SerializationImpl,
    binaryEncoder: _BinaryEncoder
): Message {
    let messageAsPseudoJson: any;
    let isMsgPack: boolean;

    try {
        if (messageBytes[0] === 0x92) {
            // MsgPack
            isMsgPack = true;
            messageAsPseudoJson = serializer.fromMsgPack(messageBytes);
        } else {
            isMsgPack = false;
            messageAsPseudoJson = serializer.fromJson(messageBytes);
        }
    } catch (e) {
        throw new _InvalidMessage(e as Error);
    }

    let messageAsPseudoJsonList: any[];
    try {
        messageAsPseudoJsonList = asList(messageAsPseudoJson);
    } catch (e) {
        throw new _InvalidMessage(e);
    }

    if (messageAsPseudoJsonList.length !== 2) {
        throw new _InvalidMessage(new Error(`Expected size of 2 but was ${messageAsPseudoJsonList.length}`));
    }

    let finalMessageAsPseudoJsonList: any[];
    if (isMsgPack) {
        finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
    } else {
        finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
    }

    let headers: Record<string, any>;
    let body: Record<string, any>;

    try {
        headers = asMap(finalMessageAsPseudoJsonList[0]);
    } catch (e) {
        throw new _InvalidMessage(e);
    }

    try {
        body = asMap(finalMessageAsPseudoJsonList[1]);
        if (Object.keys(body).length !== 1) {
            throw new _InvalidMessageBody();
        } else {
            const givenPayload = [...Object.values(body)][0];
            if (givenPayload === undefined || typeof givenPayload !== 'object' || Array.isArray(givenPayload)) {
                throw new _InvalidMessageBody();
            }
        }
    } catch (e) {
        if (e instanceof _InvalidMessageBody) {
            throw e;
        }
        throw new _InvalidMessage(e);
    }

    return new Message(headers, body);
}

export function getType(value: any): string {
    if (value === null) {
        return 'Null';
    } else if (typeof value === 'boolean') {
        return 'Boolean';
    } else if (typeof value === 'number') {
        return 'Number';
    } else if (typeof value === 'string') {
        return 'String';
    } else if (Array.isArray(value)) {
        return 'Array';
    } else if (typeof value === 'object') {
        return 'Object';
    } else {
        return 'Unknown';
    }
}

export function getTypeUnexpectedValidationFailure(
    path: any[],
    value: any,
    expectedType: string
): _ValidationFailure[] {
    const actualType = getType(value);
    const data = {
        actual: { [actualType]: {} },
        expected: { [expectedType]: {} },
    };
    return [new _ValidationFailure(path, 'TypeUnexpected', data)];
}

export function validateHeaders(
    headers: { [key: string]: any },
    parsedRequestHeaders: Record<string, _UFieldDeclaration>,
    functionType: _UFn
): _ValidationFailure[] {
    const validationFailures: _ValidationFailure[] = [];

    for (const [header, headerValue] of Object.entries(headers)) {
        const field = parsedRequestHeaders[header];
        if (field) {
            const thisValidationFailures = field.typeDeclaration.validate(
                headerValue,
                undefined,
                functionType.name,
                []
            );
            const thisValidationFailuresPath: _ValidationFailure[] = thisValidationFailures.map((e) => {
                return {
                    path: prepend(header, e.path),
                    reason: e.reason,
                    data: e.data,
                };
            });
            validationFailures.push(...thisValidationFailuresPath);
        }
    }

    return validationFailures;
}

export function validateValueOfType(
    value: any,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    generics: _UTypeDeclaration[],
    thisType: _UType,
    nullable: boolean,
    typeParameters: _UTypeDeclaration[]
): _ValidationFailure[] {
    if (value === null || value === undefined) {
        const isNullable = thisType instanceof _UGeneric ? generics[thisType.index]!.nullable : nullable;
        if (!isNullable) {
            return getTypeUnexpectedValidationFailure([], value, thisType.getName(generics));
        } else {
            return [];
        }
    } else {
        return thisType.validate(value, select, fn, typeParameters, generics);
    }
}

export function generateRandomValueOfType(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    generics: _UTypeDeclaration[],
    randomGenerator: _RandomGenerator,
    thisType: _UType,
    nullable: boolean,
    typeParameters: _UTypeDeclaration[]
): any {
    if (nullable && !useBlueprintValue && randomGenerator.nextBoolean()) {
        return null;
    } else {
        return thisType.generateRandomValue(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            generics,
            randomGenerator
        );
    }
}

export function generateRandomAny(randomGenerator: _RandomGenerator): any {
    const selectType = randomGenerator.nextIntWithCeiling(3);
    if (selectType === 0) {
        return randomGenerator.nextBoolean();
    } else if (selectType === 1) {
        return randomGenerator.nextInt();
    } else {
        return randomGenerator.nextString();
    }
}

export function validateBoolean(value: any): _ValidationFailure[] {
    if (typeof value === 'boolean') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, _BOOLEAN_NAME);
    }
}

export function generateRandomBoolean(
    blueprintValue: any,
    useBlueprintValue: boolean,
    randomGenerator: _RandomGenerator
): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return randomGenerator.nextBoolean();
    }
}

const NUMBER_TRUNCATED = 'NumberTruncated';

export function validateInteger(value: any): _ValidationFailure[] {
    if (typeof value === 'number' && Number.isInteger(value)) {
        if (value === 9223372036854776000 || value === -9223372036854776000) {
            return [
                new _ValidationFailure([], 'NumberOutOfRange', {}),
                new _ValidationFailure([], NUMBER_TRUNCATED, {}),
            ];
        }
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, _INTEGER_NAME);
    }
}

export function generateRandomInteger(
    blueprintValue: any,
    useBlueprintValue: boolean,
    randomGenerator: _RandomGenerator
): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return randomGenerator.nextInt();
    }
}

export function validateNumber(value: any): Array<_ValidationFailure> {
    if (typeof value === 'number') {
        if ((Number.isInteger(value) && value === 9223372036854776000) || value === -9223372036854776000) {
            return [
                new _ValidationFailure([], 'NumberOutOfRange', {}),
                new _ValidationFailure([], NUMBER_TRUNCATED, {}),
            ];
        }
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, _NUMBER_NAME);
    }
}

export function generateRandomNumber(
    blueprintValue: any,
    useBlueprintValue: boolean,
    randomGenerator: _RandomGenerator
): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return randomGenerator.nextDouble();
    }
}

export function validateString(value: any): Array<_ValidationFailure> {
    if (typeof value === 'string') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, _STRING_NAME);
    }
}

export function generateRandomString(
    blueprintValue: any,
    useBlueprintValue: boolean,
    randomGenerator: _RandomGenerator
): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return randomGenerator.nextString();
    }
}

export function validateArray(
    value: any,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: Array<_UTypeDeclaration>,
    generics: Array<_UTypeDeclaration>
): Array<_ValidationFailure> {
    if (Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0]!;
        const validationFailures: Array<_ValidationFailure> = [];
        for (let i = 0; i < value.length; i++) {
            const element = value[i];
            const nestedValidationFailures = nestedTypeDeclaration.validate(element, select, fn, generics);
            const index = i;
            const nestedValidationFailuresWithPath: Array<_ValidationFailure> = nestedValidationFailures.map((f) => {
                const finalPath = prepend(index, f.path);
                return {
                    path: finalPath,
                    reason: f.reason,
                    data: f.data,
                };
            });
            validationFailures.push(...nestedValidationFailuresWithPath);
        }
        return validationFailures;
    } else {
        return getTypeUnexpectedValidationFailure([], value, _ARRAY_NAME);
    }
}

export function generateRandomArray(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: Array<_UTypeDeclaration>,
    generics: Array<_UTypeDeclaration>,
    randomGenerator: _RandomGenerator
): any {
    const nestedTypeDeclaration = typeParameters[0]!;
    if (useBlueprintValue) {
        const startingArray = blueprintValue as Array<any>;
        const array: Array<any> = [];
        for (const startingArrayValue of startingArray) {
            const value = nestedTypeDeclaration.generateRandomValue(
                startingArrayValue,
                true,
                includeOptionalFields,
                randomizeOptionalFields,
                generics,
                randomGenerator
            );
            array.push(value);
        }
        return array;
    } else {
        const length = randomGenerator.nextCollectionLength();
        const array: Array<any> = [];
        for (let i = 0; i < length; i++) {
            const value = nestedTypeDeclaration.generateRandomValue(
                null,
                false,
                includeOptionalFields,
                randomizeOptionalFields,
                generics,
                randomGenerator
            );
            array.push(value);
        }
        return array;
    }
}

export function validateObject(
    value: any,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: Array<_UTypeDeclaration>,
    generics: Array<_UTypeDeclaration>
): Array<_ValidationFailure> {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0]!;
        const validationFailures: Array<_ValidationFailure> = [];
        for (const key in value) {
            const nestedValidationFailures = nestedTypeDeclaration.validate(value[key], select, fn, generics);
            const nestedValidationFailuresWithPath: Array<_ValidationFailure> = nestedValidationFailures.map((f) => {
                const thisPath = prepend(key, f.path);
                return {
                    path: thisPath,
                    reason: f.reason,
                    data: f.data,
                };
            });
            validationFailures.push(...nestedValidationFailuresWithPath);
        }
        return validationFailures;
    } else {
        return getTypeUnexpectedValidationFailure([], value, _OBJECT_NAME);
    }
}

export function generateRandomObject(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: Array<_UTypeDeclaration>,
    generics: Array<_UTypeDeclaration>,
    randomGenerator: _RandomGenerator
): any {
    const nestedTypeDeclaration = typeParameters[0]!;
    if (useBlueprintValue) {
        const startingObj = blueprintValue as Record<string, any>;
        const obj: Record<string, any> = {};
        for (const [key, startingObjValue] of Object.entries(startingObj)) {
            const value = nestedTypeDeclaration.generateRandomValue(
                startingObjValue,
                true,
                includeOptionalFields,
                randomizeOptionalFields,
                generics,
                randomGenerator
            );
            obj[key] = value;
        }
        return obj;
    } else {
        const length = randomGenerator.nextCollectionLength();
        const obj: Record<string, any> = {};
        for (let i = 0; i < length; i++) {
            const key = randomGenerator.nextString();
            const value = nestedTypeDeclaration.generateRandomValue(
                null,
                false,
                includeOptionalFields,
                randomizeOptionalFields,
                generics,
                randomGenerator
            );
            obj[key] = value;
        }
        return obj;
    }
}

export function validateStruct(
    value: any,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: Array<_UTypeDeclaration>,
    generics: Array<_UTypeDeclaration>,
    name: string,
    fields: Record<string, _UFieldDeclaration>
): Array<_ValidationFailure> {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const selectedFields = select?.[name];
        return validateStructFields(fields, selectedFields, value, select, fn, typeParameters);
    } else {
        return getTypeUnexpectedValidationFailure([], value, _STRUCT_NAME);
    }
}

export function validateStructFields(
    fields: Record<string, _UFieldDeclaration>,
    selectedFields: string[] | undefined,
    actualStruct: Record<string, any>,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: Array<_UTypeDeclaration>
): Array<_ValidationFailure> {
    const validationFailures: Array<_ValidationFailure> = [];
    const missingFields: Array<string> = [];
    for (const [fieldName, fieldDeclaration] of Object.entries(fields)) {
        const isOptional = fieldDeclaration.optional;
        const isOmittedBySelect = selectedFields && !selectedFields.includes(fieldName);
        if (!actualStruct.hasOwnProperty(fieldName) && !isOptional && !isOmittedBySelect) {
            missingFields.push(fieldName);
        }
    }
    for (const missingField of missingFields) {
        const validationFailure: _ValidationFailure = new _ValidationFailure(
            [missingField],
            'RequiredObjectKeyMissing',
            {}
        );
        validationFailures.push(validationFailure);
    }
    for (const [fieldName, fieldValue] of Object.entries(actualStruct)) {
        const referenceField = fields[fieldName];
        if (!referenceField) {
            const validationFailure: _ValidationFailure = new _ValidationFailure(
                [fieldName],
                'ObjectKeyDisallowed',
                {}
            );
            validationFailures.push(validationFailure);
            continue;
        }
        const refFieldTypeDeclaration = referenceField.typeDeclaration;
        const nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, select, fn, typeParameters);
        const nestedValidationFailuresWithPath: _ValidationFailure[] = nestedValidationFailures.map((f) => {
            const thisPath = prepend(fieldName, f.path);
            return {
                path: thisPath,
                reason: f.reason,
                data: f.data,
            };
        });
        validationFailures.push(...nestedValidationFailuresWithPath);
    }
    return validationFailures;
}

export function generateRandomStruct(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: _UTypeDeclaration[],
    generics: _UTypeDeclaration[],
    randomGenerator: _RandomGenerator,
    fields: Record<string, _UFieldDeclaration>
): any {
    if (useBlueprintValue) {
        const startingStructValue = blueprintValue as Record<string, any>;
        return constructRandomStruct(
            fields,
            startingStructValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            randomGenerator
        );
    } else {
        return constructRandomStruct(
            fields,
            {},
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            randomGenerator
        );
    }
}

export function constructRandomStruct(
    referenceStruct: Record<string, _UFieldDeclaration>,
    startingStruct: Record<string, any>,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: _UTypeDeclaration[],
    randomGenerator: _RandomGenerator
): Record<string, any> {
    const sortedReferenceStruct = Array.from(Object.entries(referenceStruct)).sort((e1, e2) => {
        const a = e1[0];
        const b = e2[0];
        for (let i = 0; i < Math.min(a.length, b.length); i++) {
            const charCodeA = a.charCodeAt(i);
            const charCodeB = b.charCodeAt(i);
            if (charCodeA !== charCodeB) {
                // If the characters are different, return the comparison result
                // where lowercase letters are considered greater than uppercase letters
                return charCodeA - charCodeB;
            }
        }
        // If one string is a prefix of the other, the shorter string comes first
        return a.length - b.length;
    });
    const obj: Record<string, any> = {};

    for (const [fieldName, fieldDeclaration] of sortedReferenceStruct) {
        const blueprintValue = startingStruct[fieldName];
        const useBlueprintValue = startingStruct.hasOwnProperty(fieldName);
        const typeDeclaration = fieldDeclaration.typeDeclaration;

        let value: any;
        if (useBlueprintValue) {
            value = typeDeclaration.generateRandomValue(
                blueprintValue,
                useBlueprintValue,
                includeOptionalFields,
                randomizeOptionalFields,
                typeParameters,
                randomGenerator
            );
        } else {
            if (!fieldDeclaration.optional) {
                value = typeDeclaration.generateRandomValue(
                    null,
                    false,
                    includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters,
                    randomGenerator
                );
            } else {
                console.log(
                    `includeOptionalFields: ${includeOptionalFields} randomizeOptionalFields: ${randomizeOptionalFields}`
                );
                console.log(`stack: ${new Error().stack})}`);
                if (!includeOptionalFields || (randomizeOptionalFields && randomGenerator.nextBoolean())) {
                    continue;
                }
                value = typeDeclaration.generateRandomValue(
                    null,
                    false,
                    includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters,
                    randomGenerator
                );
            }
        }

        obj[fieldName] = value;
    }

    return obj;
}

export function unionEntry(union: Record<string, any>): [string, any] {
    const result = Array.from(Object.entries(union))[0];
    if (result == undefined) {
        throw new Error('Invalid union');
    }
    return result;
}

export function validateUnion(
    value: any,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: _UTypeDeclaration[],
    generics: _UTypeDeclaration[],
    name: string,
    cases: Record<string, _UStruct>
): _ValidationFailure[] {
    if (typeof value == 'object' && !Array.isArray(value)) {
        let selectedCases: Record<string, any> | undefined;
        if (name.startsWith('fn.')) {
            selectedCases = { [name]: select?.[name] };
        } else {
            selectedCases = select?.[name];
        }
        return validateUnionCases(cases, selectedCases, value, select, fn, typeParameters);
    } else {
        return getTypeUnexpectedValidationFailure([], value, _UNION_NAME);
    }
}

export function validateUnionCases(
    referenceCases: Record<string, _UStruct>,
    selectedCases: Record<string, any> | undefined,
    actual: Record<string, any>,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: _UTypeDeclaration[]
): _ValidationFailure[] {
    const size = Object.keys(actual).length;
    if (size !== 1) {
        return [
            {
                path: [],
                reason: 'ObjectSizeUnexpected',
                data: { actual: size, expected: 1 },
            },
        ];
    }

    const entry = unionEntry(actual);
    const unionTarget = entry[0];
    const unionPayload = entry[1];

    const referenceStruct = referenceCases[unionTarget];
    if (!referenceStruct) {
        return [
            {
                path: [unionTarget],
                reason: 'ObjectKeyDisallowed',
                data: {},
            },
        ];
    }

    if (typeof unionPayload === 'object' && !Array.isArray(unionPayload)) {
        const nestedValidationFailures = validateUnionStruct(
            referenceStruct,
            unionTarget,
            unionPayload,
            selectedCases,
            select,
            fn,
            typeParameters
        );

        return nestedValidationFailures.map((f) => ({
            path: [unionTarget, ...f.path],
            reason: f.reason,
            data: f.data,
        }));
    } else {
        return getTypeUnexpectedValidationFailure([unionTarget], unionPayload, 'Object');
    }
}

export function validateUnionStruct(
    unionStruct: _UStruct,
    unionCase: string,
    actual: Record<string, any>,
    selectedCases: Record<string, any> | undefined,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: _UTypeDeclaration[]
): _ValidationFailure[] {
    const selectedFields = selectedCases?.[unionCase];
    return validateStructFields(unionStruct.fields, selectedFields, actual, select, fn, typeParameters);
}

export function generateRandomUnion(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: _UTypeDeclaration[],
    generics: _UTypeDeclaration[],
    randomGenerator: _RandomGenerator,
    cases: Record<string, _UStruct>
): any {
    if (useBlueprintValue) {
        const startingUnionCase = blueprintValue as Map<string, any>;
        return constructRandomUnion(
            cases,
            startingUnionCase,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            randomGenerator
        );
    } else {
        return constructRandomUnion(
            cases,
            {},
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            randomGenerator
        );
    }
}

export function constructRandomUnion(
    unionCasesReference: Record<string, _UStruct>,
    startingUnion: Record<string, any>,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: _UTypeDeclaration[],
    randomGenerator: _RandomGenerator
): Record<string, any> {
    if (Object.keys(startingUnion).length !== 0) {
        const entry = unionEntry(startingUnion);
        const unionCase = entry[0];
        const unionStructType = unionCase ? unionCasesReference[unionCase] : null;
        const unionStartingStruct: Record<string, any> = startingUnion[unionCase];

        if (unionCase && unionStructType && unionStartingStruct) {
            return {
                [unionCase]: constructRandomStruct(
                    unionStructType.fields,
                    unionStartingStruct,
                    includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters,
                    randomGenerator
                ),
            };
        }
    } else {
        const sortedUnionCasesReference = Array.from(Object.entries(unionCasesReference)).sort((e1, e2) =>
            e1[0].localeCompare(e2[0])
        );
        const randomIndex = randomGenerator.nextIntWithCeiling(sortedUnionCasesReference.length - 1);
        const unionEntry = sortedUnionCasesReference[randomIndex];
        const unionCase = unionEntry ? unionEntry[0] : null;
        const unionData = unionEntry ? unionEntry[1] : null;

        return {
            [unionCase]: constructRandomStruct(
                unionData.fields,
                {},
                includeOptionalFields,
                randomizeOptionalFields,
                typeParameters,
                randomGenerator
            ),
        };
    }
}

export function generateRandomFn(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: _UTypeDeclaration[],
    generics: _UTypeDeclaration[],
    randomGenerator: _RandomGenerator,
    callCases: Record<string, _UStruct>
): any {
    if (useBlueprintValue) {
        const startingFnValue = blueprintValue as Record<string, any>;
        return constructRandomUnion(
            callCases,
            startingFnValue,
            includeOptionalFields,
            randomizeOptionalFields,
            [],
            randomGenerator
        );
    } else {
        return constructRandomUnion(callCases, {}, includeOptionalFields, randomizeOptionalFields, [], randomGenerator);
    }
}

export function validateSelect(
    givenObj: any,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: _UTypeDeclaration[],
    generics: _UTypeDeclaration[],
    types: Record<string, _UType>
): _ValidationFailure[] {
    let selectStructFieldsHeader: Record<string, any>;
    try {
        selectStructFieldsHeader = asMap(givenObj);
    } catch (e) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }

    const validationFailures: _ValidationFailure[] = [];
    const functionType: _UFn = types[fn] as _UFn;

    for (const [typeName, selectValue] of Object.entries(selectStructFieldsHeader)) {
        let typeReference: _UType | undefined;
        if (typeName === '->') {
            typeReference = functionType.result;
        } else {
            typeReference = types[typeName];
        }

        if (!typeReference) {
            validationFailures.push(new _ValidationFailure([typeName], 'ObjectKeyDisallowed', {}));
            continue;
        }

        if (typeReference instanceof _UUnion) {
            let unionCases: Record<string, any>;
            try {
                unionCases = asMap(selectValue);
            } catch (e) {
                validationFailures.push(...getTypeUnexpectedValidationFailure([typeName], selectValue, 'Object'));
                continue;
            }

            for (const [unionCase, selectedCaseStructFields] of Object.entries(unionCases)) {
                const structRef = typeReference.cases[unionCase];
                if (!structRef) {
                    validationFailures.push(new _ValidationFailure([typeName, unionCase], 'ObjectKeyDisallowed', {}));
                    continue;
                }

                const nestedValidationFailures = validateSelectStruct(
                    structRef,
                    [typeName, unionCase],
                    selectedCaseStructFields
                );
                validationFailures.push(...nestedValidationFailures);
            }
        } else if (typeReference instanceof _UFn) {
            const fnCall = typeReference.call;
            const fnCallCases = fnCall.cases;
            const fnName = typeReference.name;
            const argStruct = fnCallCases[fnName]!;
            const nestedValidationFailures = validateSelectStruct(argStruct, [typeName], selectValue);
            validationFailures.push(...nestedValidationFailures);
        } else {
            const structRef = typeReference as _UStruct;
            const nestedValidationFailures = validateSelectStruct(structRef, [typeName], selectValue);
            validationFailures.push(...nestedValidationFailures);
        }
    }

    return validationFailures;
}

export function validateSelectStruct(
    structReference: _UStruct,
    basePath: Array<string | number>,
    selectedFields: any
): _ValidationFailure[] {
    const validationFailures: _ValidationFailure[] = [];

    let fields: string[];
    try {
        fields = asList(selectedFields);
    } catch (e) {
        return getTypeUnexpectedValidationFailure(basePath, selectedFields, 'Array');
    }

    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        let stringField: string;
        try {
            stringField = asString(field);
        } catch (e) {
            const thisPath = append(basePath, i);
            validationFailures.push(...getTypeUnexpectedValidationFailure(thisPath, field, 'String'));
            continue;
        }
        if (!(stringField in structReference.fields)) {
            const thisPath = append(basePath, i);
            validationFailures.push(new _ValidationFailure(thisPath, 'ObjectKeyDisallowed', {}));
        }
    }

    return validationFailures;
}

export function validateMockCall(
    givenObj: any,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: _UTypeDeclaration[],
    generics: _UTypeDeclaration[],
    types: Record<string, _UType>
): _ValidationFailure[] {
    let givenMap: Record<string, any>;
    try {
        givenMap = asMap(givenObj);
    } catch (e) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }

    const regexString = '^fn\\..*$';

    const matches = [...Object.keys(givenMap)].filter((k: string) => k.match(regexString));
    if (matches.length !== 1) {
        return [
            {
                path: [],
                reason: 'ObjectKeyRegexMatchCountUnexpected',
                data: {
                    regex: regexString,
                    actual: matches.length,
                    expected: 1,
                },
            },
        ];
    }

    const functionName = matches[0]!;
    const functionDef: _UFn = types[functionName]! as _UFn;
    const input = givenMap[functionName];

    const functionDefCall = functionDef?.call;
    const functionDefName = functionDef?.name;
    const functionDefCallCases = functionDefCall?.cases;

    const inputFailures = functionDefCallCases?.[functionDefName]?.validate(input, select, fn, [], []);

    if (!inputFailures) return [];

    return inputFailures
        .filter((f) => f.reason !== 'RequiredObjectKeyMissing')
        .map((f) => ({
            path: [functionName, ...f.path],
            reason: f.reason,
            data: f.data,
        }));
}

export function validateMockStub(
    givenObj: any,
    select: Record<string, any> | undefined,
    fn: string | undefined,
    typeParameters: _UTypeDeclaration[],
    generics: _UTypeDeclaration[],
    types: Record<string, _UType>
): _ValidationFailure[] {
    const validationFailures: _ValidationFailure[] = [];

    let givenMap: Record<string, any>;
    try {
        givenMap = asMap(givenObj);
    } catch (e) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }

    const regexString = '^fn\\..*$';

    const matches = Object.keys(givenMap).filter((k) => k.match(regexString)) as string[];
    if (matches.length !== 1) {
        return [
            {
                path: [],
                reason: 'ObjectKeyRegexMatchCountUnexpected',
                data: {
                    regex: regexString,
                    actual: matches.length,
                    expected: 1,
                },
            },
        ];
    }

    const functionName = matches[0]!;
    const functionDef = types[functionName] as _UFn;
    const input = givenMap[functionName];

    const functionDefCall = functionDef.call;
    const functionDefName = functionDef.name;
    const functionDefCallCases = functionDefCall.cases;
    const inputFailures = functionDefCallCases[functionDefName]!.validate(input, select, fn, [], []);

    const inputFailuresWithPath: _ValidationFailure[] = [];
    for (const f of inputFailures) {
        const thisPath = [functionName, ...f.path];
        inputFailuresWithPath.push({
            path: thisPath,
            reason: f.reason,
            data: f.data,
        });
    }

    const inputFailuresWithoutMissingRequired = inputFailuresWithPath.filter(
        (f) => f.reason !== 'RequiredObjectKeyMissing'
    );

    validationFailures.push(...inputFailuresWithoutMissingRequired);

    const resultDefKey = '->';

    if (!givenMap.hasOwnProperty(resultDefKey)) {
        validationFailures.push({
            path: [resultDefKey],
            reason: 'RequiredObjectKeyMissing',
            data: {},
        });
    } else {
        const output = givenMap[resultDefKey];
        const outputFailures = functionDef.result.validate(output, select, fn, [], []);

        const outputFailuresWithPath: _ValidationFailure[] = [];
        for (const f of outputFailures) {
            const thisPath = [resultDefKey, ...f.path];
            outputFailuresWithPath.push({
                path: thisPath,
                reason: f.reason,
                data: f.data,
            });
        }

        const failuresWithoutMissingRequired = outputFailuresWithPath.filter(
            (f) => f.reason !== 'RequiredObjectKeyMissing'
        );

        validationFailures.push(...failuresWithoutMissingRequired);
    }

    const disallowedFields = Object.keys(givenMap).filter((k) => !matches.includes(k) && k !== resultDefKey);
    for (const disallowedField of disallowedFields) {
        validationFailures.push({
            path: [disallowedField],
            reason: 'ObjectKeyDisallowed',
            data: {},
        });
    }

    return validationFailures;
}

export function selectStructFields(
    typeDeclaration: _UTypeDeclaration,
    value: any,
    selectedStructFields: Record<string, any>
): any {
    const typeDeclarationType = typeDeclaration.type;
    const typeDeclarationTypeParams = typeDeclaration.typeParameters;

    if (typeDeclarationType instanceof _UStruct) {
        const fields = typeDeclarationType.fields;
        const structName = typeDeclarationType.name;
        const selectedFields = selectedStructFields[structName] as string[];
        const valueAsMap = value as Record<string, any>;
        const finalMap: Record<string, any> = {};

        for (const [fieldName, fieldValue] of Object.entries(valueAsMap)) {
            if (!selectedFields || selectedFields.includes(fieldName)) {
                const field: _UFieldDeclaration = fields[fieldName]!;
                const fieldTypeDeclaration = field.typeDeclaration;
                const valueWithSelectedFields = selectStructFields(
                    fieldTypeDeclaration,
                    fieldValue,
                    selectedStructFields
                );

                finalMap[fieldName] = valueWithSelectedFields;
            }
        }

        return finalMap;
    } else if (typeDeclarationType instanceof _UFn) {
        const valueAsMap = value as Record<string, any>;
        const uEntry = unionEntry(valueAsMap);
        const unionCase = uEntry[0];
        const unionData = uEntry[1] as Record<string, any>;

        const fnName = typeDeclarationType.name;
        const fnCall = typeDeclarationType.call;
        const fnCallCases = fnCall.cases;

        const argStructReference: _UStruct = fnCallCases[unionCase]!;
        const selectedFields = selectedStructFields[fnName] as string[];
        const finalMap: Record<string, any> = {};

        for (const [fieldName, fieldValue] of Object.entries(unionData)) {
            if (!selectedFields || selectedFields.includes(fieldName)) {
                const field = argStructReference.fields[fieldName]!;
                const valueWithSelectedFields = selectStructFields(
                    field.typeDeclaration,
                    fieldValue,
                    selectedStructFields
                );

                finalMap[fieldName] = valueWithSelectedFields;
            }
        }

        return { [unionCase]: finalMap };
    } else if (typeDeclarationType instanceof _UUnion) {
        const valueAsMap = value as Record<string, any>;
        const uEntry = unionEntry(valueAsMap);
        const unionCase = uEntry[0];
        const unionData = uEntry[1] as Record<string, any>;

        const unionCases = typeDeclarationType.cases;
        const unionStructReference = unionCases[unionCase]!;
        const unionStructRefFields = unionStructReference.fields;
        const defaultCasesToFields: Record<string, string[]> = {};

        for (const [caseName, unionStruct] of Object.entries(unionCases)) {
            const unionStructFields = Object.keys(unionStruct.fields);
            defaultCasesToFields[caseName] = unionStructFields;
        }

        const unionSelectedFields: Record<string, string[]> =
            selectedStructFields[typeDeclarationType.name] ?? defaultCasesToFields;
        const thisUnionCaseSelectedFieldsDefault = defaultCasesToFields[unionCase];
        const selectedFields = unionSelectedFields[unionCase] ?? thisUnionCaseSelectedFieldsDefault;

        const finalMap: Record<string, any> = {};
        for (const [fieldName, fieldValue] of Object.entries(unionData)) {
            if (!selectedFields || selectedFields.includes(fieldName)) {
                const field = unionStructRefFields[fieldName]!;
                const valueWithSelectedFields = selectStructFields(
                    field.typeDeclaration,
                    fieldValue,
                    selectedStructFields
                );
                finalMap[fieldName] = valueWithSelectedFields;
            }
        }

        return { [unionCase]: finalMap };
    } else if (typeDeclarationType instanceof _UObject) {
        const nestedTypeDeclaration = typeDeclarationTypeParams[0]!;
        const valueAsMap = value as Record<string, any>;

        const finalMap: Record<string, any> = {};
        for (const [key, nestedValue] of Object.entries(valueAsMap)) {
            const valueWithSelectedFields = selectStructFields(
                nestedTypeDeclaration,
                nestedValue,
                selectedStructFields
            );
            finalMap[key] = valueWithSelectedFields;
        }

        return finalMap;
    } else if (typeDeclarationType instanceof _UArray) {
        const nestedType = typeDeclarationTypeParams[0]!;
        const valueAsList = value as any[];

        const finalList: any[] = [];
        for (const entry of valueAsList) {
            const valueWithSelectedFields = selectStructFields(nestedType, entry, selectedStructFields);
            finalList.push(valueWithSelectedFields);
        }

        return finalList;
    } else {
        return value;
    }
}

export function getInvalidErrorMessage(
    error: string,
    validationFailures: _ValidationFailure[],
    resultUnionType: _UUnion,
    responseHeaders: { [key: string]: any }
): Message {
    const validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
    const newErrorResult = { [error]: { cases: validationFailureCases } };

    validateResult(resultUnionType, newErrorResult);
    return new Message(responseHeaders, newErrorResult);
}

export function mapValidationFailuresToInvalidFieldCases(
    argumentValidationFailures: _ValidationFailure[]
): Record<string, any>[] {
    const validationFailureCases: Record<string, any>[] = [];
    for (const validationFailure of argumentValidationFailures) {
        const validationFailureCase = {
            path: validationFailure.path,
            reason: { [validationFailure.reason]: validationFailure.data },
        };
        validationFailureCases.push(validationFailureCase);
    }

    return validationFailureCases;
}

export function validateResult(resultUnionType: _UUnion, errorResult: { [key: string]: any }): void {
    const newErrorResultValidationFailures = resultUnionType.validate(errorResult, undefined, undefined, [], []);
    if (newErrorResultValidationFailures.length !== 0) {
        console.log(`original error: ${JSON.stringify(errorResult)}`);
        throw new UApiError(
            'Failed internal uAPI validation: ' +
                JSON.stringify(mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures), null, 2)
        );
    }
}

export async function handleMessage(
    requestMessage: Message,
    uApiSchema: UApiSchema,
    handler: (message: Message) => Promise<Message>,
    onError: (error: Error) => void
): Promise<Message> {
    const responseHeaders: { [key: string]: any } = {};
    const requestHeaders = requestMessage.header;
    const requestBody = requestMessage.body;
    const parsedUApiSchema = uApiSchema.parsed;
    const requestEntry = unionEntry(requestBody);

    const requestTargetInit = requestEntry[0];
    const requestPayload: Record<string, any> = requestEntry[1];

    let unknownTarget: string | null;
    let requestTarget: string;
    if (!parsedUApiSchema.hasOwnProperty(requestTargetInit)) {
        unknownTarget = requestTargetInit;
        requestTarget = 'fn._ping';
    } else {
        unknownTarget = null;
        requestTarget = requestTargetInit;
    }

    const functionType = parsedUApiSchema[requestTarget] as _UFn;
    const resultUnionType = functionType.result;

    const callId = requestHeaders['_id'];
    if (callId !== undefined) {
        responseHeaders['_id'] = callId;
    }

    if (requestHeaders.hasOwnProperty('_parseFailures')) {
        const parseFailures = requestHeaders['_parseFailures'] as unknown as Array<any>;
        const newErrorResult = {
            _ErrorParseFailure: {
                reasons: parseFailures,
            },
        };

        validateResult(resultUnionType, newErrorResult);

        return new Message(responseHeaders, newErrorResult);
    }

    const requestHeaderValidationFailures = validateHeaders(
        requestHeaders,
        uApiSchema.parsedRequestHeaders,
        functionType
    );
    if (requestHeaderValidationFailures.length > 0) {
        return getInvalidErrorMessage(
            '_ErrorInvalidRequestHeaders',
            requestHeaderValidationFailures,
            resultUnionType,
            responseHeaders
        );
    }

    if (requestHeaders.hasOwnProperty('_bin')) {
        const clientKnownBinaryChecksums = requestHeaders['_bin'] as unknown as Array<any>;

        responseHeaders['_binary'] = true;
        responseHeaders['_clientKnownBinaryChecksums'] = clientKnownBinaryChecksums;

        if (requestHeaders.hasOwnProperty('_pac')) {
            responseHeaders['_pac'] = requestHeaders['_pac'];
        }
    }

    const selectStructFieldsHeader: Record<string, any> | undefined = requestHeaders['_sel'] as Record<string, any>;

    if (unknownTarget !== null) {
        const newErrorResult = {
            _ErrorInvalidRequestBody: {
                cases: [
                    {
                        path: [unknownTarget],
                        reason: {
                            FunctionUnknown: {},
                        },
                    },
                ],
            },
        };

        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }

    const functionTypeCall = functionType.call as _UUnion;

    const warnings: _ValidationFailure[] = [];
    const filterOutWarnings = (e: _ValidationFailure) => {
        const r = e.reason == NUMBER_TRUNCATED;
        if (r) {
            warnings.push(e);
        }
        return !r;
    };

    const callValidationFailures: _ValidationFailure[] = functionTypeCall
        .validate(requestBody, undefined, undefined, [], [])
        .filter(filterOutWarnings);
    if (callValidationFailures.length > 0) {
        if (warnings.length > 0) {
            responseHeaders['_warnings'] = mapValidationFailuresToInvalidFieldCases(warnings);
        }

        return getInvalidErrorMessage(
            '_ErrorInvalidRequestBody',
            callValidationFailures,
            resultUnionType,
            responseHeaders
        );
    }

    const unsafeResponseEnabled = requestHeaders['_unsafe'] === true;

    const callMessage = new Message(requestHeaders, {
        [requestTarget]: requestPayload,
    });

    let resultMessage: Message;
    if (requestTarget === 'fn._ping') {
        resultMessage = new Message({}, { Ok: {} });
    } else if (requestTarget === 'fn._api') {
        resultMessage = new Message({}, { Ok: { api: uApiSchema.original } });
    } else {
        try {
            resultMessage = await handler(callMessage);
        } catch (e) {
            try {
                onError(e as Error);
            } catch (ignored) {}

            return new Message(responseHeaders, { _ErrorUnknown: {} });
        }
    }

    const resultUnion = resultMessage.body;

    Object.assign(resultMessage.header, responseHeaders);
    const finalResponseHeaders = resultMessage.header;

    const skipResultValidation = unsafeResponseEnabled;
    if (!skipResultValidation) {
        const resultValidationFailures = resultUnionType
            .validate(resultUnion, selectStructFieldsHeader, undefined, [], [])
            .filter(filterOutWarnings);

        if (warnings.length > 0) {
            responseHeaders['_warnings'] = mapValidationFailuresToInvalidFieldCases(warnings);
        }

        if (resultValidationFailures.length > 0) {
            return getInvalidErrorMessage(
                '_ErrorInvalidResponseBody',
                resultValidationFailures,
                resultUnionType,
                responseHeaders
            );
        }

        const responseHeaderValidationFailures = validateHeaders(
            finalResponseHeaders,
            uApiSchema.parsedResponseHeaders,
            functionType
        );
        if (responseHeaderValidationFailures.length > 0) {
            return getInvalidErrorMessage(
                '_ErrorInvalidResponseHeaders',
                responseHeaderValidationFailures,
                resultUnionType,
                responseHeaders
            );
        }
    }

    let finalResultUnion;
    if (selectStructFieldsHeader) {
        finalResultUnion = selectStructFields(
            new _UTypeDeclaration(resultUnionType, false, []),
            resultUnion,
            selectStructFieldsHeader
        );
    } else {
        finalResultUnion = resultUnion;
    }

    return new Message(finalResponseHeaders, finalResultUnion);
}

export function parseRequestMessage(
    requestMessageBytes: Uint8Array,
    serializer: Serializer,
    uApiSchema: UApiSchema,
    onError: (e: Error) => void
): Message {
    try {
        return serializer.deserialize(requestMessageBytes);
    } catch (e) {
        onError(e as Error);

        let reason: string;
        if (e instanceof _BinaryEncoderUnavailableError) {
            reason = 'IncompatibleBinaryEncoding';
        } else if (e instanceof _BinaryEncodingMissing) {
            reason = 'BinaryDecodeFailure';
        } else if (e instanceof _InvalidMessage) {
            reason = 'ExpectedJsonArrayOfTwoObjects';
        } else if (e instanceof _InvalidMessageBody) {
            reason = 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject';
        } else {
            reason = 'ExpectedJsonArrayOfTwoObjects';
        }

        return new Message({ _parseFailures: [{ [reason]: {} }] }, { _unknown: {} });
    }
}

export async function processBytes(
    requestMessageBytes: Uint8Array,
    serializer: Serializer,
    uApiSchema: UApiSchema,
    onError: (e: Error) => void,
    onRequest: (m: Message) => void,
    onResponse: (m: Message) => void,
    handler: (m: Message) => Promise<Message>
): Promise<Uint8Array> {
    try {
        const requestMessage = parseRequestMessage(requestMessageBytes, serializer, uApiSchema, onError);

        try {
            onRequest(requestMessage);
        } catch (ignored) {}

        const responseMessage = await handleMessage(requestMessage, uApiSchema, handler, onError);

        try {
            onResponse(responseMessage);
        } catch (ignored) {}

        return serializer.serialize(responseMessage);
    } catch (e) {
        try {
            onError(e as Error);
        } catch (ignored) {}

        return serializer.serialize(new Message({}, { _ErrorUnknown: {} }));
    }
}

export function isSubMap(part: Record<string, any>, whole: Record<string, any>): boolean {
    for (const partKey of Object.keys(part)) {
        const wholeValue = whole[partKey];
        const partValue = part[partKey];
        const entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
        if (!entryIsEqual) {
            return false;
        }
    }
    return true;
}

export function isSubMapEntryEqual(partValue: any, wholeValue: any): boolean {
    if (Array.isArray(partValue) && Array.isArray(wholeValue)) {
        for (let i = 0; i < partValue.length; i += 1) {
            const partElement = partValue[i];
            const partMatches = partiallyMatches(wholeValue, partElement);
            if (!partMatches) {
                return false;
            }
        }

        return true;
    } else if (typeof partValue === 'object' && typeof wholeValue === 'object') {
        return isSubMap(partValue, wholeValue);
    } else {
        return objectsAreEqual(partValue, wholeValue);
    }
}

function objectsAreEqual(obj1: any, obj2: any): boolean {
    // Check if both objects are the same type
    if (typeof obj1 !== typeof obj2) {
        return false;
    }

    // If objects are primitive types, compare directly
    if (typeof obj1 !== 'object' || obj1 === null || obj2 === null) {
        return obj1 === obj2;
    }

    // Check if both objects have the same keys
    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);
    if (keys1.length !== keys2.length || !keys1.every((key) => keys2.includes(key))) {
        return false;
    }

    // Recursively compare nested objects and arrays
    for (const key of keys1) {
        if (!objectsAreEqual(obj1[key], obj2[key])) {
            return false;
        }
    }

    // If all checks pass, objects are considered equal
    return true;
}

export function partiallyMatches(wholeList: any[], partElement: any): boolean {
    for (const wholeElement of wholeList) {
        if (isSubMapEntryEqual(partElement, wholeElement)) {
            return true;
        }
    }

    return false;
}

function verify(
    functionName: string,
    argument: { [key: string]: any },
    exactMatch: boolean,
    verificationTimes: { [key: string]: any },
    invocations: _MockInvocation[]
): Record<string, any> {
    let matchesFound = 0;
    for (const invocation of invocations) {
        if (invocation.functionName === functionName) {
            if (exactMatch) {
                if (JSON.stringify(invocation.functionArgument) === JSON.stringify(argument)) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            } else {
                const isSubMapVal = isSubMap(argument, invocation.functionArgument);
                if (isSubMapVal) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            }
        }
    }

    const allCallsPseudoJson: { [key: string]: any }[] = [];
    for (const invocation of invocations) {
        allCallsPseudoJson.push({
            [invocation.functionName]: invocation.functionArgument,
        });
    }

    const [verifyKey, verifyTimesStruct] = unionEntry(verificationTimes);

    let verificationFailurePseudoJson: { [key: string]: any } | null = null;
    if (verifyKey === 'Exact') {
        const times = verifyTimesStruct.times;
        if (matchesFound > times) {
            verificationFailurePseudoJson = {
                TooManyMatchingCalls: {
                    wanted: { Exact: { times: times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        } else if (matchesFound < times) {
            verificationFailurePseudoJson = {
                TooFewMatchingCalls: {
                    wanted: { Exact: { times: times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    } else if (verifyKey === 'AtMost') {
        const times = verifyTimesStruct.times;
        if (matchesFound > times) {
            verificationFailurePseudoJson = {
                TooManyMatchingCalls: {
                    wanted: { AtMost: { times: times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    } else if (verifyKey === 'AtLeast') {
        const times = verifyTimesStruct.times;
        if (matchesFound < times) {
            verificationFailurePseudoJson = {
                TooFewMatchingCalls: {
                    wanted: { AtLeast: { times: times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    }

    if (verificationFailurePseudoJson === null) {
        return { Ok: {} };
    }

    return {
        ErrorVerificationFailure: { reason: verificationFailurePseudoJson },
    };
}

function verifyNoMoreInteractions(invocations: _MockInvocation[]): Record<string, any> {
    const invocationsNotVerified = invocations.filter((i) => !i.verified);

    if (invocationsNotVerified.length > 0) {
        const unverifiedCallsPseudoJson: { [key: string]: any }[] = [];
        for (const invocation of invocationsNotVerified) {
            unverifiedCallsPseudoJson.push({
                [invocation.functionName]: invocation.functionArgument,
            });
        }
        return {
            ErrorVerificationFailure: {
                additionalUnverifiedCalls: unverifiedCallsPseudoJson,
            },
        };
    }

    return { Ok: {} };
}

export function mockHandle(
    requestMessage: Message,
    stubs: _MockStub[],
    invocations: _MockInvocation[],
    random: _RandomGenerator,
    uApiSchema: UApiSchema,
    enableGeneratedDefaultStub: boolean,
    enableOptionalFieldGeneration: boolean,
    randomizeOptionalFieldGeneration: boolean
): Message {
    console.log(`enableOptionalFieldGeneration: ${enableOptionalFieldGeneration}`);
    const header = requestMessage.header;

    const enableGenerationStub = header['_gen'] || false;
    const functionName = requestMessage.getBodyTarget();
    const argument: Record<string, any> = requestMessage.getBodyPayload();

    switch (functionName) {
        case 'fn._createStub': {
            const givenStub = argument['stub'];

            const stubCall = Object.entries(givenStub).find(([key]) => key.startsWith('fn.'))!;
            const stubFunctionName = stubCall[0];
            const stubArg: Record<string, any> = stubCall[1]!;
            const stubResult = givenStub['->'];
            const allowArgumentPartialMatch = !(argument['strictMatch!'] || false);
            const stubCount = argument['count!'] ?? -1;

            const stub: _MockStub = {
                whenFunction: stubFunctionName,
                whenArgument: { ...stubArg },
                thenResult: { ...stubResult },
                allowArgumentPartialMatch,
                count: stubCount,
            };

            stubs.unshift(stub);
            return new Message({}, { Ok: {} });
        }
        case 'fn._verify': {
            const givenCall = argument['call'];

            const call = Object.entries(givenCall).find(([key]) => key.startsWith('fn.'))!;
            const callFunctionName = call[0];
            const callArg = call[1]!;
            const verifyTimes = argument['count!'] || { AtLeast: { times: 1 } };
            const strictMatch = argument['strictMatch!'] || false;

            const verificationResult = verify(callFunctionName, callArg, strictMatch, verifyTimes, invocations);
            return new Message({}, verificationResult);
        }
        case 'fn._verifyNoMoreInteractions': {
            const verificationResult = verifyNoMoreInteractions(invocations);
            return new Message({}, verificationResult);
        }
        case 'fn._clearCalls': {
            invocations.length = 0;
            return new Message({}, { Ok: {} });
        }
        case 'fn._clearStubs': {
            stubs.length = 0;
            return new Message({}, { Ok: {} });
        }
        case 'fn._setRandomSeed': {
            const givenSeed = argument['seed'];

            random.setSeed(givenSeed);
            return new Message({}, { Ok: {} });
        }
        default: {
            invocations.push(new _MockInvocation(functionName, argument));

            const definition: _UFn = uApiSchema.parsed[functionName] as _UFn;

            for (const stub of stubs) {
                if (stub.count === 0) {
                    continue;
                }
                if (stub.whenFunction === functionName) {
                    if (stub.allowArgumentPartialMatch) {
                        if (isSubMap(stub.whenArgument, argument)) {
                            const useBlueprintValue = true;
                            const includeOptionalFields = false;
                            const result = definition.result.generateRandomValue(
                                stub.thenResult,
                                useBlueprintValue,
                                includeOptionalFields,
                                randomizeOptionalFieldGeneration,
                                [],
                                [],
                                random
                            );
                            if (stub.count > 0) {
                                stub.count -= 1;
                            }
                            return new Message({}, result);
                        }
                    } else {
                        if (objectsAreEqual(stub.whenArgument, argument)) {
                            const useBlueprintValue = true;
                            const includeOptionalFields = false;
                            const result = definition.result.generateRandomValue(
                                stub.thenResult,
                                useBlueprintValue,
                                includeOptionalFields,
                                randomizeOptionalFieldGeneration,
                                [],
                                [],
                                random
                            );
                            if (stub.count > 0) {
                                stub.count -= 1;
                            }
                            return new Message({}, result);
                        }
                    }
                }
            }

            if (!enableGeneratedDefaultStub && !enableGenerationStub) {
                return new Message({}, { _ErrorNoMatchingStub: {} });
            }

            if (definition) {
                const resultUnion = definition.result as any;
                const okStructRef = resultUnion.cases['Ok'];
                const useBlueprintValue = true;
                const randomOkStruct = okStructRef.generateRandomValue(
                    {},
                    useBlueprintValue,
                    enableOptionalFieldGeneration,
                    randomizeOptionalFieldGeneration,
                    [],
                    [],
                    random
                );
                return new Message({}, { Ok: randomOkStruct });
            } else {
                throw new UApiError(`Unexpected unknown function: ${functionName}`);
            }
        }
    }
}

export async function processRequestObject(
    requestMessage: Message,
    adapter: (requestMessage: Message, serializer: Serializer) => Promise<Message>,
    serializer: Serializer,
    timeoutMsDefault: number,
    useBinaryDefault: boolean
): Promise<Message> {
    const header = requestMessage.header;

    try {
        if (!header.hasOwnProperty('_tim')) {
            header['_tim'] = timeoutMsDefault;
        }

        if (useBinaryDefault) {
            header['_binary'] = true;
        }

        const timeoutMs = header['_tim'] as number;

        const responseMessage = await Promise.race([adapter(requestMessage, serializer), timeoutPromise(timeoutMs)]);

        if (
            objectsAreEqual(responseMessage.body, {
                _ErrorParseFailure: {
                    reasons: [{ IncompatibleBinaryEncoding: {} }],
                },
            })
        ) {
            // Try again, but as json
            header['_binary'] = true;
            header['_forceSendJson'] = true;

            return await Promise.race([adapter(requestMessage, serializer), timeoutPromise(timeoutMs)]);
        }

        return responseMessage;
    } catch (e) {
        throw new UApiError(e as Error);
    }
}

function timeoutPromise(timeoutMs: number): Promise<never> {
    return new Promise((_resolve, reject) => {
        setTimeout(() => {
            reject(new Error('Promise timed out'));
        }, timeoutMs);
    });
}

export function mapSchemaParseFailuresToPseudoJson(schemaParseFailures: any[]): any[] {
    return schemaParseFailures.map((f) => ({
        ...(f.key === null ? {} : { 'key!': f.key }),
        path: f.path,
        reason: { [f.reason]: f.data },
    }));
}
