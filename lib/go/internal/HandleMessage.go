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

package internal

import (
	"fmt"

	"github.com/telepact/telepact/lib/go/internal/binary"
	"github.com/telepact/telepact/lib/go/internal/types"
)

// HandleMessage mirrors the Python server handler orchestration using primitive maps.
func HandleMessage(
	requestMessage ServerMessage,
	overrideHeaders map[string]any,
	schema SchemaAccessor,
	handler func(ServerMessage) (ServerMessage, error),
	onError func(error),
) (ServerMessage, error) {
	if schema == nil {
		return ServerMessage{}, fmt.Errorf("telepact: schema must not be nil")
	}
	if handler == nil {
		return ServerMessage{}, fmt.Errorf("telepact: handler must not be nil")
	}

	requestHeaders := requestMessage.Headers
	if requestHeaders == nil {
		requestHeaders = make(map[string]any)
	}
	requestBody := requestMessage.Body
	if requestBody == nil {
		requestBody = make(map[string]any)
	}

	if overrideHeaders == nil {
		overrideHeaders = map[string]any{}
	}

	responseHeaders := make(map[string]any)
	for key, value := range overrideHeaders {
		requestHeaders[key] = value
	}

	requestTargetInit, requestPayload, err := firstServerMessageEntry(requestBody)
	if err != nil {
		return ServerMessage{}, err
	}

	parsed := schema.ParsedDefinitions()
	if parsed == nil {
		return ServerMessage{}, fmt.Errorf("telepact: schema missing parsed definitions")
	}

	requestTarget := requestTargetInit
	unknownTarget := ""
	if _, ok := parsed[requestTargetInit]; !ok {
		unknownTarget = requestTargetInit
		requestTarget = "fn.ping_"
	}

	callUnion, err := lookupUnionType(parsed, requestTarget)
	if err != nil {
		return ServerMessage{}, err
	}

	resultUnionType, err := lookupUnionType(parsed, requestTarget+".->")
	if err != nil {
		return ServerMessage{}, err
	}

	if callID, ok := requestHeaders["@id_"]; ok && callID != nil {
		responseHeaders["@id_"] = callID
	}

	if parseFailuresRaw, ok := requestHeaders["_parseFailures"]; ok {
		parseFailures := convertToAnySlice(parseFailuresRaw)
		newErrorResult := map[string]any{
			"ErrorParseFailure_": map[string]any{
				"reasons": parseFailures,
			},
		}
		if err := validateResult(resultUnionType, newErrorResult); err != nil {
			return ServerMessage{}, err
		}
		return ServerMessage{Headers: cloneStringAnyMap(responseHeaders), Body: newErrorResult}, nil
	}

	if unknownTarget != "" {
		newErrorResult := map[string]any{
			"ErrorInvalidRequestBody_": map[string]any{
				"cases": []any{
					map[string]any{
						"path":   []any{unknownTarget},
						"reason": map[string]any{"FunctionUnknown": map[string]any{}},
					},
				},
			},
		}
		if err := validateResult(resultUnionType, newErrorResult); err != nil {
			return ServerMessage{}, err
		}
		return ServerMessage{Headers: cloneStringAnyMap(responseHeaders), Body: newErrorResult}, nil
	}

	functionName := requestTarget

	requestHeaderFailures := types.ValidateHeaders(requestHeaders, schema.RequestHeaderDeclarations(), functionName)
	if len(requestHeaderFailures) > 0 {
		invalidMessage, err := buildInvalidErrorMessage("ErrorInvalidRequestHeaders_", requestHeaderFailures, resultUnionType, responseHeaders)
		return invalidMessage, err
	}

	if clientKnownRaw, ok := requestHeaders["@bin_"]; ok {
		responseHeaders["@binary_"] = true
		responseHeaders["@clientKnownBinaryChecksums_"] = convertToAnySlice(clientKnownRaw)
		if pac, ok := requestHeaders["@pac_"]; ok {
			responseHeaders["@pac_"] = pac
		}
	}

	selectStructFields := extractSelectStructFields(requestHeaders["@select_"])

	callValidateCtx := types.NewValidateContext(nil, functionName, false)
	callValidationFailures := callUnion.Validate(requestBody, nil, callValidateCtx)
	if len(callValidationFailures) > 0 {
		invalidMessage, err := buildInvalidErrorMessage("ErrorInvalidRequestBody_", callValidationFailures, resultUnionType, responseHeaders)
		return invalidMessage, err
	}

	if len(callValidateCtx.BytesCoercions) > 0 {
		if err := binary.ServerBase64Decode(requestBody, callValidateCtx.BytesCoercions); err != nil {
			return ServerMessage{}, err
		}
	}

	unsafeResponseEnabled := boolValue(requestHeaders["@unsafe_"])

	callMessage := ServerMessage{
		Headers: requestHeaders,
		Body:    map[string]any{requestTarget: requestPayload},
	}

	var resultMessage ServerMessage
	switch functionName {
	case "fn.ping_":
		resultMessage = ServerMessage{Headers: make(map[string]any), Body: map[string]any{"Ok_": map[string]any{}}}
	case "fn.api_":
		resultMessage = ServerMessage{Headers: make(map[string]any), Body: map[string]any{"Ok_": map[string]any{"api": schema.OriginalDefinitions()}}}
	default:
		resp, err := handler(callMessage)
		if err != nil {
			invokeOnError(onError, err)
			return ServerMessage{Headers: cloneStringAnyMap(responseHeaders), Body: map[string]any{"ErrorUnknown_": map[string]any{}}}, nil
		}
		resultMessage = resp
	}

	if resultMessage.Headers == nil {
		resultMessage.Headers = make(map[string]any)
	}
	for key, value := range responseHeaders {
		resultMessage.Headers[key] = value
	}

	finalResponseHeaders := resultMessage.Headers
	resultUnion := resultMessage.Body
	if resultUnion == nil {
		resultUnion = make(map[string]any)
	}

	skipResultValidation := unsafeResponseEnabled
	coerceBase64 := !boolValue(finalResponseHeaders["@binary_"])

	resultValidateCtx := types.NewValidateContext(selectStructFields, functionName, coerceBase64)
	resultValidationFailures := resultUnionType.Validate(resultUnion, nil, resultValidateCtx)
	if len(resultValidationFailures) > 0 && !skipResultValidation {
		invalidMessage, err := buildInvalidErrorMessage("ErrorInvalidResponseBody_", resultValidationFailures, resultUnionType, finalResponseHeaders)
		if err == nil {
			invokeOnError(onError, fmt.Errorf("Response validation failed: %v. Actual response: %v", resultValidationFailures, resultUnion))
		}
		return invalidMessage, err
	}

	if len(resultValidateCtx.Base64Coercions) > 0 {
		finalResponseHeaders["@base64_"] = resultValidateCtx.Base64Coercions
	}
	if len(resultValidateCtx.BytesCoercions) > 0 {
		if err := binary.ServerBase64Decode(resultUnion, resultValidateCtx.BytesCoercions); err != nil {
			return ServerMessage{}, err
		}
	}

	responseHeaderFailures := types.ValidateHeaders(finalResponseHeaders, schema.ResponseHeaderDeclarations(), functionName)
	if len(responseHeaderFailures) > 0 {
		invalidMessage, err := buildInvalidErrorMessage("ErrorInvalidResponseHeaders_", responseHeaderFailures, resultUnionType, responseHeaders)
		return invalidMessage, err
	}

	finalResultUnion := resultUnion
	if selectStructFields != nil {
		selected := SelectStructFields(types.NewTTypeDeclaration(resultUnionType, false, nil), resultUnion, selectStructFields)
		if converted := convertToStringAnyMap(selected); converted != nil {
			finalResultUnion = converted
		}
	}

	return ServerMessage{Headers: finalResponseHeaders, Body: finalResultUnion}, nil
}

