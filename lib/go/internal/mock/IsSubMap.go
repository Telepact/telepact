//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package mock

// IsSubMap verifies that every entry in part matches the corresponding entry in whole.
func IsSubMap(part map[string]any, whole map[string]any) bool {
	if len(part) == 0 {
		return true
	}

	for key, partValue := range part {
		wholeValue, ok := whole[key]
		if !ok {
			return false
		}

		if !IsSubMapEntryEqual(partValue, wholeValue) {
			return false
		}
	}

	return true
}
