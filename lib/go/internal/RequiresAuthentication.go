//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
