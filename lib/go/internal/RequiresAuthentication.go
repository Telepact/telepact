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

func RequiresAuthentication(schema SchemaAccessor, functionName string) bool {
	var functionDefinition map[string]any
	for _, definition := range schema.FullDefinitions() {
		definitionMap, ok := definition.(map[string]any)
		if !ok {
			continue
		}
		if _, exists := definitionMap[functionName]; !exists {
			continue
		}
		functionDefinition = definitionMap
		break
	}

	if functionName == "" || functionName[len(functionName)-1] == '_' {
		return false
	}
	if internal, ok := functionDefinition["$internal"].(bool); ok && internal {
		return false
	}
	if _, exists := schema.ParsedDefinitions()["union.Auth_"]; !exists {
		return false
	}
	if authenticated, ok := functionDefinition["$authenticated"].(bool); ok && !authenticated {
		return false
	}
	return true
}
