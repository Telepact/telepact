//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package mock

import "reflect"

// Verify inspects recorded mock invocations and produces verification metadata mirroring Telepact's Python implementation.
func Verify(
	functionName string,
	argument map[string]any,
	exactMatch bool,
	verificationTimes map[string]any,
	invocations []*MockInvocation,
) map[string]any {
	matchesFound := 0

	for _, invocation := range invocations {
		if invocation == nil || invocation.FunctionName != functionName {
			continue
		}

		if exactMatch {
			if reflect.DeepEqual(invocation.FunctionArgument, argument) {
				invocation.Verified = true
				matchesFound++
			}
			continue
		}

		if IsSubMap(argument, invocation.FunctionArgument) {
			invocation.Verified = true
			matchesFound++
		}
	}

	allCallsPseudoJSON := make([]any, 0, len(invocations))
	for _, invocation := range invocations {
		if invocation == nil {
			continue
		}
		allCallsPseudoJSON = append(allCallsPseudoJSON, map[string]any{
			invocation.FunctionName: invocation.FunctionArgument,
		})
	}

	var verifyKey string
	var verifyTimesStruct map[string]any
	for key, raw := range verificationTimes {
		verifyKey = key
		verifyTimesStruct, _ = toStringAnyMap(raw)
		break
	}

	var verificationFailure map[string]any

	switch verifyKey {
	case "Exact":
		times := toInt(verifyTimesStruct["times"])
		if matchesFound > times {
			verificationFailure = map[string]any{
				"TooManyMatchingCalls": map[string]any{
					"wanted":   map[string]any{"Exact": map[string]any{"times": times}},
					"found":    matchesFound,
					"allCalls": allCallsPseudoJSON,
				},
			}
		} else if matchesFound < times {
			verificationFailure = map[string]any{
				"TooFewMatchingCalls": map[string]any{
					"wanted":   map[string]any{"Exact": map[string]any{"times": times}},
					"found":    matchesFound,
					"allCalls": allCallsPseudoJSON,
				},
			}
		}
	case "AtMost":
		times := toInt(verifyTimesStruct["times"])
		if matchesFound > times {
			verificationFailure = map[string]any{
				"TooManyMatchingCalls": map[string]any{
					"wanted":   map[string]any{"AtMost": map[string]any{"times": times}},
					"found":    matchesFound,
					"allCalls": allCallsPseudoJSON,
				},
			}
		}
	case "AtLeast":
		times := toInt(verifyTimesStruct["times"])
		if matchesFound < times {
			verificationFailure = map[string]any{
				"TooFewMatchingCalls": map[string]any{
					"wanted":   map[string]any{"AtLeast": map[string]any{"times": times}},
					"found":    matchesFound,
					"allCalls": allCallsPseudoJSON,
				},
			}
		}
	}

	if verificationFailure == nil {
		return map[string]any{"Ok_": map[string]any{}}
	}

	return map[string]any{
		"ErrorVerificationFailure": map[string]any{
			"reason": verificationFailure,
		},
	}
}

func toInt(value any) int {
	switch typed := value.(type) {
	case int:
		return typed
	case int32:
		return int(typed)
	case int64:
		return int(typed)
	case float32:
		return int(typed)
	case float64:
		return int(typed)
	default:
		return 0
	}
}
