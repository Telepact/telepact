import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';

export function offsetSchemaIndex(
    initialFailures: SchemaParseFailure[],
    offset: number,
    schemaKeysToIndex: { [key: string]: number },
    errorIndices: Set<number>,
): SchemaParseFailure[] {
    const finalList: SchemaParseFailure[] = [];

    const indexToSchemaKey: { [key: number]: string } = {};
    for (const [key, value] of Object.entries(schemaKeysToIndex)) {
        indexToSchemaKey[value] = key;
    }

    for (const f of initialFailures) {
        const reason = f.reason;
        const path = f.path;
        const data: { [key: string]: any } = f.data;
        const newPath = [...path];

        const originalIndex = newPath[0];
        newPath[0] = originalIndex - offset;

        let finalData: { [key: string]: any };
        if (reason === 'PathCollision') {
            const otherNewPath = data['other'];
            otherNewPath[0] = otherNewPath[0] - offset;
            finalData = { other: otherNewPath };
        } else {
            finalData = data;
        }

        let schemaKey: string | null;
        if (errorIndices.has(originalIndex)) {
            schemaKey = 'errors';
        } else {
            schemaKey = indexToSchemaKey[originalIndex] || null;
        }

        finalList.push(new SchemaParseFailure(newPath, reason, finalData, schemaKey));
    }

    return finalList;
}
