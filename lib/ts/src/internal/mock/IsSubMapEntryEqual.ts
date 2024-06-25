import { isSubMap } from '../../internal/mock/IsSubMap';
import { partiallyMatches } from '../../internal/mock/PartiallyMatches';
import { objectsAreEqual } from '../ObjectsAreEqual';

export function isSubMapEntryEqual(partValue: any, wholeValue: any): boolean {
    if (Array.isArray(partValue) && Array.isArray(wholeValue)) {
        for (let i = 0; i < partValue.length; i += 1) {
            const partElement = partValue[i];
            const partMatches = partiallyMatches(wholeValue, partElement);
            if (!partMatches) {
                return false;
            }
        }

        return true;
    } else if (typeof partValue === 'object' && typeof wholeValue === 'object') {
        return isSubMap(partValue, wholeValue);
    } else {
        return objectsAreEqual(partValue, wholeValue);
    }
}
