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
	"strings"
)

func GetIndexEntries(schema SchemaAccessor, includeInternal bool) []any {
	definitions := schema.OriginalDefinitions()
	if includeInternal {
		definitions = schema.FullDefinitions()
	}

	entries := make([]any, 0)
	for _, definition := range definitions {
		definitionMap := toStringAnyMap(definition)
		schemaKey := getSchemaKey(definitionMap)
		if !strings.HasPrefix(schemaKey, "fn.") || strings.HasSuffix(schemaKey, ".->") {
			continue
		}
		if !includeInternal && strings.HasSuffix(schemaKey, "_") {
			continue
		}

		entry := map[string]any{"name": schemaKey}
		if comment, ok := definitionMap["///"]; ok {
			entry["comment!"] = comment
		}
		entries = append(entries, entry)
	}

	return entries
}

func GetDefinitionClosure(schema SchemaAccessor, name string, includeInternal bool) []any {
	rootDefinition := getRootDefinition(schema, name, includeInternal)
	if rootDefinition == nil {
		return []any{}
	}

	definitionsByName := map[string]map[string]any{}
	for _, definition := range schema.FullDefinitions() {
		definitionMap := toStringAnyMap(definition)
		definitionsByName[getSchemaKey(definitionMap)] = definitionMap
	}

	visited := map[string]bool{}
	var visit func(schemaKey string)
	visit = func(schemaKey string) {
		if visited[schemaKey] {
			return
		}

		definition, ok := definitionsByName[schemaKey]
		if !ok {
			return
		}

		visited[schemaKey] = true
		for _, reference := range getDefinitionReferences(definition, definitionsByName) {
			visit(reference)
		}
	}

	visit(getSchemaKey(rootDefinition))

	closure := make([]any, 0)
	for _, definition := range schema.FullDefinitions() {
		definitionMap := toStringAnyMap(definition)
		if visited[getSchemaKey(definitionMap)] {
			closure = append(closure, definition)
		}
	}

	return closure
}

func getRootDefinition(schema SchemaAccessor, name string, includeInternal bool) map[string]any {
	if !includeInternal && strings.HasSuffix(name, "_") {
		return nil
	}

	definitions := schema.OriginalDefinitions()
	if includeInternal {
		definitions = schema.FullDefinitions()
	}

	for _, definition := range definitions {
		definitionMap := toStringAnyMap(definition)
		if getSchemaKey(definitionMap) == name {
			return definitionMap
		}
	}

	return nil
}

func getDefinitionReferences(definition map[string]any, definitionsByName map[string]map[string]any) []string {
	references := map[string]bool{}
	schemaKey := getSchemaKey(definition)

	for key, value := range definition {
		switch key {
		case "///":
			continue
		case "_errors":
			regexString, ok := value.(string)
			if !ok {
				continue
			}
			regex, err := regexp.Compile(regexString)
			if err != nil {
				continue
			}
			for candidate := range definitionsByName {
				if regex.MatchString(candidate) {
					references[candidate] = true
				}
			}
		case schemaKey, "->":
			for _, reference := range getTypeExpressionReferences(value, definitionsByName) {
				references[reference] = true
			}
		}
	}

	result := make([]string, 0, len(references))
	for reference := range references {
		result = append(result, reference)
	}
	return result
}

func getTypeExpressionReferences(typeExpression any, definitionsByName map[string]map[string]any) []string {
	references := map[string]bool{}

	switch value := typeExpression.(type) {
	case string:
		schemaKey := strings.TrimSuffix(value, "?")
		if _, ok := definitionsByName[schemaKey]; ok {
			references[schemaKey] = true
		}
	case []any:
		if isUnionDefinition(value) {
			for _, tagDefinition := range value {
				tagMap := toStringAnyMap(tagDefinition)
				for key, entry := range tagMap {
					if key == "///" {
						continue
					}
					for _, reference := range getTypeExpressionReferences(entry, definitionsByName) {
						references[reference] = true
					}
				}
			}
		} else if len(value) > 0 {
			for _, reference := range getTypeExpressionReferences(value[0], definitionsByName) {
				references[reference] = true
			}
		}
	case map[string]any:
		if len(value) == 1 {
			if objectValue, ok := value["string"]; ok {
				for _, reference := range getTypeExpressionReferences(objectValue, definitionsByName) {
					references[reference] = true
				}
				break
			}
		}
		for _, entry := range value {
			for _, reference := range getTypeExpressionReferences(entry, definitionsByName) {
				references[reference] = true
			}
		}
	}

	result := make([]string, 0, len(references))
	for reference := range references {
		result = append(result, reference)
	}
	return result
}

func isUnionDefinition(typeExpression []any) bool {
	if len(typeExpression) == 0 {
		return false
	}

	for _, entry := range typeExpression {
		tagMap := toStringAnyMap(entry)
		if tagMap == nil {
			return false
		}

		nonCommentKeys := 0
		for key, value := range tagMap {
			if key == "///" {
				continue
			}
			if toStringAnyMap(value) == nil {
				return false
			}
			nonCommentKeys += 1
		}
		if nonCommentKeys != 1 {
			return false
		}
	}

	return true
}
