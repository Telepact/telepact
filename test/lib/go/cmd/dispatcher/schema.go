package main

import (
	"encoding/json"
	"errors"
	"fmt"

	telepact "github.com/telepact/telepact/lib/go/telepact"
	gen "github.com/telepact/telepact/test/lib/go/cmd/dispatcher/gen"
)

type codeGenHandler struct {
	handler *gen.TypedServerHandler
}

func newCodeGenHandler(enabled bool) *codeGenHandler {
	if !enabled {
		return nil
	}
	impl := &typedCodeGenServer{}
	return &codeGenHandler{handler: gen.NewTypedServerHandler(impl)}
}

func (c *codeGenHandler) Handle(message telepact.Message) (telepact.Message, error) {
	if c == nil || c.handler == nil {
		return message, nil
	}

	response, err := c.handler.Handler(message)
	if err != nil {
		return telepact.Message{}, err
	}

	headers := response.Headers
	if headers == nil {
		headers = map[string]any{}
	}
	headers["@codegens_"] = true

	return telepact.NewMessage(headers, response.Body), nil
}

type typedCodeGenServer struct{}

func (s *typedCodeGenServer) CircularLink1(headers map[string]any, input gen.CircularLink1Input) (telepact.TypedMessage[gen.CircularLink1Output], error) {
	return telepact.TypedMessage[gen.CircularLink1Output]{}, telepact.NewTelepactError("generated server circularLink1 not implemented")
}

func (s *typedCodeGenServer) CircularLink2(headers map[string]any, input gen.CircularLink2Input) (telepact.TypedMessage[gen.CircularLink2Output], error) {
	return telepact.TypedMessage[gen.CircularLink2Output]{}, telepact.NewTelepactError("generated server circularLink2 not implemented")
}

func (s *typedCodeGenServer) Example(headers map[string]any, input gen.ExampleInput) (telepact.TypedMessage[gen.ExampleOutput], error) {
	return telepact.TypedMessage[gen.ExampleOutput]{}, telepact.NewTelepactError("generated server example not implemented")
}

func (s *typedCodeGenServer) GetBigList(headers map[string]any, input gen.GetBigListInput) (telepact.TypedMessage[gen.GetBigListOutput], error) {
	return telepact.TypedMessage[gen.GetBigListOutput]{}, telepact.NewTelepactError("generated server getBigList not implemented")
}

func (s *typedCodeGenServer) SelfLink(headers map[string]any, input gen.SelfLinkInput) (telepact.TypedMessage[gen.SelfLinkOutput], error) {
	return telepact.TypedMessage[gen.SelfLinkOutput]{}, telepact.NewTelepactError("generated server selfLink not implemented")
}

func (s *typedCodeGenServer) Test(headers map[string]any, input gen.TestInput) (telepact.TypedMessage[gen.TestOutput], error) {
	if boolValue(headers["@error"]) {
		body := gen.NewTestOutputFromErrorExample2(gen.NewTestOutputErrorExample2("Boom!"))
		return telepact.NewTypedMessage(map[string]any{}, body), nil
	}

	valueOpt := gen.None[gen.Value]()
	if top, ok := input.Value(); ok {
		mapped, hasValue, err := s.mapValue(top)
		if err != nil {
			return telepact.TypedMessage[gen.TestOutput]{}, err
		}
		if hasValue {
			valueOpt = gen.Some(mapped)
		}
	}

	okBody := gen.NewTestOutputOk(valueOpt)
	body := gen.NewTestOutputFromOk(okBody)

	return telepact.NewTypedMessage(map[string]any{}, body), nil
}

