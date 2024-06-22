export function findMatchingSchemaKey(schemaKeys: Set<string>, schemaKey: string): string | null {
    for (const k of schemaKeys) {
        if (k === schemaKey) {
            return k;
        }
    }
    return null;
}
