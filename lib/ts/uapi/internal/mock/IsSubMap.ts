import { isSubMapEntryEqual } from 'uapi/internal/mock/IsSubMapEntryEqual';

export function isSubMap(part: Record<string, any>, whole: Record<string, any>): boolean {
    for (const partKey in part) {
        const wholeValue = whole[partKey] as Record<string, any>;
        const partValue = part[partKey] as Record<string, any>;
        const entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
        if (!entryIsEqual) {
            return false;
        }
    }
    return true;
}