func (s *typedCodeGenServer) mapValue(top gen.Value) (gen.Value, bool, error) {
	if v, ok := top.Bool(); ok {
		return newValueWith("bool!", v), true, nil
	}
	if v, ok := top.NullBool(); ok {
		return newValueWith("nullBool!", pointerValue(v, func(b bool) any { return b })), true, nil
	}
	if v, ok := top.ArrBool(); ok {
		return newValueWith("arrBool!", cloneSlice(v)), true, nil
	}
	if v, ok := top.ArrNullBool(); ok {
		return newValueWith("arrNullBool!", slicePointerValue(v, func(b bool) any { return b })), true, nil
	}
	if v, ok := top.ObjBool(); ok {
		return newValueWith("objBool!", mapValueWith(v, func(b bool) any { return b })), true, nil
	}
	if v, ok := top.ObjNullBool(); ok {
		return newValueWith("objNullBool!", mapPointerValue(v, func(b bool) any { return b })), true, nil
	}
	if v, ok := top.Int(); ok {
		return newValueWith("int!", v), true, nil
	}
	if v, ok := top.NullInt(); ok {
		return newValueWith("nullInt!", pointerValue(v, func(i int) any { return i })), true, nil
	}
	if v, ok := top.ArrInt(); ok {
		return newValueWith("arrInt!", cloneSlice(v)), true, nil
	}
	if v, ok := top.ArrNullInt(); ok {
		return newValueWith("arrNullInt!", slicePointerValue(v, func(i int) any { return i })), true, nil
	}
	if v, ok := top.ObjInt(); ok {
		return newValueWith("objInt!", mapValueWith(v, func(i int) any { return i })), true, nil
	}
	if v, ok := top.ObjNullInt(); ok {
		return newValueWith("objNullInt!", mapPointerValue(v, func(i int) any { return i })), true, nil
	}
	if v, ok := top.Num(); ok {
		return newValueWith("num!", v), true, nil
	}
	if v, ok := top.NullNum(); ok {
		return newValueWith("nullNum!", pointerValue(v, func(f float64) any { return f })), true, nil
	}
	if v, ok := top.ArrNum(); ok {
		return newValueWith("arrNum!", cloneSlice(v)), true, nil
	}
	if v, ok := top.ArrNullNum(); ok {
		return newValueWith("arrNullNum!", slicePointerValue(v, func(f float64) any { return f })), true, nil
	}
	if v, ok := top.ObjNum(); ok {
		return newValueWith("objNum!", mapValueWith(v, func(f float64) any { return f })), true, nil
	}
	if v, ok := top.ObjNullNum(); ok {
		return newValueWith("objNullNum!", mapPointerValue(v, func(f float64) any { return f })), true, nil
	}
	if v, ok := top.Str(); ok {
		return newValueWith("str!", v), true, nil
	}
	if v, ok := top.NullStr(); ok {
		return newValueWith("nullStr!", pointerValue(v, func(s string) any { return s })), true, nil
	}
	if v, ok := top.ArrStr(); ok {
		return newValueWith("arrStr!", cloneSlice(v)), true, nil
	}
	if v, ok := top.ArrNullStr(); ok {
		return newValueWith("arrNullStr!", slicePointerValue(v, func(s string) any { return s })), true, nil
	}
	if v, ok := top.ObjStr(); ok {
		return newValueWith("objStr!", mapValueWith(v, func(s string) any { return s })), true, nil
	}
	if v, ok := top.ObjNullStr(); ok {
		return newValueWith("objNullStr!", mapPointerValue(v, func(s string) any { return s })), true, nil
	}
	if v, ok := top.Arr(); ok {
		return newValueWith("arr!", cloneAnySlice(v)), true, nil
	}
	if v, ok := top.ArrArr(); ok {
		converted := make([]any, len(v))
		for i, inner := range v {
			converted[i] = cloneAnySlice(inner)
		}
		return newValueWith("arrArr!", converted), true, nil
	}
	if v, ok := top.ObjArr(); ok {
		converted := make(map[string]any, len(v))
		for k, inner := range v {
			converted[k] = cloneAnySlice(inner)
		}
		return newValueWith("objArr!", converted), true, nil
	}
	if v, ok := top.Obj(); ok {
		return newValueWith("obj!", cloneStringAnyMap(v)), true, nil
	}
	if v, ok := top.ArrObj(); ok {
		converted := make([]any, len(v))
		for i, inner := range v {
			converted[i] = cloneStringAnyMap(inner)
		}
		return newValueWith("arrObj!", converted), true, nil
	}
	if v, ok := top.ObjObj(); ok {
		converted := make(map[string]any, len(v))
		for k, inner := range v {
			converted[k] = cloneStringAnyMap(inner)
		}
		return newValueWith("objObj!", converted), true, nil
	}
	if v, ok := top.Any(); ok {
		return newValueWith("any!", cloneAny(v)), true, nil
	}
	if v, ok := top.NullAny(); ok {
		return newValueWith("nullAny!", cloneAny(v)), true, nil
	}
	if v, ok := top.ArrAny(); ok {
		return newValueWith("arrAny!", cloneAnySlice(v)), true, nil
	}
	if v, ok := top.ArrNullAny(); ok {
		return newValueWith("arrNullAny!", cloneAnySlice(v)), true, nil
	}
	if v, ok := top.ObjAny(); ok {
		return newValueWith("objAny!", cloneStringAnyMap(v)), true, nil
	}
	if v, ok := top.ObjNullAny(); ok {
		return newValueWith("objNullAny!", cloneStringAnyMap(v)), true, nil
	}
	if v, ok := top.Bytes(); ok {
		return newValueWith("bytes!", cloneBytes(v)), true, nil
	}
	if v, ok := top.NullBytes(); ok {
		if v == nil {
			return newValueWith("nullBytes!", nil), true, nil
		}
		return newValueWith("nullBytes!", cloneBytes(v)), true, nil
	}
	if v, ok := top.ArrBytes(); ok {
		return newValueWith("arrBytes!", cloneBytesSlice(v)), true, nil
	}
	if v, ok := top.ArrNullBytes(); ok {
		return newValueWith("arrNullBytes!", cloneBytesSlice(v)), true, nil
	}
	if v, ok := top.ObjBytes(); ok {
		return newValueWith("objBytes!", cloneBytesMap(v)), true, nil
	}
	if v, ok := top.ObjNullBytes(); ok {
		return newValueWith("objNullBytes!", cloneBytesMap(v)), true, nil
	}
	if v, ok := top.Struct(); ok {
		mapped := s.mapStruct(v)
		return newValueWith("struct!", mapped.PseudoJSON()), true, nil
	}
	if v, ok := top.NullStruct(); ok {
		result := pointerValue(v, func(sv gen.ExStruct) any {
			mapped := s.mapStruct(sv)
			return mapped.PseudoJSON()
		})
		return newValueWith("nullStruct!", result), true, nil
	}
	if v, ok := top.ArrStruct(); ok {
		converted := make([]any, len(v))
		for i, sv := range v {
			mapped := s.mapStruct(sv)
			converted[i] = mapped.PseudoJSON()
		}
		return newValueWith("arrStruct!", converted), true, nil
	}
	if v, ok := top.ArrNullStruct(); ok {
		converted := slicePointerValue(v, func(sv gen.ExStruct) any {
			mapped := s.mapStruct(sv)
			return mapped.PseudoJSON()
		})
		return newValueWith("arrNullStruct!", converted), true, nil
	}
	if v, ok := top.ObjStruct(); ok {
		converted := make(map[string]any, len(v))
		for k, sv := range v {
			mapped := s.mapStruct(sv)
			converted[k] = mapped.PseudoJSON()
		}
		return newValueWith("objStruct!", converted), true, nil
	}
	if v, ok := top.ObjNullStruct(); ok {
		converted := mapPointerValue(v, func(sv gen.ExStruct) any {
			mapped := s.mapStruct(sv)
			return mapped.PseudoJSON()
		})
		return newValueWith("objNullStruct!", converted), true, nil
	}
	if v, ok := top.Union(); ok {
		mapped, err := s.mapUnion(v)
		if err != nil {
			return gen.Value{}, false, err
		}
		return newValueWith("union!", mapped.PseudoJSON()), true, nil
	}
	if v, ok := top.NullUnion(); ok {
		var result any
		if v != nil {
			mapped, err := s.mapUnion(*v)
			if err != nil {
				return gen.Value{}, false, err
			}
			result = mapped.PseudoJSON()
		}
		return newValueWith("nullUnion!", result), true, nil
	}
	if v, ok := top.ArrUnion(); ok {
		converted, err := s.mapUnionSlice(v)
		if err != nil {
			return gen.Value{}, false, err
		}
		return newValueWith("arrUnion!", converted), true, nil
	}
	if v, ok := top.ArrNullUnion(); ok {
		converted, err := s.mapUnionPointerSlice(v)
		if err != nil {
			return gen.Value{}, false, err
		}
		return newValueWith("arrNullUnion!", converted), true, nil
	}
	if v, ok := top.ObjUnion(); ok {
		converted, err := s.mapUnionMap(v)
		if err != nil {
			return gen.Value{}, false, err
		}
		return newValueWith("objUnion!", converted), true, nil
	}
	if v, ok := top.ObjNullUnion(); ok {
		converted, err := s.mapUnionPointerMap(v)
		if err != nil {
			return gen.Value{}, false, err
		}
		return newValueWith("objNullUnion!", converted), true, nil
	}
	if v, ok := top.Fn(); ok {
		mapped := s.mapExampleInput(v)
		return newValueWith("fn!", mapped.PseudoJSON()), true, nil
	}
	if v, ok := top.NullFn(); ok {
		result := pointerValue(v, func(fn gen.ExampleInput) any {
			mapped := s.mapExampleInput(fn)
			return mapped.PseudoJSON()
		})
		return newValueWith("nullFn!", result), true, nil
	}
	if v, ok := top.ArrFn(); ok {
		converted := make([]any, len(v))
		for i, fn := range v {
			mapped := s.mapExampleInput(fn)
			converted[i] = mapped.PseudoJSON()
		}
		return newValueWith("arrFn!", converted), true, nil
	}
	if v, ok := top.ArrNullFn(); ok {
		converted := slicePointerValue(v, func(fn gen.ExampleInput) any {
			mapped := s.mapExampleInput(fn)
			return mapped.PseudoJSON()
		})
		return newValueWith("arrNullFn!", converted), true, nil
	}
	if v, ok := top.ObjFn(); ok {
		converted := make(map[string]any, len(v))
		for k, fn := range v {
			mapped := s.mapExampleInput(fn)
			converted[k] = mapped.PseudoJSON()
		}
		return newValueWith("objFn!", converted), true, nil
	}
	if v, ok := top.ObjNullFn(); ok {
		converted := mapPointerValue(v, func(fn gen.ExampleInput) any {
			mapped := s.mapExampleInput(fn)
			return mapped.PseudoJSON()
		})
		return newValueWith("objNullFn!", converted), true, nil
	}
	if v, ok := top.Sel(); ok {
		return newValueWith("sel!", v.PseudoJSON()), true, nil
	}
	if v, ok := top.NullSel(); ok {
		result := pointerValue(v, func(sel gen.Select) any { return sel.PseudoJSON() })
		return newValueWith("nullSel!", result), true, nil
	}
	if v, ok := top.ArrSel(); ok {
		converted := make([]any, len(v))
		for i, sel := range v {
			converted[i] = sel.PseudoJSON()
		}
		return newValueWith("arrSel!", converted), true, nil
	}
	if v, ok := top.ArrNullSel(); ok {
		converted := slicePointerValue(v, func(sel gen.Select) any { return sel.PseudoJSON() })
		return newValueWith("arrNullSel!", converted), true, nil
	}
	if v, ok := top.ObjSel(); ok {
		converted := make(map[string]any, len(v))
		for k, sel := range v {
			converted[k] = sel.PseudoJSON()
		}
		return newValueWith("objSel!", converted), true, nil
	}
	if v, ok := top.ObjNullSel(); ok {
		converted := mapPointerValue(v, func(sel gen.Select) any { return sel.PseudoJSON() })
		return newValueWith("objNullSel!", converted), true, nil
	}

	return gen.Value{}, false, nil
}

