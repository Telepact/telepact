//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// TFieldDeclaration describes a struct field in a Telepact schema.
type TFieldDeclaration struct {
	FieldName       string
	TypeDeclaration *TTypeDeclaration
	Optional        bool
}

// NewTFieldDeclaration constructs a TFieldDeclaration instance.
func NewTFieldDeclaration(fieldName string, typeDeclaration *TTypeDeclaration, optional bool) *TFieldDeclaration {
	return &TFieldDeclaration{
		FieldName:       fieldName,
		TypeDeclaration: typeDeclaration,
		Optional:        optional,
	}
}
