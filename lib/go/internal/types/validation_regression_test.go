package types_test

import (
	"path/filepath"
	"testing"

	telepact "github.com/telepact/telepact/lib/go"
	typ "github.com/telepact/telepact/lib/go/internal/types"
)

func TestResultValidationDetectsMissingFnRequired(t *testing.T) {
	schemaDir := filepath.Join("..", "..", "..", "..", "test", "runner", "schema", "example")

	telepactSchema, err := telepact.TelepactSchemaFromDirectory(schemaDir)
	if err != nil {
		t.Fatalf("failed loading schema: %v", err)
	}

	parsed := telepactSchema.ParsedDefinitions()
	definition, ok := parsed["fn.test.->"]
	if !ok {
		t.Fatalf("missing fn.test.-> definition in schema")
	}

	resultUnion, ok := definition.(*typ.TUnion)
	if !ok {
		t.Fatalf("fn.test.-> definition is %T, want *TUnion", definition)
	}

	invalidResponse := map[string]any{
		"Ok_": map[string]any{
			"value!": map[string]any{
				"arrFn!": []any{
					map[string]any{"fn.example": map[string]any{"required": true}},
					map[string]any{"fn.example": map[string]any{}},
				},
			},
		},
	}

	ctx := typ.NewValidateContext(nil, "fn.test", true)
	failures := resultUnion.Validate(invalidResponse, nil, ctx)
	if len(failures) == 0 {
		t.Fatalf("expected validation failures, got none")
	}

	failure := failures[0]
	if failure.Reason != "RequiredObjectKeyMissing" {
		t.Fatalf("unexpected failure reason %q", failure.Reason)
	}
}
