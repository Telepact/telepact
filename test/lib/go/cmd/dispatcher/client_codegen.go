package main

import (
	telepact "github.com/telepact/telepact/lib/go/telepact"
)

type generatedTypedClient struct {
	client *telepact.Client
	schema *telepact.TelepactSchema
}

func newGeneratedTypedClient(client *telepact.Client, schema *telepact.TelepactSchema) *generatedTypedClient {
	return &generatedTypedClient{client: client, schema: schema}
}

func (g *generatedTypedClient) Handle(message telepact.Message) (telepact.Message, error) {
	if g == nil || g.client == nil {
		return telepact.Message{}, telepact.NewTelepactError("generated client not configured")
	}

	response, err := g.client.Request(message)
	if err != nil {
		return telepact.Message{}, err
	}

	if response.Headers == nil {
		response.Headers = map[string]any{}
	}
	response.Headers["@codegenc_"] = true

	return response, nil
}
