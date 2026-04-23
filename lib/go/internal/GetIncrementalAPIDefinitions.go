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
	"regexp"
	"sort"
	"strings"
)

var entrypointPrefixes = []string{"info.", "headers.", "errors.", "fn."}
var customTypePrefixes = []string{"fn.", "struct.", "union.", "headers.", "errors.", "info.", "_ext."}

// GetAPIEntrypointDefinitions returns only top-level schema entrypoint definitions.
func GetAPIEntrypointDefinitions(schema SchemaAccessor, includeInternal bool) []any {
	definitions := schema.OriginalDefinitions()
	if includeInternal {
		definitions = schema.FullDefinitions()
	}

	result := make([]any, 0)
	for _, definition := range definitions {
		definitionMap := toStringAnyMap(definition)
		if definitionMap == nil {
			continue
		}
		schemaKey := getSchemaKey(definitionMap)
		if hasPrefix(schemaKey, entrypointPrefixes) {
			result = append(result, definition)
		}
	}
	return result
}

// GetAPIDefinitionsBySchemaKey returns a definition and its transitive dependencies.
func GetAPIDefinitionsBySchemaKey(schema SchemaAccessor, schemaKey string, includeInternal bool) []any {
	definitions := schema.OriginalDefinitions()
	if includeInternal {
		definitions = schema.FullDefinitions()
	}

	definitionsByKey := make(map[string]map[string]any, len(definitions))
	for _, definition := range definitions {
		definitionMap := toStringAnyMap(definition)
		if definitionMap == nil {
			continue
		}
		definitionsByKey[getSchemaKey(definitionMap)] = definitionMap
	}
	if _, ok := definitionsByKey[schemaKey]; !ok {
		return nil
	}

	includedSchemaKeys := make(map[string]struct{})
	pendingSchemaKeys := []string{schemaKey}
	for len(pendingSchemaKeys) > 0 {
		currentSchemaKey := pendingSchemaKeys[len(pendingSchemaKeys)-1]
		pendingSchemaKeys = pendingSchemaKeys[:len(pendingSchemaKeys)-1]
		if _, seen := includedSchemaKeys[currentSchemaKey]; seen {
			continue
		}

		definitionMap := definitionsByKey[currentSchemaKey]
		if definitionMap == nil {
			continue
		}
		includedSchemaKeys[currentSchemaKey] = struct{}{}
		for _, referencedSchemaKey := range getReferencedSchemaKeys(definitionMap, definitionsByKey) {
			if _, seen := includedSchemaKeys[referencedSchemaKey]; !seen {
				pendingSchemaKeys = append(pendingSchemaKeys, referencedSchemaKey)
			}
		}
	}

	result := make([]any, 0)
	for _, definition := range definitions {
		definitionMap := toStringAnyMap(definition)
		if definitionMap == nil {
			continue
		}
		if _, ok := includedSchemaKeys[getSchemaKey(definitionMap)]; ok {
			result = append(result, definition)
		}
	}
	return result
}

func getReferencedSchemaKeys(definition map[string]any, definitionsByKey map[string]map[string]any) []string {
	references := make(map[string]struct{})
	for key, value := range definition {
		if key == "///" || key == "_errors" {
			continue
		}
		collectReferencedSchemaKeys(value, definitionsByKey, references)
	}

	errorsRegex, ok := definition["_errors"].(string)
	if ok {
		regex := regexp.MustCompile(errorsRegex)
		for schemaKey := range definitionsByKey {
			if regex.MatchString(schemaKey) {
				references[schemaKey] = struct{}{}
			}
		}
	}

	result := make([]string, 0, len(references))
	for schemaKey := range references {
		result = append(result, schemaKey)
	}
	sort.Strings(result)
	return result
}

func collectReferencedSchemaKeys(value any, definitionsByKey map[string]map[string]any, references map[string]struct{}) {
	switch typed := value.(type) {
	case string:
		schemaKey := strings.TrimSuffix(typed, "?")
		if hasPrefix(schemaKey, customTypePrefixes) {
			if _, ok := definitionsByKey[schemaKey]; ok {
				references[schemaKey] = struct{}{}
			}
		}
	case []any:
		for _, entry := range typed {
			collectReferencedSchemaKeys(entry, definitionsByKey, references)
		}
	case map[string]any:
		for key, entry := range typed {
			if key == "///" {
				continue
			}
			collectReferencedSchemaKeys(entry, definitionsByKey, references)
		}
	case map[any]any:
		collectReferencedSchemaKeys(toStringAnyMap(typed), definitionsByKey, references)
	}
}

func hasPrefix(value string, prefixes []string) bool {
	for _, prefix := range prefixes {
		if strings.HasPrefix(value, prefix) {
			return true
		}
	}
	return false
}
