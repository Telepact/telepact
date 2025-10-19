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

package telepact

import (
	"bytes"
	"encoding/json"
	"testing"
)

func TestDefaultSerializationJSONRoundTrip(t *testing.T) {
	serialization := NewDefaultSerialization()
	input := map[string]any{"headers": map[string]any{"trace": "abc"}}

	encoded, err := serialization.ToJSON(input)
	if err != nil {
		t.Fatalf("unexpected error encoding JSON: %v", err)
	}

	decoded, err := serialization.FromJSON(encoded)
	if err != nil {
		t.Fatalf("unexpected error decoding JSON: %v", err)
	}

	assertPseudoJSONEqual(t, input, decoded)
}

func TestDefaultSerializationMsgpackRoundTrip(t *testing.T) {
	serialization := NewDefaultSerialization()
	input := map[string]any{
		"headers": map[string]any{"trace": "abc"},
		"body":    map[string]any{"call": map[string]any{"arg": 1}},
	}

	encoded, err := serialization.ToMsgpack(input)
	if err != nil {
		t.Fatalf("unexpected error encoding msgpack: %v", err)
	}

	decoded, err := serialization.FromMsgpack(encoded)
	if err != nil {
		t.Fatalf("unexpected error decoding msgpack: %v", err)
	}

	assertPseudoJSONEqual(t, input, decoded)
}

func assertPseudoJSONEqual(t *testing.T, expected any, actual any) {
	t.Helper()

	left, err := json.Marshal(normalizePseudoJSON(expected))
	if err != nil {
		t.Fatalf("marshal expected: %v", err)
	}
	right, err := json.Marshal(normalizePseudoJSON(actual))
	if err != nil {
		t.Fatalf("marshal actual: %v", err)
	}

	if !bytes.Equal(left, right) {
		t.Fatalf("pseudo JSON mismatch:\nexpected: %s\nactual:   %s", left, right)
	}
}
