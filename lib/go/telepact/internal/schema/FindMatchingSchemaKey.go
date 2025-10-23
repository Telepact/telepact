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
