export function convertMapsToObjects(value: any): any {
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
