package main

import (
	"encoding/json"
	"errors"
	"fmt"

	telepact "github.com/telepact/telepact/lib/go/telepact"
)

type codeGenHandler struct{}

type validationFailure struct {
	Document string         `json:"document"`
	Location any            `json:"location"`
	Path     any            `json:"path"`
	Reason   map[string]any `json:"reason"`
}

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

func validatePseudoJSONSchema(input map[string]any) ([]validationFailure, error) {
	schemaRaw, ok := input["schema"]
	if !ok {
		return nil, errors.New("missing schema")
	}

	schemaBytes, err := json.Marshal(schemaRaw)
	if err != nil {
		return nil, err
	}

	if extendRaw, ok := input["extend!"]; ok {
		extendBytes, err := json.Marshal(extendRaw)
		if err != nil {
			return nil, err
		}

		_, err = telepact.TelepactSchemaFromFileJSONMap(map[string]string{
			"default": string(schemaBytes),
			"extend":  string(extendBytes),
		})
	} else {
		_, err = telepact.TelepactSchemaFromJSON(string(schemaBytes))
	}
	if err == nil {
		return nil, nil
	}

	parseErr, ok := err.(*telepact.TelepactSchemaParseError)
	if !ok {
		return nil, err
	}

	failures, ok := parseErr.SchemaParseFailuresPseudoJSON.([]any)
	if !ok {
		return nil, fmt.Errorf("unexpected parse failure pseudo json type %T", parseErr.SchemaParseFailuresPseudoJSON)
	}

	result := make([]validationFailure, 0, len(failures))
	for _, entry := range failures {
		if converted, err := asMap(entry); err == nil {
			failure := validationFailure{}
			if doc, ok := converted["document"].(string); ok {
				failure.Document = doc
			}
			if loc, ok := converted["location"]; ok {
				failure.Location = loc
			}
			if path, ok := converted["path"]; ok {
				failure.Path = path
			}
			if reason, ok := converted["reason"].(map[string]any); ok {
				failure.Reason = reason
			}
			result = append(result, failure)
		}
	}

	return result, nil
}
