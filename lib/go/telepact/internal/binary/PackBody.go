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

package binary

// PackBody packs the message body map into the compact binary representation when possible.
func PackBody(body map[any]any) (map[any]any, error) {
	result := make(map[any]any, len(body))
	for key, value := range body {
		packedValue, err := Pack(value)
		if err != nil {
			return nil, err
		}
		result[key] = packedValue
	}
	return result, nil
}
