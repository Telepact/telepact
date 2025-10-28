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

// BinaryEncodingMissing indicates that an expected key was absent from the binary encoding map.
type BinaryEncodingMissing struct {
	Key any
}

// NewBinaryEncodingMissing constructs a BinaryEncodingMissing error for the provided key.
func NewBinaryEncodingMissing(key any) *BinaryEncodingMissing {
	return &BinaryEncodingMissing{Key: key}
}

// Error implements the error interface.
func (e *BinaryEncodingMissing) Error() string {
	if e == nil {
		return "missing binary encoding"
	}
	return fmt.Sprintf("Missing binary encoding for %v", e.Key)
}
