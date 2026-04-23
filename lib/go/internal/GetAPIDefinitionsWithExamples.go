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

package internal

import (
	"encoding/base64"
	"encoding/binary"
	"fmt"
	"sort"
	"strings"

	"github.com/telepact/telepact/lib/go/internal/types"
)

const exampleCollectionLength = 2

var exampleRandomWords = []string{
	"alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
	"iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi",
	"rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega",
}

type apiExampleRandomGenerator struct {
	seed                int32
	collectionLengthMin int
	collectionLengthMax int
}

func newAPIExampleRandomGenerator() *apiExampleRandomGenerator {
	random := &apiExampleRandomGenerator{
		collectionLengthMin: exampleCollectionLength,
		collectionLengthMax: exampleCollectionLength,
	}
	random.SetSeed(0)
	return random
}

func (r *apiExampleRandomGenerator) SetSeed(seed int32) {
	if seed == 0 {
		r.seed = 1
		return
	}
	r.seed = seed
}

func (r *apiExampleRandomGenerator) NextInt() int {
	x := r.seed
	x ^= x << 16
	x ^= x >> 11
	x ^= x << 5
	if x == 0 {
		x = 1
	}
	r.seed = x
	return int(x & 0x7fffffff)
}

func (r *apiExampleRandomGenerator) NextIntWithCeiling(ceiling int) int {
	if ceiling == 0 {
		return 0
	}
	return r.NextInt() % ceiling
}

func (r *apiExampleRandomGenerator) NextBoolean() bool {
	return r.NextIntWithCeiling(31) > 15
}

func (r *apiExampleRandomGenerator) NextString() string {
	return exampleRandomWords[r.NextIntWithCeiling(len(exampleRandomWords))]
}

func (r *apiExampleRandomGenerator) NextCollectionLength() int {
	offset := r.collectionLengthMax - r.collectionLengthMin
	if offset <= 0 {
		return r.collectionLengthMin
	}
	return r.NextIntWithCeiling(offset) + r.collectionLengthMin
}

func (r *apiExampleRandomGenerator) NextBytes() []byte {
	bytes := make([]byte, 4)
	binary.BigEndian.PutUint32(bytes, uint32(r.NextInt()))
	return bytes
}

func (r *apiExampleRandomGenerator) NextDouble() float64 {
	return float64(r.NextInt()&0x7fffffff) / float64(0x7fffffff)
}

// GetAPIDefinitionsWithExamples returns schema definitions annotated with deterministic example payloads.
func GetAPIDefinitionsWithExamples(schema SchemaAccessor, includeInternal bool) []any {
	definitions := schema.OriginalDefinitions()
	if includeInternal {
		definitions = schema.FullDefinitions()
	}

	defaultFnScope := getDefaultFnScope(schema.ParsedDefinitions())
	result := make([]any, 0, len(definitions))
	for _, definition := range definitions {
		definitionMap, ok := definition.(map[string]any)
		if !ok {
			result = append(result, definition)
			continue
		}
		result = append(result, addExamplesToDefinition(definitionMap, schema, defaultFnScope))
	}

	return result
}

// GetDefinitionExample returns example payload fields for a single schema definition.
func GetDefinitionExample(schema SchemaAccessor, name string, includeInternal bool) map[string]any {
	if !includeInternal && strings.HasSuffix(name, "_") {
		return map[string]any{}
	}

	definitions := schema.OriginalDefinitions()
	if includeInternal {
		definitions = schema.FullDefinitions()
	}

	for _, definition := range definitions {
		definitionMap := toStringAnyMap(definition)
		if getSchemaKey(definitionMap) != name {
			continue
		}

		exampleDefinition := addExamplesToDefinition(
			definitionMap,
			schema,
			getDefaultFnScope(schema.ParsedDefinitions()),
		)
		result := map[string]any{}
		for _, key := range []string{"example", "inputExample", "outputExample"} {
			if value, ok := exampleDefinition[key]; ok {
				result[key] = value
			}
		}
		return result
	}

	return map[string]any{}
}

