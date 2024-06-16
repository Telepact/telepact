import { isSubMap } from './IsSubMap';
import { partiallyMatches } from './PartiallyMatches';

export function isSubMapEntryEqual(partValue: any, wholeValue: any): boolean {
    if (typeof partValue === 'object' && typeof wholeValue === 'object') {
        return isSubMap(partValue, wholeValue);
    } else if (Array.isArray(partValue) && Array.isArray(wholeValue)) {
        for (const partElement of partValue) {
            const partMatches = partiallyMatches(wholeValue, partElement);
            if (!partMatches) {
                return false;
            }
        }
        return true;
    } else {
        return partValue === wholeValue;
    }
}