func (s *typedCodeGenServer) mapStruct(value gen.ExStruct) gen.ExStruct {
	opt, hasOpt := value.Optional()
	opt2, hasOpt2 := value.Optional2()
	return gen.NewExStruct(value.Required(), toOptional(opt, hasOpt), toOptional(opt2, hasOpt2))
}

func (s *typedCodeGenServer) mapExampleInput(value gen.ExampleInput) gen.ExampleInput {
	opt, hasOpt := value.Optional()
	return gen.NewExampleInput(value.Required(), toOptional(opt, hasOpt))
}

func (s *typedCodeGenServer) mapUnion(value gen.ExUnion) (gen.ExUnion, error) {
	tagged := value.TaggedValue()
	switch tagged.Tag {
	case "One":
		return gen.NewExUnionFromOne(gen.NewExUnionOne()), nil
	case "Two":
		two, ok := tagged.Value.(gen.ExUnionTwo)
		if !ok {
			return gen.ExUnion{}, fmt.Errorf("telepact: unexpected union payload type %T", tagged.Value)
		}
		opt, hasOpt := two.Optional()
		return gen.NewExUnionFromTwo(gen.NewExUnionTwo(two.Required(), toOptional(opt, hasOpt))), nil
	default:
		return gen.ExUnion{}, fmt.Errorf("telepact: unknown union tag %q", tagged.Tag)
	}
}

