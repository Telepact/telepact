export function findMatchingSchemaKey(schemaKeys: Set<string>, schemaKey: string): string | null {
    for (const k of schemaKeys) {
        if (schemaKey.startsWith('info.') && k.startsWith('info.')) {
            return k;
        }
        if (k === schemaKey) {
            return k;
        }
    }
    return null;
}
