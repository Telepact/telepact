import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';

export function catchErrorCollisions(
    uApiSchemaPseudoJson: any[],
    errorKeys: Set<string>,
    keysToIndex: Record<string, number>,
): void {
    const parseFailures: SchemaParseFailure[] = [];

    const indices = Array.from(errorKeys, (key) => keysToIndex[key]).sort();
    const indexToKeys: Record<number, string> = {};
    for (const [key, value] of Object.entries(keysToIndex)) {
        indexToKeys[value] = key;
    }

    for (let i = 0; i < indices.length; i++) {
        for (let j = i + 1; j < indices.length; j++) {
            const index = indices[i];
            const otherIndex = indices[j];

            const def = uApiSchemaPseudoJson[index] as Record<string, object>;
            const otherDef = uApiSchemaPseudoJson[otherIndex] as Record<string, object>;

            const defKey = indexToKeys[index];
            const otherDefKey = indexToKeys[otherIndex];

            const errDef = def[defKey] as object[];
            const otherErrDef = otherDef[otherDefKey] as object[];

            for (let k = 0; k < errDef.length; k++) {
                const thisErrDef = errDef[k] as Record<string, object>;
                const thisErrDefKeys = new Set(Object.keys(thisErrDef));
                thisErrDefKeys.delete('///');

                for (let l = 0; l < otherErrDef.length; l++) {
                    const thisOtherErrDef = otherErrDef[l] as Record<string, object>;
                    const thisOtherErrDefKeys = new Set(Object.keys(thisOtherErrDef));
                    thisOtherErrDefKeys.delete('///');

                    if (
                        thisErrDefKeys.size === thisOtherErrDefKeys.size &&
                        [...thisErrDefKeys].every((key) => thisOtherErrDefKeys.has(key))
                    ) {
                        const thisErrorDefKey = thisErrDefKeys.values().next().value as string;
                        const thisOtherErrorDefKey = thisOtherErrDefKeys.values().next().value as string;
                        parseFailures.push(
                            new SchemaParseFailure(
                                [otherIndex, otherDefKey, l, thisOtherErrorDefKey],
                                'PathCollision',
                                { other: [index, defKey, k, thisErrorDefKey] },
                                otherDefKey,
                            ),
                        );
                    }
                }
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }
}