func addExamplesToDefinition(
	definition map[string]any,
	schema SchemaAccessor,
	defaultFnScope string,
) map[string]any {
	schemaKey := getSchemaKey(definition)
	clonedDefinition := cloneStringAnyMap(definition)

	if strings.HasPrefix(schemaKey, "info.") {
		clonedDefinition["example"] = map[string]any{}
		return clonedDefinition
	}

	randomGenerator := newAPIExampleRandomGenerator()

	if strings.HasPrefix(schemaKey, "fn.") {
		ctx := types.NewGenerateContext(true, false, true, schemaKey, randomGenerator)
		clonedDefinition["inputExample"] = normalizeExampleValue(
			schema.ParsedDefinitions()[schemaKey].GenerateRandomValue(nil, false, nil, ctx),
		)
		clonedDefinition["outputExample"] = normalizeExampleValue(
			schema.ParsedDefinitions()[schemaKey+".->"].GenerateRandomValue(nil, false, nil, ctx),
		)
		return clonedDefinition
	}

	if strings.HasPrefix(schemaKey, "headers.") {
		ctx := types.NewGenerateContext(true, false, true, defaultFnScope, randomGenerator)
		clonedDefinition["inputExample"] = generateHeaderExample(
			toStringAnyMap(definition[schemaKey]),
			schema.RequestHeaderDeclarations(),
			ctx,
		)
		clonedDefinition["outputExample"] = generateHeaderExample(
			toStringAnyMap(definition["->"]),
			schema.ResponseHeaderDeclarations(),
			ctx,
		)
		return clonedDefinition
	}

	if strings.HasPrefix(schemaKey, "errors.") {
		ctx := types.NewGenerateContext(true, false, true, defaultFnScope, randomGenerator)
		clonedDefinition["example"] = generateRawUnionExample(
			toAnySlice(definition[schemaKey]),
			schema,
			ctx,
		)
		return clonedDefinition
	}

	ctx := types.NewGenerateContext(true, false, true, defaultFnScope, randomGenerator)
	clonedDefinition["example"] = normalizeExampleValue(
		schema.ParsedDefinitions()[schemaKey].GenerateRandomValue(nil, false, nil, ctx),
	)
	return clonedDefinition
}

func generateHeaderExample(
	headerDefinition map[string]any,
	parsedHeaders map[string]*types.TFieldDeclaration,
	ctx *types.GenerateContext,
) map[string]any {
	if headerDefinition == nil {
		return map[string]any{}
	}

	headerNames := make([]string, 0, len(headerDefinition))
	for headerName := range headerDefinition {
		headerNames = append(headerNames, headerName)
	}
	sort.Strings(headerNames)

	example := make(map[string]any, len(headerNames))
	for _, headerName := range headerNames {
		example[headerName] = normalizeExampleValue(
			parsedHeaders[headerName].TypeDeclaration.GenerateRandomValue(nil, false, ctx),
		)
	}

	return example
}

func generateRawUnionExample(
	unionDefinition []any,
	schema SchemaAccessor,
	ctx *types.GenerateContext,
) map[string]any {
	type tagDefinition struct {
		name    string
		payload map[string]any
	}

	tags := make([]tagDefinition, 0, len(unionDefinition))
	for _, entry := range unionDefinition {
		tagMap := toStringAnyMap(entry)
		for key, value := range tagMap {
			if key == "///" {
				continue
			}
			tags = append(tags, tagDefinition{
				name:    key,
				payload: toStringAnyMap(value),
			})
			break
		}
	}

	sort.Slice(tags, func(i, j int) bool {
		return tags[i].name < tags[j].name
	})

	tag := tags[ctx.RandomGenerator.NextIntWithCeiling(len(tags))]
	return map[string]any{
		tag.name: generateRawStructExample(tag.payload, schema, ctx),
	}
}

func generateRawStructExample(
	structDefinition map[string]any,
	schema SchemaAccessor,
	ctx *types.GenerateContext,
) map[string]any {
	fieldNames := make([]string, 0, len(structDefinition))
	for fieldName := range structDefinition {
		fieldNames = append(fieldNames, fieldName)
	}
	sort.Strings(fieldNames)

	example := make(map[string]any)
	for _, fieldName := range fieldNames {
		optional := strings.HasSuffix(fieldName, "!")
		if optional {
			if !ctx.IncludeOptionalFields || (ctx.RandomizeOptionalFields && ctx.RandomGenerator.NextBoolean()) {
				continue
			}
		} else if !ctx.AlwaysIncludeRequiredFields && ctx.RandomGenerator.NextBoolean() {
			continue
		}

		example[fieldName] = generateRawTypeExample(structDefinition[fieldName], schema, ctx)
	}

	return example
}

