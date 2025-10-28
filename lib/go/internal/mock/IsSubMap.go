//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
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
