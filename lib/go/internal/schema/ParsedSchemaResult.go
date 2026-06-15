//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import "github.com/telepact/telepact/lib/go/internal/types"

// ParsedSchemaResult contains the parsed schema artifacts required to construct a Telepact schema.
type ParsedSchemaResult struct {
	Original              []any
	Full                  []any
	Parsed                map[string]types.TType
	ParsedRequestHeaders  map[string]*types.TFieldDeclaration
	ParsedResponseHeaders map[string]*types.TFieldDeclaration
}
