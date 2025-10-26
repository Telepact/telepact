package telepact

import (
	"path/filepath"
	"runtime"
	"testing"
)

func TestServerReturnsInvalidResponseBodyForArrFn(t *testing.T) {
	_, filename, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatalf("failed to locate test file path")
	}

	repoRoot := filepath.Clean(filepath.Join(filepath.Dir(filename), "..", "..", "..", ".."))
	schemaDir := filepath.Join(repoRoot, "test", "runner", "schema", "example")

	schema, err := TelepactSchemaFromDirectory(schemaDir)
	if err != nil {
		t.Fatalf("failed loading schema: %v", err)
	}

	handler := func(msg Message) (Message, error) {
		return NewMessage(map[string]any{}, map[string]any{
			"Ok_": map[string]any{
				"value!": map[string]any{
					"arrFn!": []any{
						map[string]any{"fn.example": map[string]any{"required": true}},
						map[string]any{"fn.example": map[string]any{}},
					},
				},
			},
		}), nil
	}

	options := NewServerOptions()
	options.AuthRequired = false
	server, err := NewServer(schema, handler, options)
	if err != nil {
		t.Fatalf("failed creating server: %v", err)
	}

	requestMessage := NewMessage(map[string]any{}, map[string]any{"fn.test": map[string]any{}})
	requestBytes, err := server.Serializer().Serialize(requestMessage)
	if err != nil {
		t.Fatalf("failed serializing request: %v", err)
	}

	response, err := server.Process(requestBytes)
	if err != nil {
		t.Fatalf("server process failed: %v", err)
	}

	decoded, err := server.Serializer().Deserialize(response.Bytes)
	if err != nil {
		t.Fatalf("failed deserializing response: %v", err)
	}

	if _, ok := decoded.Body["ErrorInvalidResponseBody_"]; !ok {
		t.Fatalf("expected ErrorInvalidResponseBody_, got %v", decoded.Body)
	}
}
