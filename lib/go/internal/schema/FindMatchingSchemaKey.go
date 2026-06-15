//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import "strings"

// FindMatchingSchemaKey finds an existing schema key equivalent to the supplied key, accounting for info keys.
func FindMatchingSchemaKey(schemaKeys map[string]struct{}, schemaKey string) string {
	for key := range schemaKeys {
		if strings.HasPrefix(schemaKey, "info.") && strings.HasPrefix(key, "info.") {
			return key
		}
		if key == schemaKey {
			return key
		}
	}
	return ""
}
