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

// ParseError represents a collection of schema parse failures.
type ParseError struct {
    Failures     []*SchemaParseFailure
    DocumentJSON map[string]string
}

// Error implements the error interface.
func (e *ParseError) Error() string {
    if e == nil {
        return ""
    }
    return "telepact: schema parse failure"
}
