//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package validation

import (
	"fmt"

	telepact "github.com/telepact/telepact/lib/go"
	"github.com/telepact/telepact/lib/go/internal/types"
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
