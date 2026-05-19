//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import (
	"embed"
	"fmt"
	"path"
)

//go:embed do_not_edit/*.json
var embeddedSchemas embed.FS

func loadBundledSchema(filename string) (string, error) {
	bytes, err := embeddedSchemas.ReadFile(path.Join("do_not_edit", filename))
	if err != nil {
		return "", fmt.Errorf("telepact: failed to read bundled schema %s: %w", filename, err)
	}

	return string(bytes), nil
}
