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
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

// GetSchemaFileMap reads Telepact schema resources beneath directory and returns their contents, along with any schema parse failures.
func GetSchemaFileMap(directory string) (map[string]string, []*SchemaParseFailure, error) {
	finalJSONDocuments := make(map[string]string)
	parseFailures := make([]*SchemaParseFailure, 0)

	err := filepath.WalkDir(directory, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}

		relativePath, err := filepath.Rel(directory, path)
		if err != nil {
			return err
		}

		if d.IsDir() {
			if relativePath == "." {
				return nil
			}
			parseFailures = append(parseFailures, NewSchemaParseFailure(relativePath, nil, "DirectoryDisallowed", map[string]any{}))
			finalJSONDocuments[relativePath] = "[]"
			return nil
		}

		content, err := os.ReadFile(path)
		if err != nil {
			return err
		}

		if !strings.HasSuffix(relativePath, ".telepact.json") {
			parseFailures = append(parseFailures, NewSchemaParseFailure(relativePath, nil, "FileNamePatternInvalid", map[string]any{"expected": "*.telepact.json"}))
		}

		finalJSONDocuments[relativePath] = string(content)
		return nil
	})

	if err != nil {
		return nil, nil, err
	}

	return finalJSONDocuments, parseFailures, nil
}