func (s *typedCodeGenServer) mapUnionSlice(values []gen.ExUnion) ([]any, error) {
	if values == nil {
		return nil, nil
	}
	result := make([]any, len(values))
	for i, value := range values {
		mapped, err := s.mapUnion(value)
		if err != nil {
			return nil, err
		}
		result[i] = mapped.PseudoJSON()
	}
	return result, nil
}

func (s *typedCodeGenServer) mapUnionPointerSlice(values []*gen.ExUnion) ([]any, error) {
	if values == nil {
		return nil, nil
	}
	result := make([]any, len(values))
	for i, value := range values {
		if value == nil {
			result[i] = nil
			continue
		}
		mapped, err := s.mapUnion(*value)
		if err != nil {
			return nil, err
		}
		result[i] = mapped.PseudoJSON()
	}
	return result, nil
}

func (s *typedCodeGenServer) mapUnionMap(values map[string]gen.ExUnion) (map[string]any, error) {
	if values == nil {
		return nil, nil
	}
	result := make(map[string]any, len(values))
	for key, value := range values {
		mapped, err := s.mapUnion(value)
		if err != nil {
			return nil, err
		}
		result[key] = mapped.PseudoJSON()
	}
	return result, nil
}

func (s *typedCodeGenServer) mapUnionPointerMap(values map[string]*gen.ExUnion) (map[string]any, error) {
	if values == nil {
		return nil, nil
	}
	result := make(map[string]any, len(values))
	for key, value := range values {
		if value == nil {
			result[key] = nil
			continue
		}
		mapped, err := s.mapUnion(*value)
		if err != nil {
			return nil, err
		}
		result[key] = mapped.PseudoJSON()
	}
	return result, nil
}

