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

import "fmt"

// EncodeBody encodes a pseudo-JSON message body with the provided BinaryEncoding lookup tables.
func EncodeBody(messageBody map[string]any, encoding *BinaryEncoding) (map[any]any, error) {
	encoded, err := EncodeKeys(messageBody, encoding)
	if err != nil {
		return nil, err
	}

	result, ok := encoded.(map[any]any)
	if !ok {
		return nil, fmt.Errorf("expected encoded body to be map[any]any, got %T", encoded)
	}

	return result, nil
}
