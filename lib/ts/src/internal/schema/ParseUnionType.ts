import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UUnion } from '../../internal/types/UUnion';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructFields } from '../../internal/schema/ParseStructFields';
import { UStruct } from '../../internal/types/UStruct';
import { UType } from '../../internal/types/UType';

export function parseUnionType(
    documentName: string,
    path: any[],
    unionDefinitionAsPseudoJson: { [key: string]: any },
    schemaKey: string,
    ignoreKeys: string[],
    requiredKeys: string[],
    typeParameterCount: number,
    uApiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
    schemaKeysToDocumentName: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UUnion {
    const parseFailures: SchemaParseFailure[] = [];

    const otherKeys = new Set(Object.keys(unionDefinitionAsPseudoJson));
    otherKeys.delete(schemaKey);
    otherKeys.delete('///');
    for (const ignoreKey of ignoreKeys) {
        otherKeys.delete(ignoreKey);
    }

    if (otherKeys.size > 0) {
        for (const k of otherKeys) {
            const loopPath = path.concat(k);
            parseFailures.push(new SchemaParseFailure(documentName, loopPath, 'ObjectKeyDisallowed', {}));
        }
    }

    const thisPath = path.concat(schemaKey);
    const defInit = unionDefinitionAsPseudoJson[schemaKey];

    if (!Array.isArray(defInit)) {
        const finalParseFailures = getTypeUnexpectedParseFailure(documentName, thisPath, defInit, 'Array');
        parseFailures.push(...finalParseFailures);
        throw new UApiSchemaParseError(parseFailures);
    }

    const definition2 = defInit;
    const definition = [];
    let index = -1;
    for (const element of definition2) {
        index += 1;
        const loopPath = thisPath.concat(index);
        if (typeof element !== 'object' || Array.isArray(element) || element === null || element === undefined) {
            const thisParseFailures = getTypeUnexpectedParseFailure(documentName, loopPath, element, 'Object');
            parseFailures.push(...thisParseFailures);
            continue;
        }
        definition.push(element);
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    if (definition.length === 0 && requiredKeys.length === 0) {
        parseFailures.push(new SchemaParseFailure(documentName, thisPath, 'EmptyArrayDisallowed', {}));
    } else {
        for (const requiredKey of requiredKeys) {
            let found = false;
            for (const element of definition) {
                const caseKeys = new Set(Object.keys(element));
                caseKeys.delete('///');
                if (caseKeys.has(requiredKey)) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                const branchPath = thisPath.concat(0, requiredKey);
                parseFailures.push(new SchemaParseFailure(documentName, branchPath, 'RequiredObjectKeyMissing', {}));
            }
        }
    }

    const cases: { [key: string]: UStruct } = {};
    const caseIndices: { [key: string]: number } = {};

    for (let i = 0; i < definition.length; i++) {
        const element = definition[i];
        const loopPath = thisPath.concat(i);
        const mapInit = element;
        const map = Object.fromEntries(Object.entries(mapInit));
        delete map['///'];
        const keys = Object.keys(map);

        const regexString = '^([A-Z][a-zA-Z0-9_]*)$';

        const regex = new RegExp(regexString);
        const matches = keys.filter((k) => regex.test(k));
        if (matches.length !== 1) {
            parseFailures.push(
                new SchemaParseFailure(documentName, loopPath, 'ObjectKeyRegexMatchCountUnexpected', {
                    regex: regexString,
                    actual: matches.length,
                    expected: 1,
                    keys: keys,
                }),
            );
            continue;
        }
        if (Object.keys(map).length !== 1) {
            parseFailures.push(
                new SchemaParseFailure(documentName, loopPath, 'ObjectSizeUnexpected', {
                    expected: 1,
                    actual: Object.keys(map).length,
                }),
            );
            continue;
        }

        const entry = Object.entries(map)[0];
        const unionCase = entry[0];
        const unionKeyPath = loopPath.concat(unionCase);

        if (typeof entry[1] !== 'object' || Array.isArray(entry[1]) || entry[1] === null || entry[1] === undefined) {
            const thisParseFailures = getTypeUnexpectedParseFailure(documentName, unionKeyPath, entry[1], 'Object');
            parseFailures.push(...thisParseFailures);
            continue;
        }
        const unionCaseStruct = entry[1];

        try {
            const fields = parseStructFields(
                unionCaseStruct,
                documentName,
                unionKeyPath,
                typeParameterCount,
                uApiSchemaDocumentNamesToPseudoJson,
                schemaKeysToDocumentName,
                schemaKeysToIndex,
                parsedTypes,
                allParseFailures,
                failedTypes,
            );
            const unionStruct = new UStruct(`${schemaKey}.${unionCase}`, fields, typeParameterCount);
            cases[unionCase] = unionStruct;
            caseIndices[unionCase] = i;
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

    return new UUnion(schemaKey, cases, caseIndices, typeParameterCount);
}
