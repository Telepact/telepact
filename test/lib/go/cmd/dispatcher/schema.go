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
		valueOpt = gen.Some(copyValue(top))
	}

	okBody := gen.NewTestOutputOk(valueOpt)
	body := gen.NewTestOutputFromOk(okBody)

	return telepact.NewTypedMessage(map[string]any{}, body), nil
}

func copyValue(value gen.Value) gen.Value {
	return gen.NewValueFromPseudoJSON(value.PseudoJSON())
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
