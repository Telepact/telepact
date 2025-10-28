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

// DecodeBody decodes a binary-encoded message body into pseudo-JSON using the provided BinaryEncoding.
func DecodeBody(encodedBody map[any]any, encoding *BinaryEncoding) (map[string]any, error) {
	decoded, err := DecodeKeys(encodedBody, encoding)
	if err != nil {
		return nil, err
	}

	result, ok := decoded.(map[string]any)
	if !ok {
		return nil, fmt.Errorf("expected decoded body to be map[string]any, got %T", decoded)
	}

	return result, nil
}
