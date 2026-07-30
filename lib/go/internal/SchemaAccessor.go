//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package internal

import "github.com/telepact/telepact/lib/go/internal/types"

// SchemaAccessor exposes the Telepact schema details required by server helpers.
type SchemaAccessor interface {
	ParsedDefinitions() map[string]types.TType
	RequestHeaderDeclarations() map[string]*types.TFieldDeclaration
	ResponseHeaderDeclarations() map[string]*types.TFieldDeclaration
	OriginalDefinitions() []any
	FullDefinitions() []any
}