func firstServerMessageEntry(body map[string]any) (string, any, error) {
	for key, value := range body {
		return key, value, nil
	}
	return "", nil, fmt.Errorf("telepact: message body missing target entry")
}

func lookupUnionType(parsed map[string]types.TType, key string) (*types.TUnion, error) {
	definition, ok := parsed[key]
	if !ok || definition == nil {
		return nil, fmt.Errorf("telepact: schema missing definition for %s", key)
	}
	union, ok := definition.(*types.TUnion)
	if !ok || union == nil {
		return nil, fmt.Errorf("telepact: definition for %s is not a union", key)
	}
	return union, nil
}

func extractSelectStructFields(value any) map[string]any {
	switch typed := value.(type) {
	case map[string]any:
		return typed
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for key, val := range typed {
			converted[fmt.Sprint(key)] = val
		}
		return converted
	default:
		return nil
	}
}

func boolValue(value any) bool {
	if flag, ok := value.(bool); ok {
		return flag
	}
	return false
}

func invokeOnError(callback func(error), err error) {
	if callback == nil || err == nil {
		return
	}
	defer func() { _ = recover() }()
	callback(err)
}

func buildInvalidErrorMessage(
	errorKey string,
	validationFailures []*types.ValidationFailure,
	resultUnionType *types.TUnion,
	responseHeaders map[string]any,
) (ServerMessage, error) {
	cases := types.MapValidationFailuresToInvalidFieldCases(validationFailures)
	newErrorResult := map[string]any{
		errorKey: map[string]any{
			"cases": cases,
		},
	}
	if err := validateResult(resultUnionType, newErrorResult); err != nil {
		return ServerMessage{}, err
	}
	return ServerMessage{Headers: cloneStringAnyMap(responseHeaders), Body: newErrorResult}, nil
}

func validateResult(resultUnionType *types.TUnion, errorResult map[string]any) error {
	if resultUnionType == nil {
		return fmt.Errorf("telepact: result union type is nil")
	}
	ctx := types.NewValidateContext(nil, "", false)
	validationFailures := resultUnionType.Validate(errorResult, nil, ctx)
	if len(validationFailures) == 0 {
		return nil
	}
	cases := types.MapValidationFailuresToInvalidFieldCases(validationFailures)
	return fmt.Errorf("telepact: failed internal validation: %v", cases)
}

func convertToAnySlice(value any) []any {
	switch typed := value.(type) {
	case nil:
		return nil
	case []any:
		return typed
	case []string:
		result := make([]any, len(typed))
		for i, entry := range typed {
			result[i] = entry
		}
		return result
	case []int:
		result := make([]any, len(typed))
		for i, entry := range typed {
			result[i] = entry
		}
		return result
	default:
		return []any{typed}
	}
}

func convertToStringAnyMap(value any) map[string]any {
	switch typed := value.(type) {
	case nil:
		return nil
	case map[string]any:
		return typed
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for key, val := range typed {
			converted[fmt.Sprint(key)] = val
		}
		return converted
	default:
		return nil
	}
}
