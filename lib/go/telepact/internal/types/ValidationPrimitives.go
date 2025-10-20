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
	"encoding/base64"
	"math"
	"reflect"
)

// ValidateBoolean validates that the value is a boolean.
func ValidateBoolean(value any) []*ValidationFailure {
	if _, ok := value.(bool); ok {
		return nil
	}
	return GetTypeUnexpectedValidationFailure(nil, value, booleanName)
}

// ValidateNumber ensures the value is an integer or floating point number.
func ValidateNumber(value any, ctx *ValidateContext) []*ValidationFailure {
	switch v := value.(type) {
	case int:
		return validateSignedInt(int64(v))
	case int8:
		return validateSignedInt(int64(v))
	case int16:
		return validateSignedInt(int64(v))
	case int32:
		return validateSignedInt(int64(v))
	case int64:
		return validateSignedInt(v)
	case uint:
		if v > math.MaxInt64 {
			return []*ValidationFailure{NewValidationFailure(nil, "NumberOutOfRange", map[string]any{})}
		}
		return nil
	case uint8:
		return nil
	case uint16:
		return nil
	case uint32:
		if uint64(v) > uint64(math.MaxInt64) {
			return []*ValidationFailure{NewValidationFailure(nil, "NumberOutOfRange", map[string]any{})}
		}
		return nil
	case uint64:
		if v > uint64(math.MaxInt64) {
			return []*ValidationFailure{NewValidationFailure(nil, "NumberOutOfRange", map[string]any{})}
		}
		return nil
	case float32, float64:
		return nil
	default:
		return GetTypeUnexpectedValidationFailure(nil, value, numberName)
	}
}

// ValidateInteger ensures the value is an integer within 64-bit range.
func ValidateInteger(value any) []*ValidationFailure {
	switch v := value.(type) {
	case int:
		return validateSignedInt(int64(v))
	case int8:
		return validateSignedInt(int64(v))
	case int16:
		return validateSignedInt(int64(v))
	case int32:
		return validateSignedInt(int64(v))
	case int64:
		return validateSignedInt(v)
	default:
		return GetTypeUnexpectedValidationFailure(nil, value, integerName)
	}
}

func validateSignedInt(v int64) []*ValidationFailure {
	if v > math.MaxInt64 || v < math.MinInt64 {
		return []*ValidationFailure{NewValidationFailure(nil, "NumberOutOfRange", map[string]any{})}
	}
	return nil
}

// ValidateString ensures the value is a string.
func ValidateString(value any) []*ValidationFailure {
	if _, ok := value.(string); ok {
		return nil
	}
	return GetTypeUnexpectedValidationFailure(nil, value, stringName)
}

// ValidateNull ensures the value is nil.
func ValidateNull(value any, ctx *ValidateContext) []*ValidationFailure {
	if value == nil {
		return nil
	}
	return GetTypeUnexpectedValidationFailure(nil, value, "Null")
}

// ValidateBytes validates base64 strings or raw byte slices depending on context.
func ValidateBytes(value any, ctx *ValidateContext) []*ValidationFailure {
	if _, ok := value.([]byte); ok {
		if ctx != nil && ctx.CoerceBase64 {
			setCoercedPath(ctx.Path, ctx.Base64Coercions)
		}
		return nil
	}

	if str, ok := value.(string); ok {
		_, err := base64.StdEncoding.DecodeString(str)
		if err != nil {
			return GetTypeUnexpectedValidationFailure(nil, value, "Base64String")
		}
		if ctx != nil && !ctx.CoerceBase64 {
			setCoercedPath(ctx.Path, ctx.BytesCoercions)
		}
		return nil
	}

	return GetTypeUnexpectedValidationFailure(nil, value, bytesName)
}

func setCoercedPath(path []string, coercedPath map[string]any) {
	if len(path) == 0 {
		return
	}

	part := path[0]
	if len(path) == 1 {
		coercedPath[part] = true
		return
	}

	next, ok := coercedPath[part]
	if !ok {
		next = map[string]any{}
		coercedPath[part] = next
	}

	nextMap, ok := next.(map[string]any)
	if !ok {
		nextMap = map[string]any{}
		coercedPath[part] = nextMap
	}
	setCoercedPath(path[1:], nextMap)
}

// ValidateArray validates array values by delegating to the nested type declaration.
func ValidateArray(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	if value == nil {
		return GetTypeUnexpectedValidationFailure(nil, value, arrayName)
	}

	rv := reflect.ValueOf(value)
	kind := rv.Kind()

	if kind != reflect.Array && kind != reflect.Slice {
		return GetTypeUnexpectedValidationFailure(nil, value, arrayName)
	}

	// Prevent treating []byte as array because that's handled by ValidateBytes.
	if rv.Type().Elem().Kind() == reflect.Uint8 {
		return GetTypeUnexpectedValidationFailure(nil, value, arrayName)
	}

	nested := typeParameters[0]
	failures := make([]*ValidationFailure, 0)

	for i := 0; i < rv.Len(); i++ {
		element := rv.Index(i).Interface()
		if ctx != nil {
			ctx.Path = append(ctx.Path, "*")
		}
		nestedFailures := nested.Validate(element, ctx)
		if ctx != nil && len(ctx.Path) > 0 {
			ctx.Path = ctx.Path[:len(ctx.Path)-1]
		}
		failures = append(failures, prependPathToFailures(nestedFailures, i)...)
	}

	return failures
}

// ValidateObject validates object/map values by delegating to the nested type.
func ValidateObject(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	if value == nil {
		return GetTypeUnexpectedValidationFailure(nil, value, objectName)
	}

	rv := reflect.ValueOf(value)
	if rv.Kind() != reflect.Map {
		return GetTypeUnexpectedValidationFailure(nil, value, objectName)
	}

	nested := typeParameters[0]
	failures := make([]*ValidationFailure, 0)

	for _, key := range rv.MapKeys() {
		entryValue := rv.MapIndex(key).Interface()
		if ctx != nil {
			ctx.Path = append(ctx.Path, "*")
		}
		nestedFailures := nested.Validate(entryValue, ctx)
		if ctx != nil && len(ctx.Path) > 0 {
			ctx.Path = ctx.Path[:len(ctx.Path)-1]
		}
		failures = append(failures, prependPathToFailures(nestedFailures, key.Interface())...)
	}

	return failures
}

// ValidateOptional validates optional values; nil is always accepted.
func ValidateOptional(value any, t TType, ctx *ValidateContext) []*ValidationFailure {
	if value == nil {
		return nil
	}
	if t == nil {
		return nil
	}
	return t.Validate(value, nil, ctx)
}

// ValidateValueOfType validates the supplied value against a type declaration, respecting nullability.
func ValidateValueOfType(value any, thisType TType, nullable bool, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	if value == nil {
		if !nullable {
			expected := "Unknown"
			if thisType != nil {
				expected = thisType.GetName(ctx)
			}
			return GetTypeUnexpectedValidationFailure(nil, value, expected)
		}
		return nil
	}

	if thisType == nil {
		return nil
	}

	return thisType.Validate(value, typeParameters, ctx)
}
