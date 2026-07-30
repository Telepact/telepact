//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package mock

// VerifyNoMoreInteractions ensures that all recorded mock invocations have been verified.
func VerifyNoMoreInteractions(invocations []*MockInvocation) map[string]any {
	unverified := make([]map[string]any, 0)
	for _, invocation := range invocations {
		if invocation == nil || invocation.Verified {
			continue
		}

		unverified = append(unverified, map[string]any{
			invocation.FunctionName: invocation.FunctionArgument,
		})
	}

	if len(unverified) == 0 {
		return map[string]any{"Ok_": map[string]any{}}
	}

	return map[string]any{
		"ErrorVerificationFailure": map[string]any{
			"additionalUnverifiedCalls": unverified,
		},
	}
}
