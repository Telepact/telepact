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
