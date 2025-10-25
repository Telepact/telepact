package main

import (
	telepact "github.com/telepact/telepact/lib/go/telepact"
	gen "github.com/telepact/telepact/test/lib/go/cmd/dispatcher/gen"
)

type generatedTypedClient struct {
	client *telepact.Client
	typed  *gen.TypedClient
}

func newGeneratedTypedClient(client *telepact.Client) *generatedTypedClient {
	var typed *gen.TypedClient
	if client != nil {
		typed = gen.NewTypedClient(client)
	}
	return &generatedTypedClient{client: client, typed: typed}
}

func (g *generatedTypedClient) Handle(message telepact.Message) (telepact.Message, error) {
	if g == nil || g.client == nil {
		return telepact.Message{}, telepact.NewTelepactError("generated client not configured")
	}

	target, err := message.BodyTarget()
	if err != nil {
		return telepact.Message{}, err
	}

	payload, err := message.BodyPayload()
	if err != nil {
		return telepact.Message{}, err
	}

	if g.typed == nil {
		g.typed = gen.NewTypedClient(g.client)
	}

	headers, body, handled, err := g.typed.Invoke(target, message.Headers, payload)
	if err != nil {
		return telepact.Message{}, err
	}

	if handled {
		if headers == nil {
			headers = map[string]any{}
		}
		if body == nil {
			body = map[string]any{}
		}
		headers["@codegenc_"] = true
		return telepact.NewMessage(headers, body), nil
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
