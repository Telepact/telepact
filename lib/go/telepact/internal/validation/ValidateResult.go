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

package validation

import (
	"fmt"

	"github.com/telepact/telepact/lib/go/telepact"
	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// ValidateResult ensures the provided error result conforms to the union type definition.
func ValidateResult(resultUnionType *types.TUnion, errorResult map[string]any) error {
	if resultUnionType == nil {
		return telepact.NewTelepactError("result union type is nil")
	}

	validateCtx := types.NewValidateContext(nil, "", false)
	validationFailures := resultUnionType.Validate(errorResult, nil, validateCtx)
	if len(validationFailures) == 0 {
		return nil
	}

	cases := types.MapValidationFailuresToInvalidFieldCases(validationFailures)
	return telepact.NewTelepactError(fmt.Sprintf("Failed internal telepact validation: %v", cases))
}
