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

package types

import (
	"regexp"
	"sort"
)

const (
	mockFunctionRegex = "^fn\\..*$"
	resultKey         = "->"
)

// ValidateMockCall mirrors the Python implementation for validating mock call payloads.
func ValidateMockCall(givenObj any, typesMap map[string]TType, ctx *ValidateContext) []*ValidationFailure {
	givenMap, ok := coerceToStringAnyMap(givenObj)
	if !ok {
		return GetTypeUnexpectedValidationFailure(nil, givenObj, objectName)
	}

	keys := make([]string, 0, len(givenMap))
	for key := range givenMap {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	re := regexp.MustCompile(mockFunctionRegex)
	matches := make([]string, 0)
	for _, key := range keys {
		if re.MatchString(key) {
			matches = append(matches, key)
		}
	}

	if len(matches) != 1 {
		return []*ValidationFailure{NewValidationFailure(nil, "ObjectKeyRegexMatchCountUnexpected", map[string]any{
			"regex":    mockFunctionRegex,
			"actual":   len(matches),
			"expected": 1,
			"keys":     keys,
		})}
	}

	functionName := matches[0]
	functionType, _ := typesMap[functionName].(*TUnion)
	if functionType == nil {
		return []*ValidationFailure{NewValidationFailure([]any{functionName}, "ObjectKeyDisallowed", map[string]any{})}
	}

	input := givenMap[functionName]
	structType := functionType.Tags[functionName]
	if structType == nil {
		return []*ValidationFailure{NewValidationFailure([]any{functionName}, "ObjectKeyDisallowed", map[string]any{})}
	}

	inputFailures := structType.Validate(input, nil, ctx)
	inputFailuresWithPath := prependPathToFailures(inputFailures, functionName)

	filtered := make([]*ValidationFailure, 0, len(inputFailuresWithPath))
	for _, failure := range inputFailuresWithPath {
		if failure.Reason == "RequiredObjectKeyMissing" {
			continue
		}
		filtered = append(filtered, failure)
	}

	sortValidationFailures(filtered)
	return filtered
}

// ValidateMockStub mirrors the Python implementation for validating mock stub payloads.
func ValidateMockStub(givenObj any, typesMap map[string]TType, ctx *ValidateContext) []*ValidationFailure {
	givenMap, ok := coerceToStringAnyMap(givenObj)
	if !ok {
		return GetTypeUnexpectedValidationFailure(nil, givenObj, objectName)
	}

	keys := make([]string, 0, len(givenMap))
	for key := range givenMap {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	re := regexp.MustCompile(mockFunctionRegex)
	matches := make([]string, 0)
	for _, key := range keys {
		if re.MatchString(key) {
			matches = append(matches, key)
		}
	}

	if len(matches) != 1 {
		return []*ValidationFailure{NewValidationFailure(nil, "ObjectKeyRegexMatchCountUnexpected", map[string]any{
			"regex":    mockFunctionRegex,
			"actual":   len(matches),
			"expected": 1,
			"keys":     keys,
		})}
	}

	functionName := matches[0]
	input := givenMap[functionName]

	functionCallUnion, _ := typesMap[functionName].(*TUnion)
	if functionCallUnion == nil {
		return []*ValidationFailure{NewValidationFailure([]any{functionName}, "ObjectKeyDisallowed", map[string]any{})}
	}

	callStruct := functionCallUnion.Tags[functionName]
	if callStruct == nil {
		return []*ValidationFailure{NewValidationFailure([]any{functionName}, "ObjectKeyDisallowed", map[string]any{})}
	}

	inputFailures := callStruct.Validate(input, nil, ctx)
	inputFailures = prependPathToFailures(inputFailures, functionName)
	filtered := make([]*ValidationFailure, 0, len(inputFailures))
	for _, failure := range inputFailures {
		if failure.Reason == "RequiredObjectKeyMissing" {
			continue
		}
		filtered = append(filtered, failure)
	}

	resultUnionKey := functionName + ".->"
	functionResultUnion, _ := typesMap[resultUnionKey].(*TUnion)
	failures := make([]*ValidationFailure, 0)
	failures = append(failures, filtered...)

	if functionResultUnion == nil {
		failures = append(failures, NewValidationFailure([]any{resultKey}, "ObjectKeyDisallowed", map[string]any{}))
	} else {
		output, hasOutput := givenMap[resultKey]
		if !hasOutput {
			failures = append(failures, NewValidationFailure(nil, "RequiredObjectKeyMissing", map[string]any{"key": resultKey}))
		} else {
			outputFailures := functionResultUnion.Validate(output, nil, ctx)
			outputFailures = prependPathToFailures(outputFailures, resultKey)
			for _, failure := range outputFailures {
				if failure.Reason == "RequiredObjectKeyMissing" {
					continue
				}
				failures = append(failures, failure)
			}
		}
	}

	for _, key := range keys {
		if key == functionName || key == resultKey {
			continue
		}
		if re.MatchString(key) {
			continue
		}
		failures = append(failures, NewValidationFailure([]any{key}, "ObjectKeyDisallowed", map[string]any{}))
	}

	sortValidationFailures(failures)
	return failures
}
