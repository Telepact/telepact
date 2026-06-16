//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import "sync"

var (
	mockTelepactJSON     string
	mockTelepactJSONOnce sync.Once
)

// GetMockTelepactJSON returns the bundled Telepact mock schema JSON content.
func GetMockTelepactJSON() string {
	mockTelepactJSONOnce.Do(func() {
		content, err := loadBundledSchema("mock-internal.telepact.json")
		if err != nil {
			panic(err)
		}
		mockTelepactJSON = content
	})
	return mockTelepactJSON
}