func newValueWith(key string, value any) gen.Value {
	payload := map[string]any{key: value}
	return gen.NewValueFromPseudoJSON(payload)
}

func toOptional[T any](value T, present bool) gen.Optional[T] {
	if present {
		return gen.Some(value)
	}
	return gen.None[T]()
}

func pointerValue[T any](ptr *T, mapper func(T) any) any {
	if ptr == nil {
		return nil
	}
	return mapper(*ptr)
}

func slicePointerValue[T any](values []*T, mapper func(T) any) []any {
	if values == nil {
		return nil
	}
	result := make([]any, len(values))
	for i, value := range values {
		if value == nil {
			result[i] = nil
			continue
		}
		result[i] = mapper(*value)
	}
	return result
}

func mapValueWith[T any](values map[string]T, mapper func(T) any) map[string]any {
	if values == nil {
		return nil
	}
	result := make(map[string]any, len(values))
	for key, value := range values {
		result[key] = mapper(value)
	}
	return result
}

func mapPointerValue[T any](values map[string]*T, mapper func(T) any) map[string]any {
	if values == nil {
		return nil
	}
	result := make(map[string]any, len(values))
	for key, value := range values {
		if value == nil {
			result[key] = nil
			continue
		}
		result[key] = mapper(*value)
	}
	return result
}

