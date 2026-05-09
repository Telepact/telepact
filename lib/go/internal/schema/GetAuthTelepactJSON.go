//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import "sync"

var (
	authTelepactJSON     string
	authTelepactJSONOnce sync.Once
)

// GetAuthTelepactJSON returns the bundled Telepact auth schema JSON content.
func GetAuthTelepactJSON() string {
	authTelepactJSONOnce.Do(func() {
		content, err := loadBundledSchema("auth.telepact.json")
		if err != nil {
			panic(err)
		}
		authTelepactJSON = content
	})
	return authTelepactJSON
}