func generateRawTypeExample(
	typeExpression any,
	schema SchemaAccessor,
	ctx *types.GenerateContext,
) any {
	switch typed := typeExpression.(type) {
	case string:
		nullable := strings.HasSuffix(typed, "?")
		nonNullableTypeExpression := typed
		if nullable {
			nonNullableTypeExpression = strings.TrimSuffix(typed, "?")
			if ctx.RandomGenerator.NextBoolean() {
				return nil
			}
		}

		switch nonNullableTypeExpression {
		case "boolean":
			return ctx.RandomGenerator.NextBoolean()
		case "integer":
			return ctx.RandomGenerator.NextInt()
		case "number":
			return ctx.RandomGenerator.NextDouble()
		case "string":
			return ctx.RandomGenerator.NextString()
		case "any":
			selectType := ctx.RandomGenerator.NextIntWithCeiling(3)
			switch selectType {
			case 0:
				return ctx.RandomGenerator.NextBoolean()
			case 1:
				return ctx.RandomGenerator.NextInt()
			default:
				return ctx.RandomGenerator.NextString()
			}
		case "bytes":
			return base64.StdEncoding.EncodeToString(ctx.RandomGenerator.NextBytes())
		default:
			return normalizeExampleValue(
				schema.ParsedDefinitions()[nonNullableTypeExpression].GenerateRandomValue(nil, false, nil, ctx),
			)
		}

	case []any:
		length := ctx.RandomGenerator.NextCollectionLength()
		example := make([]any, 0, length)
		for i := 0; i < length; i += 1 {
			example = append(example, generateRawTypeExample(typed[0], schema, ctx))
		}
		return example

	case map[string]any:
		if len(typed) == 1 {
			if nestedType, ok := typed["string"]; ok {
				length := ctx.RandomGenerator.NextCollectionLength()
				example := make(map[string]any)
				for i := 0; i < length; i += 1 {
					example[ctx.RandomGenerator.NextString()] = generateRawTypeExample(nestedType, schema, ctx)
				}
				return example
			}
		}
	case map[any]any:
		return generateRawTypeExample(toStringAnyMap(typed), schema, ctx)
	}

	return nil
}

func normalizeExampleValue(value any) any {
	switch typed := value.(type) {
	case []byte:
		return base64.StdEncoding.EncodeToString(typed)
	case []any:
		normalized := make([]any, 0, len(typed))
		for _, entry := range typed {
			normalized = append(normalized, normalizeExampleValue(entry))
		}
		return normalized
	case map[string]any:
		normalized := make(map[string]any, len(typed))
		for key, entry := range typed {
			normalized[key] = normalizeExampleValue(entry)
		}
		return normalized
	case map[any]any:
		return normalizeExampleValue(toStringAnyMap(typed))
	default:
		return value
	}
}

func getDefaultFnScope(parsedTypes map[string]types.TType) string {
	nonInternalFunctions := make([]string, 0)
	allFunctions := make([]string, 0)

	for schemaKey := range parsedTypes {
		if !strings.HasPrefix(schemaKey, "fn.") || strings.HasSuffix(schemaKey, ".->") {
			continue
		}
		allFunctions = append(allFunctions, schemaKey)
		if !strings.HasSuffix(schemaKey, "_") {
			nonInternalFunctions = append(nonInternalFunctions, schemaKey)
		}
	}

	sort.Strings(nonInternalFunctions)
	if len(nonInternalFunctions) > 0 {
		return nonInternalFunctions[0]
	}

	sort.Strings(allFunctions)
	if len(allFunctions) > 0 {
		return allFunctions[0]
	}

	return "fn.ping_"
}

func getSchemaKey(definition map[string]any) string {
	for key := range definition {
		if key != "///" && key != "->" && key != "_errors" {
			return key
		}
	}

	panic(fmt.Errorf("telepact: schema entry has no schema key: %v", definition))
}