func cloneSlice[T any](values []T) []T {
	if values == nil {
		return nil
	}
	result := make([]T, len(values))
	copy(result, values)
	return result
}

func cloneAnySlice(values []any) []any {
	if values == nil {
		return nil
	}
	result := make([]any, len(values))
	for i, value := range values {
		result[i] = cloneAny(value)
	}
	return result
}

func cloneStringAnyMap(values map[string]any) map[string]any {
	if values == nil {
		return nil
	}
	result := make(map[string]any, len(values))
	for key, value := range values {
		result[key] = cloneAny(value)
	}
	return result
}

func cloneAny(value any) any {
	switch typed := value.(type) {
	case []any:
		return cloneAnySlice(typed)
	case map[string]any:
		return cloneStringAnyMap(typed)
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for key, entry := range typed {
			converted[fmt.Sprint(key)] = cloneAny(entry)
		}
		return converted
	case []byte:
		return cloneBytes(typed)
	default:
		return typed
	}
}

func cloneBytes(value []byte) []byte {
	if value == nil {
		return nil
	}
	result := make([]byte, len(value))
	copy(result, value)
	return result
}

func cloneBytesSlice(values [][]byte) []any {
	if values == nil {
		return nil
	}
	result := make([]any, len(values))
	for i, value := range values {
		if value == nil {
			result[i] = nil
			continue
		}
		result[i] = cloneBytes(value)
	}
	return result
}

func cloneBytesMap(values map[string][]byte) map[string]any {
	if values == nil {
		return nil
	}
	result := make(map[string]any, len(values))
	for key, value := range values {
		if value == nil {
			result[key] = nil
			continue
		}
		result[key] = cloneBytes(value)
	}
	return result
}

func validatePseudoJSONSchema(input map[string]any) ([]map[string]any, error) {
	schemaRaw, ok := input["schema"]
	if !ok {
		return nil, errors.New("missing schema")
	}

	schemaJSON, err := toJSONString(schemaRaw)
	if err != nil {
		return nil, err
	}

	var extendJSON string
	if extendRaw, ok := input["extend!"]; ok {
		extendJSON, err = toJSONString(extendRaw)
		if err != nil {
			return nil, err
		}

		_, err = telepact.TelepactSchemaFromFileJSONMap(map[string]string{
			"default": schemaJSON,
			"extend":  extendJSON,
		})
	} else {
		_, err = telepact.TelepactSchemaFromJSON(schemaJSON)
	}
	if err == nil {
		return nil, nil
	}

	parseErr, ok := err.(*telepact.TelepactSchemaParseError)
	if !ok {
		return nil, err
	}

	var entries []map[string]any
	switch typed := parseErr.SchemaParseFailuresPseudoJSON.(type) {
	case []map[string]any:
		entries = typed
	case []any:
		entries = make([]map[string]any, 0, len(typed))
		for _, entry := range typed {
			if converted, err := asMap(entry); err == nil {
				entries = append(entries, converted)
			}
		}
	default:
		return nil, fmt.Errorf("unexpected parse failure pseudo json type %T", parseErr.SchemaParseFailuresPseudoJSON)
	}

	result := make([]map[string]any, 0, len(entries))
	for _, converted := range entries {
		failure := make(map[string]any, len(converted))
		if doc, ok := converted["document"].(string); ok {
			failure["document"] = doc
		}
		if loc, ok := converted["location"]; ok {
			failure["location"] = loc
		}
		if path, ok := converted["path"]; ok {
			failure["path"] = path
		}
		if reason, ok := converted["reason"].(map[string]any); ok {
			failure["reason"] = reason
		}
		result = append(result, failure)
	}

	return result, nil
}

func toJSONString(value any) (string, error) {
	switch typed := value.(type) {
	case string:
		return typed, nil
	case json.RawMessage:
		return string(typed), nil
	default:
		bytes, err := json.Marshal(typed)
		if err != nil {
			return "", err
		}
		return string(bytes), nil
	}
}
