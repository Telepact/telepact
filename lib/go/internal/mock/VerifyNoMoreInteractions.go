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
