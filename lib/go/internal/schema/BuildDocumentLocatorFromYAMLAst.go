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

package schema

import (
	"encoding/json"
	"fmt"

	"gopkg.in/yaml.v3"
)

func createDocumentLocatorFromYAMLText(text string) (DocumentLocator, error) {
	var document yaml.Node
	if err := yaml.Unmarshal([]byte(text), &document); err != nil {
		return nil, err
	}
	if len(document.Content) == 0 {
		return nil, fmt.Errorf("YAML document cannot be empty")
	}

	if err := validateNoDuplicateYAMLKeys(document.Content[0]); err != nil {
		return nil, err
	}
	locations := map[string]map[string]any{
		serializePath(nil): coordinatesFromYAMLNode(document.Content[0]),
	}
	buildLocationsForYAMLNode(document.Content[0], nil, locations)

	return func(path []any) map[string]any {
		if location, ok := locations[SerializePathCopy(path)]; ok {
			return map[string]any{"row": location["row"], "col": location["col"]}
		}
		return defaultDocumentCoordinates()
	}, nil
}

func SerializePathCopy(path []any) string {
	if path == nil {
		path = []any{}
	}
	return serializePath(path)
}

func serializePath(path []any) string {
	if path == nil {
		path = []any{}
	}
	bytes, err := json.Marshal(path)
	if err != nil {
		return "[]"
	}
	return string(bytes)
}

func coordinatesFromYAMLNode(node *yaml.Node) map[string]any {
	if node == nil || node.Line <= 0 || node.Column <= 0 {
		return documentCoordinates(1, 1)
	}
	return map[string]any{"row": node.Line, "col": node.Column}
}

func defaultDocumentCoordinates() map[string]any {
	return documentCoordinates(1, 1)
}

func documentCoordinates(row int, col int) map[string]any {
	return map[string]any{"row": row, "col": col}
}

func buildLocationsForYAMLNode(node *yaml.Node, path []any, locations map[string]map[string]any) {
	if node == nil {
		return
	}

	switch node.Kind {
	case yaml.SequenceNode:
		for index, item := range node.Content {
			itemPath := append(append([]any{}, path...), index)
			locations[serializePath(itemPath)] = coordinatesFromYAMLNode(item)
			buildLocationsForYAMLNode(item, itemPath, locations)
		}
	case yaml.MappingNode:
		for index := 0; index+1 < len(node.Content); index += 2 {
			keyNode := node.Content[index]
			valueNode := node.Content[index+1]
			if keyNode == nil {
				continue
			}

			keyPath := append(append([]any{}, path...), keyNode.Value)
			locations[serializePath(keyPath)] = coordinatesFromYAMLNode(keyNode)
			buildLocationsForYAMLNode(valueNode, keyPath, locations)
		}
	}
}

func validateNoDuplicateYAMLKeys(node *yaml.Node) error {
	if node == nil {
		return nil
	}

	switch node.Kind {
	case yaml.SequenceNode:
		for _, child := range node.Content {
			if err := validateNoDuplicateYAMLKeys(child); err != nil {
				return err
			}
		}
	case yaml.MappingNode:
		seenKeys := map[string]struct{}{}
		for index := 0; index+1 < len(node.Content); index += 2 {
			keyNode := node.Content[index]
			valueNode := node.Content[index+1]
			key := ""
			if keyNode != nil {
				key = keyNode.Value
			}
			if _, exists := seenKeys[key]; exists {
				return fmt.Errorf("duplicate YAML key")
			}
			seenKeys[key] = struct{}{}
			if err := validateNoDuplicateYAMLKeys(valueNode); err != nil {
				return err
			}
		}
	}

	return nil
}
