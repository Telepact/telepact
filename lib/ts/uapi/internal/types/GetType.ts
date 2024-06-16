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
