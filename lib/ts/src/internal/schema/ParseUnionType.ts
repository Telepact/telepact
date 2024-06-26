import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UUnion } from '../../internal/types/UUnion';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructFields } from '../../internal/schema/ParseStructFields';
import { UStruct } from '../../internal/types/UStruct';
import { UType } from '../../internal/types/UType';

export function parseUnionType(
    path: any[],
    unionDefinitionAsPseudoJson: { [key: string]: any },
    schemaKey: string,
    ignoreKeys: string[],
    requiredKeys: string[],
    typeParameterCount: number,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    typeExtensions: { [key: string]: UType },
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
            parseFailures.push(new SchemaParseFailure(loopPath, 'ObjectKeyDisallowed', {}, null));
        }
    }

    const thisPath = path.concat(schemaKey);
    const defInit = unionDefinitionAsPseudoJson[schemaKey];

    if (!Array.isArray(defInit)) {
        const finalParseFailures = getTypeUnexpectedParseFailure(thisPath, defInit, 'Array');
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
            const thisParseFailures = getTypeUnexpectedParseFailure(loopPath, element, 'Object');
            parseFailures.push(...thisParseFailures);
            continue;
        }
        definition.push(element);
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    if (definition.length === 0 && requiredKeys.length === 0) {
        parseFailures.push(new SchemaParseFailure(thisPath, 'EmptyArrayDisallowed', {}, null));
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
                parseFailures.push(new SchemaParseFailure(branchPath, 'RequiredObjectKeyMissing', {}, null));
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
                new SchemaParseFailure(
                    loopPath,
                    'ObjectKeyRegexMatchCountUnexpected',
                    { regex: regexString, actual: matches.length, expected: 1, keys: keys },
                    null,
                ),
            );
            continue;
        }
        if (Object.keys(map).length !== 1) {
            parseFailures.push(
                new SchemaParseFailure(
                    loopPath,
                    'ObjectSizeUnexpected',
                    { expected: 1, actual: Object.keys(map).length },
                    null,
                ),
            );
            continue;
        }

        const entry = Object.entries(map)[0];
        const unionCase = entry[0];
        const unionKeyPath = loopPath.concat(unionCase);

        if (typeof entry[1] !== 'object' || Array.isArray(entry[1])) {
            const thisParseFailures = getTypeUnexpectedParseFailure(unionKeyPath, entry[1], 'Object');
            parseFailures.push(...thisParseFailures);
            continue;
        }
        const unionCaseStruct = entry[1];

        try {
            const fields = parseStructFields(
                unionCaseStruct,
                unionKeyPath,
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
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
