//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

// MapSchemaParseFailuresToPseudoJSON converts schema parse failures into pseudo JSON diagnostics.
func MapSchemaParseFailuresToPseudoJSON(schemaParseFailures []*SchemaParseFailure, telepactDocumentNameToJSON map[string]string) []map[string]any {
	pseudoJSONList := make([]map[string]any, 0, len(schemaParseFailures))
	for _, failure := range schemaParseFailures {
		if failure == nil {
			continue
		}
		location := ResolveDocumentCoordinates(append([]any{}, failure.Path...), failure.DocumentName, telepactDocumentNameToJSON)
		pseudoJSON := map[string]any{
			"document": failure.DocumentName,
			"location": location,
			"path":     append([]any{}, failure.Path...),
			"reason":   map[string]any{failure.Reason: cloneStringInterfaceMap(failure.Data)},
		}
		pseudoJSONList = append(pseudoJSONList, pseudoJSON)
	}
	return pseudoJSONList
}

func cloneStringInterfaceMap(src map[string]any) map[string]any {
	if src == nil {
		return nil
	}
	cloned := make(map[string]any, len(src))
	for k, v := range src {
		cloned[k] = v
	}
	return cloned
}
