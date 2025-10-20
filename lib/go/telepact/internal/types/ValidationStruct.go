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
	"reflect"
	"sort"
	"strings"
)

// ValidateStruct mirrors the Python behaviour for struct validation.
func ValidateStruct(value any, name string, fields map[string]*TFieldDeclaration, ctx *ValidateContext) []*ValidationFailure {
	actualMap, ok := coerceToStringAnyMap(value)
	if !ok {
		return GetTypeUnexpectedValidationFailure(nil, value, structName)
	}

	var selectedFields []string
	if ctx != nil && ctx.Select != nil {
		if rawSelected, found := ctx.Select[name]; found {
			selectedFields = toStringSlice(rawSelected)
		}
	}

	return validateStructFields(fields, selectedFields, actualMap, ctx)
}

func validateStructFields(fields map[string]*TFieldDeclaration, selectedFields []string, actual map[string]any, ctx *ValidateContext) []*ValidationFailure {
	failures := make([]*ValidationFailure, 0)

	selectedSet := make(map[string]struct{}, len(selectedFields))
	for _, field := range selectedFields {
		selectedSet[field] = struct{}{}
	}

	missingFields := make([]string, 0)
	for fieldName, fieldDecl := range fields {
		_, hasValue := actual[fieldName]
		_, selected := selectedSet[fieldName]
		isOmittedBySelect := selectedFields != nil && !selected
		if !hasValue && !fieldDecl.Optional && !isOmittedBySelect {
			missingFields = append(missingFields, fieldName)
		}
	}

	sort.Strings(missingFields)
	for _, missing := range missingFields {
		failures = append(failures, NewValidationFailure(nil, "RequiredObjectKeyMissing", map[string]any{"key": missing}))
	}

	for fieldName, fieldValue := range actual {
		referenceField, exists := fields[fieldName]
		if !exists {
			failures = append(failures, NewValidationFailure([]any{fieldName}, "ObjectKeyDisallowed", map[string]any{}))
			continue
		}

		if ctx != nil {
			ctx.Path = append(ctx.Path, fieldName)
		}
		nestedFailures := referenceField.TypeDeclaration.Validate(fieldValue, ctx)
		if ctx != nil && len(ctx.Path) > 0 {
			ctx.Path = ctx.Path[:len(ctx.Path)-1]
		}
		failures = append(failures, prependPathToFailures(nestedFailures, fieldName)...)
	}

	return failures
}

// ValidateUnion mirrors the Python implementation for union validation.
func ValidateUnion(value any, name string, tags map[string]*TStruct, ctx *ValidateContext) []*ValidationFailure {
	actualMap, ok := coerceToStringAnyMap(value)
	if !ok {
		return GetTypeUnexpectedValidationFailure(nil, value, unionName)
	}

	var selectedTags map[string]any
	if ctx != nil && ctx.Select != nil {
		if strings.HasPrefix(name, "fn.") {
			selected := any(nil)
			if ctx.Select != nil {
				selected = ctx.Select[name]
			}
			selectedTags = map[string]any{name: selected}
		} else {
			if raw, found := ctx.Select[name]; found {
				if castMap, ok := raw.(map[string]any); ok {
					selectedTags = castMap
				}
			}
		}
	}

	return validateUnionTags(tags, selectedTags, actualMap, ctx)
}

func validateUnionTags(referenceTags map[string]*TStruct, selectedTags map[string]any, actual map[string]any, ctx *ValidateContext) []*ValidationFailure {
	if len(actual) != 1 {
		return []*ValidationFailure{NewValidationFailure(nil, "ObjectSizeUnexpected", map[string]any{"actual": len(actual), "expected": 1})}
	}

	var unionTarget string
	var unionPayload any
	for key, val := range actual {
		unionTarget = key
		unionPayload = val
		break
	}

	referenceStruct := referenceTags[unionTarget]
	if referenceStruct == nil {
		return []*ValidationFailure{NewValidationFailure([]any{unionTarget}, "ObjectKeyDisallowed", map[string]any{})}
	}

	payloadMap, ok := coerceToStringAnyMap(unionPayload)
	if !ok {
		return GetTypeUnexpectedValidationFailure([]any{unionTarget}, unionPayload, objectName)
	}

	var structSelectedFields []string
	if selectedTags != nil {
		if raw, found := selectedTags[unionTarget]; found {
			structSelectedFields = toStringSlice(raw)
		}
	}

	if ctx != nil {
		ctx.Path = append(ctx.Path, unionTarget)
	}
	nestedFailures := validateStructFields(referenceStruct.Fields, structSelectedFields, payloadMap, ctx)
	if ctx != nil && len(ctx.Path) > 0 {
		ctx.Path = ctx.Path[:len(ctx.Path)-1]
	}

	return prependPathToFailures(nestedFailures, unionTarget)
}

