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

import "github.com/telepact/telepact/lib/go/telepact/internal/schema"

// TelepactSchemaFiles holds the raw JSON contents of Telepact schema files keyed by filename.
type TelepactSchemaFiles struct {
	FilenamesToJSON map[string]string
}

// NewTelepactSchemaFiles constructs a TelepactSchemaFiles instance by reading schema files from a directory.
func NewTelepactSchemaFiles(directory string) (*TelepactSchemaFiles, error) {
	fileMap, err := schema.GetSchemaFileMap(directory)
	if err != nil {
		return nil, err
	}

	return &TelepactSchemaFiles{
		FilenamesToJSON: fileMap,
	}, nil
}
