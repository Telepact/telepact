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
