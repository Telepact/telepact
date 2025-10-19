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

package telepact

// TelepactError indicates a critical failure in Telepact processing logic.
type TelepactError struct {
	message string
}

// NewTelepactError constructs a new TelepactError with the given message.
func NewTelepactError(message string) *TelepactError {
	return &TelepactError{message: message}
}

// Error implements the error interface.
func (e *TelepactError) Error() string {
	if e == nil {
		return "<nil>"
	}
	if e.message == "" {
		return "telepact error"
	}
	return e.message
}
