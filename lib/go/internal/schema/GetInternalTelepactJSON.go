//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import "sync"

var (
	internalTelepactJSON     string
	internalTelepactJSONOnce sync.Once
)

// GetInternalTelepactJSON returns the bundled Telepact internal schema JSON content.
func GetInternalTelepactJSON() string {
	internalTelepactJSONOnce.Do(func() {
		content, err := loadBundledSchema("internal.telepact.json")
		if err != nil {
			panic(err)
		}
		internalTelepactJSON = content
	})
	return internalTelepactJSON
}
