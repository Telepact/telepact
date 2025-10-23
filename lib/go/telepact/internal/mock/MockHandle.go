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

import (
	"fmt"
	"reflect"
	"strings"

	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

type seedableRandomGenerator interface {
	types.RandomGenerator
	SetSeed(int32)
}

// MockHandle processes a Telepact mock request and produces response headers and body content.
func MockHandle(
	headers map[string]any,
	functionName string,
	argument map[string]any,
	stubs *[]*MockStub,
	invocations *[]*MockInvocation,
	random seedableRandomGenerator,
	parsed map[string]types.TType,
	enableGeneratedDefaultStub bool,
	enableOptionalFieldGeneration bool,
	randomizeOptionalFieldGeneration bool,
) (map[string]any, map[string]any, error) {
	if stubs == nil || invocations == nil {
		return nil, nil, fmt.Errorf("telepact: mock handle requires stub and invocation storage")
	}

	enableGenerationStub := boolValue(headers["@gen_"])

	switch functionName {
	case "fn.createStub_":
		return handleCreateStub(argument, stubs)
	case "fn.verify_":
		return map[string]any{}, handleVerify(argument, *invocations), nil
	case "fn.verifyNoMoreInteractions_":
		return map[string]any{}, VerifyNoMoreInteractions(*invocations), nil
	case "fn.clearCalls_":
		*invocations = (*invocations)[:0]
		return map[string]any{}, map[string]any{"Ok_": map[string]any{}}, nil
	case "fn.clearStubs_":
		*stubs = (*stubs)[:0]
		return map[string]any{}, map[string]any{"Ok_": map[string]any{}}, nil
	case "fn.setRandomSeed_":
		if random == nil {
			return nil, nil, fmt.Errorf("telepact: random generator unavailable")
		}
		seedValue, ok := argument["seed"]
		if !ok {
			return nil, nil, fmt.Errorf("telepact: setRandomSeed request missing seed")
		}
		random.SetSeed(int32(toInt(seedValue)))
		return map[string]any{}, map[string]any{"Ok_": map[string]any{}}, nil
	}

	*invocations = append(*invocations, NewMockInvocation(functionName, cloneStringAnyMap(argument)))

	definition := lookupUnionDefinition(parsed, functionName)

	if definition != nil {
		for _, stub := range *stubs {
			if stub == nil || stub.Count == 0 || stub.WhenFunction != functionName {
				continue
			}

			matches := false
			if stub.AllowArgumentPartialMatch {
				matches = IsSubMap(stub.WhenArgument, argument)
			} else {
				matches = reflect.DeepEqual(stub.WhenArgument, argument)
			}

			if matches {
				resultBody, err := generateStubResult(definition, stub.ThenResult, functionName, random, randomizeOptionalFieldGeneration)
				if err != nil {
					return nil, nil, err
				}
				if stub.Count > 0 {
					stub.Count--
				}
				return map[string]any{}, resultBody, nil
			}
		}
	}

	if !enableGeneratedDefaultStub && !enableGenerationStub {
		return map[string]any{}, map[string]any{"ErrorNoMatchingStub_": map[string]any{}}, nil
	}

	if definition == nil {
		return nil, nil, fmt.Errorf("unexpected unknown function: %s", functionName)
	}

	okStructRef, ok := definition.Tags["Ok_"]
	if !ok || okStructRef == nil {
		return nil, nil, fmt.Errorf("telepact: union type missing Ok_ tag")
	}

	// The Python implementation always enables optional field generation for the
	// auto-generated Ok_ stub response, regardless of the server option. We
	// mirror that behavior here to keep the port faithful.
	includeOptionalFields := true
	_ = enableOptionalFieldGeneration

	ctx := types.NewGenerateContext(
		includeOptionalFields,
		randomizeOptionalFieldGeneration,
		true,
		functionName,
		random,
	)

	randomOkStruct := okStructRef.GenerateRandomValue(map[string]any{}, true, nil, ctx)
	okBody, ok := toStringAnyMap(randomOkStruct)
	if !ok {
		return nil, nil, fmt.Errorf("telepact: generated Ok_ struct was not an object")
	}

	return map[string]any{}, map[string]any{"Ok_": okBody}, nil
}

func handleCreateStub(argument map[string]any, stubs *[]*MockStub) (map[string]any, map[string]any, error) {
	if argument == nil {
		return nil, nil, fmt.Errorf("telepact: createStub request missing stub argument")
	}

	stubValue, ok := argument["stub"]
	if !ok {
		return nil, nil, fmt.Errorf("telepact: createStub request missing stub definition")
	}

	givenStub, ok := toStringAnyMap(stubValue)
	if !ok {
		return nil, nil, fmt.Errorf("telepact: stub definition must be an object")
	}

	stubFunctionName := ""
	stubArgument := map[string]any{}
	for key, value := range givenStub {
		if strings.HasPrefix(key, "fn.") {
			stubFunctionName = key
			if converted, ok := toStringAnyMap(value); ok {
				stubArgument = cloneStringAnyMap(converted)
			}
			break
		}
	}

	if stubFunctionName == "" {
		return nil, nil, fmt.Errorf("telepact: stub definition missing function call")
	}

	stubResult := map[string]any{}
	if stubResultRaw, ok := givenStub["->"]; ok {
		if converted, ok := toStringAnyMap(stubResultRaw); ok {
			stubResult = cloneStringAnyMap(converted)
		}
	}

	allowArgumentPartialMatch := !boolValue(argument["strictMatch!"])
	stubCount := -1
	if countRaw, ok := argument["count!"]; ok {
		stubCount = toInt(countRaw)
	}

	stub := NewMockStub(stubFunctionName, stubArgument, stubResult, allowArgumentPartialMatch, stubCount)
	*stubs = append([]*MockStub{stub}, *stubs...)

	return map[string]any{}, map[string]any{"Ok_": map[string]any{}}, nil
}

func handleVerify(argument map[string]any, invocations []*MockInvocation) map[string]any {
	if argument == nil {
		return map[string]any{"ErrorVerificationFailure": map[string]any{"reason": "missing call argument"}}
	}

	givenCallRaw, ok := argument["call"]
	if !ok {
		return map[string]any{"ErrorVerificationFailure": map[string]any{"reason": "missing call definition"}}
	}

	givenCall, ok := toStringAnyMap(givenCallRaw)
	if !ok {
		return map[string]any{"ErrorVerificationFailure": map[string]any{"reason": "call definition must be an object"}}
	}

	callFunctionName := ""
	callArgument := map[string]any{}
	for key, value := range givenCall {
		if strings.HasPrefix(key, "fn.") {
			callFunctionName = key
			if converted, ok := toStringAnyMap(value); ok {
				callArgument = cloneStringAnyMap(converted)
			}
			break
		}
	}

	if callFunctionName == "" {
		return map[string]any{"ErrorVerificationFailure": map[string]any{"reason": "missing function call"}}
	}

	verifyTimes := map[string]any{"AtLeast": map[string]any{"times": 1}}
	if verifyTimesRaw, ok := argument["count!"]; ok {
		if converted, ok := toStringAnyMap(verifyTimesRaw); ok {
			verifyTimes = cloneStringAnyMap(converted)
		}
	}

	strictMatch := boolValue(argument["strictMatch!"])

	return Verify(callFunctionName, callArgument, strictMatch, verifyTimes, invocations)
}

func lookupUnionDefinition(parsed map[string]types.TType, functionName string) *types.TUnion {
	if parsed == nil {
		return nil
	}

	definition, ok := parsed[functionName+".->"]
	if !ok || definition == nil {
		return nil
	}

	if union, ok := definition.(*types.TUnion); ok {
		return union
	}
	return nil
}

func generateStubResult(
	definition *types.TUnion,
	blueprint map[string]any,
	functionName string,
	random types.RandomGenerator,
	randomizeOptionalFieldGeneration bool,
) (map[string]any, error) {
	if definition == nil {
		return nil, fmt.Errorf("telepact: missing result union definition")
	}

	ctx := types.NewGenerateContext(
		false,
		randomizeOptionalFieldGeneration,
		true,
		functionName,
		random,
	)

	generated := definition.GenerateRandomValue(blueprint, true, nil, ctx)
	resultMap, ok := toStringAnyMap(generated)
	if !ok {
		return nil, fmt.Errorf("telepact: generated stub result was not an object")
	}
	return resultMap, nil
}

func boolValue(value any) bool {
	if flag, ok := value.(bool); ok {
		return flag
	}
	return false
}

func cloneStringAnyMap(source map[string]any) map[string]any {
	if source == nil {
		return map[string]any{}
	}
	clone := make(map[string]any, len(source))
	for key, value := range source {
		clone[key] = value
	}
	return clone
}
