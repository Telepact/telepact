package main

import (
	"encoding/json"
	"errors"
	"fmt"

	telepact "github.com/telepact/telepact/lib/go/telepact"
)

type codeGenHandler struct{}

func newCodeGenHandler(enabled bool) *codeGenHandler {
	if !enabled {
		return nil
	}
	return &codeGenHandler{}
}

func (c *codeGenHandler) Handle(message telepact.Message) (telepact.Message, error) {
	if c == nil {
		return message, nil
	}

	headers := message.Headers
	body := message.Body

	if headers == nil {
		headers = map[string]any{}
	}
	if body == nil {
		body = map[string]any{}
	}

	headers["@codegens_"] = true
	return telepact.NewMessage(headers, body), nil
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