// ValidateSelect mirrors the Python select validation behaviour.
func ValidateSelect(givenObj any, possibleSelects map[string]any, ctx *ValidateContext) []*ValidationFailure {
	actualMap, ok := coerceToStringAnyMap(givenObj)
	if !ok {
		return GetTypeUnexpectedValidationFailure(nil, givenObj, objectName)
	}

	if ctx == nil || ctx.Fn == "" {
		return nil
	}

	possibleSelect := possibleSelects[ctx.Fn]
	return isSubSelect([]any{}, actualMap, possibleSelect)
}

func isSubSelect(path []any, givenObj any, possibleSection any) []*ValidationFailure {
	switch allowed := possibleSection.(type) {
	case []any:
		givenSlice, ok := coerceToInterfaceSlice(givenObj)
		if !ok {
			return GetTypeUnexpectedValidationFailure(path, givenObj, arrayName)
		}

		failures := make([]*ValidationFailure, 0)
		allowedSet := make(map[any]struct{}, len(allowed))
		for _, v := range allowed {
			allowedSet[v] = struct{}{}
		}
		for index, element := range givenSlice {
			if _, ok := allowedSet[element]; !ok {
				failures = append(failures, NewValidationFailure(append(clonePath(path), index), "ArrayElementDisallowed", map[string]any{}))
			}
		}
		return failures
	case map[string]any:
		givenMap, ok := coerceToStringAnyMap(givenObj)
		if !ok {
			return GetTypeUnexpectedValidationFailure(path, givenObj, objectName)
		}

		failures := make([]*ValidationFailure, 0)
		for key, value := range givenMap {
			allowedSub, exists := allowed[key]
			if !exists {
				failures = append(failures, NewValidationFailure(append(clonePath(path), key), "ObjectKeyDisallowed", map[string]any{}))
				continue
			}
			childFailures := isSubSelect(append(clonePath(path), key), value, allowedSub)
			failures = append(failures, childFailures...)
		}
		return failures
	default:
		return nil
	}
}

// toStringAnyMap attempts to coerce common map representations to map[string]any.
func coerceToStringAnyMap(value any) (map[string]any, bool) {
	switch typed := value.(type) {
	case map[string]any:
		return typed, true
	case map[string]string:
		converted := make(map[string]any, len(typed))
		for k, v := range typed {
			converted[k] = v
		}
		return converted, true
	case map[string]int:
		converted := make(map[string]any, len(typed))
		for k, v := range typed {
			converted[k] = v
		}
		return converted, true
	default:
		rv := reflect.ValueOf(value)
		if rv.IsValid() && rv.Kind() == reflect.Map && rv.Type().Key().Kind() == reflect.String {
			converted := make(map[string]any, rv.Len())
			for _, key := range rv.MapKeys() {
				converted[key.String()] = rv.MapIndex(key).Interface()
			}
			return converted, true
		}
		return nil, false
	}
}

func coerceToInterfaceSlice(value any) ([]any, bool) {
	switch typed := value.(type) {
	case []any:
		return typed, true
	case []string:
		result := make([]any, len(typed))
		for i, v := range typed {
			result[i] = v
		}
		return result, true
	case []int:
		result := make([]any, len(typed))
		for i, v := range typed {
			result[i] = v
		}
		return result, true
	}

	rv := reflect.ValueOf(value)
	if rv.IsValid() && (rv.Kind() == reflect.Slice || rv.Kind() == reflect.Array) {
		if rv.Type().Elem().Kind() == reflect.Uint8 {
			return nil, false
		}
		result := make([]any, rv.Len())
		for i := 0; i < rv.Len(); i++ {
			result[i] = rv.Index(i).Interface()
		}
		return result, true
	}
	return nil, false
}

func toStringSlice(value any) []string {
	if value == nil {
		return nil
	}
	switch typed := value.(type) {
	case []string:
		return append([]string{}, typed...)
	case []any:
		result := make([]string, 0, len(typed))
		for _, v := range typed {
			if str, ok := v.(string); ok {
				result = append(result, str)
			}
		}
		return result
	default:
		return nil
	}
}

func clonePath(path []any) []any {
	if len(path) == 0 {
		return nil
	}
	out := make([]any, len(path))
	copy(out, path)
	return out
}
