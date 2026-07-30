//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package mock

// PartiallyMatches determines if any element in wholeList matches partElement using sub-map comparison semantics.
func PartiallyMatches(wholeList []any, partElement any) bool {
	for _, wholeElement := range wholeList {
		if IsSubMapEntryEqual(partElement, wholeElement) {
			return true
		}
	}
	return false
}
