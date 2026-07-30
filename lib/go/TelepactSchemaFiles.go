//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

import "github.com/telepact/telepact/lib/go/internal/schema"

// TelepactSchemaFiles holds the raw JSON contents of Telepact schema files keyed by filename.
type TelepactSchemaFiles struct {
	FilenamesToJSON map[string]string
}

// NewTelepactSchemaFiles constructs a TelepactSchemaFiles instance by reading schema files from a directory.
func NewTelepactSchemaFiles(directory string) (*TelepactSchemaFiles, error) {
	fileMap, parseFailures, err := schema.GetSchemaFileMap(directory)
	if err != nil {
		return nil, err
	}
	if len(parseFailures) > 0 {
		return nil, NewTelepactSchemaParseError(parseFailures, fileMap)
	}

	return &TelepactSchemaFiles{
		FilenamesToJSON: fileMap,
	}, nil
}
