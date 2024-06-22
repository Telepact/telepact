import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';

export function catchErrorCollisions(
    uApiSchemaPseudoJson: any[],
    errorIndices: Set<number>,
    keysToIndex: Record<string, number>,
): void {
    const parseFailures: SchemaParseFailure[] = [];

    const indices = Array.from(errorIndices).sort();

    for (let i = 0; i < indices.length; i++) {
        for (let j = i + 1; j < indices.length; j++) {
            const index = indices[i];
            const otherIndex = indices[j];

            const def = uApiSchemaPseudoJson[index] as Record<string, any>;
            const otherDef = uApiSchemaPseudoJson[otherIndex] as Record<string, any>;

            const errDef = def.errors as any[];
            const otherErrDef = otherDef.errors as any[];

            for (let k = 0; k < errDef.length; k++) {
                const thisErrDef = errDef[k] as Record<string, any>;
                const thisErrDefKeys = new Set(Object.keys(thisErrDef));
                thisErrDefKeys.delete('///');

                for (let l = 0; l < otherErrDef.length; l++) {
                    const thisOtherErrDef = otherErrDef[l] as Record<string, any>;
                    const thisOtherErrDefKeys = new Set(Object.keys(thisOtherErrDef));
                    thisOtherErrDefKeys.delete('///');

                    if (
                        thisErrDefKeys.size === thisOtherErrDefKeys.size &&
                        [...thisErrDefKeys].every((key) => thisOtherErrDefKeys.has(key))
                    ) {
                        const thisErrorDefKey = [...thisErrDefKeys][0];
                        const thisOtherErrorDefKey = [...thisOtherErrDefKeys][0];
                        parseFailures.push(
                            new SchemaParseFailure(
                                [otherIndex, 'errors', l, thisOtherErrorDefKey],
                                'PathCollision',
                                { other: [index, 'errors', k, thisErrorDefKey] },
                                'errors',
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
