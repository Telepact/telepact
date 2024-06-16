import { isSubMapEntryEqual } from './IsSubMapEntryEqual';

export function partiallyMatches(wholeList: any[], partElement: any): boolean {
    for (const wholeElement of wholeList) {
        if (isSubMapEntryEqual(partElement, wholeElement)) {
            return true;
        }
    }
    return false;
}
