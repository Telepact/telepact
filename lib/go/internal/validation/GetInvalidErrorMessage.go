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
	"github.com/telepact/telepact/lib/go/internal/types"
	telepact "github.com/telepact/telepact/lib/go/pkg"
)

// GetInvalidErrorMessage mirrors the Python helper for constructing an error message from validation failures.
func GetInvalidErrorMessage(errorKey string, validationFailures []*types.ValidationFailure, resultUnionType *types.TUnion, responseHeaders map[string]any) (telepact.Message, error) {
	validationFailureCases := types.MapValidationFailuresToInvalidFieldCases(validationFailures)

	newErrorResult := map[string]any{
		errorKey: map[string]any{
			"cases": validationFailureCases,
		},
	}

	if err := ValidateResult(resultUnionType, newErrorResult); err != nil {
		return telepact.Message{}, err
	}

	return telepact.NewMessage(responseHeaders, newErrorResult), nil
}
