//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

import telepactinternal "github.com/telepact/telepact/lib/go/internal"

func createInternalFunctionRoutes(telepactSchema *TelepactSchema) map[string]FunctionRoute {
	return map[string]FunctionRoute{
		"fn.ping_": func(_ string, _ Message) (Message, error) {
			return NewMessage(map[string]any{}, map[string]any{"Ok_": map[string]any{}}), nil
		},
		"fn.api_": func(_ string, requestMessage Message) (Message, error) {
			requestPayload, err := requestMessage.BodyPayload()
			if err != nil {
				return Message{}, err
			}

			includeInternal, _ := requestPayload["includeInternal!"].(bool)
			includeExamples, _ := requestPayload["includeExamples!"].(bool)

			apiDefinitions := telepactSchema.Original
			if includeInternal {
				apiDefinitions = telepactSchema.Full
			}
			if includeExamples {
				apiDefinitions = telepactinternal.GetAPIDefinitionsWithExamples(telepactSchema, includeInternal)
			}

			return NewMessage(map[string]any{}, map[string]any{"Ok_": map[string]any{"api": apiDefinitions}}), nil
		},
	}
}
