package main

import (
	"fmt"
	"os"

	telepact "github.com/telepact/telepact/lib/go/telepact"
	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

func main() {
	schema, err := telepact.TelepactSchemaFromDirectory("../../test/runner/schema/example")
	if err != nil {
		fmt.Println("schema err:", err)
		os.Exit(1)
	}
	field := schema.RequestHeaderDeclarations()["@select_"]
	if field == nil {
		fmt.Println("@select_ field nil")
		return
	}
	sel, ok := field.TypeDeclaration.Type.(*types.TSelect)
	if !ok || sel == nil {
		fmt.Println("type not TSelect")
		return
	}
	fmt.Println("select keys:")
	for k := range sel.PossibleSelects {
		fmt.Println(" ", k)
	}

	fmt.Println("fn.test selects:")
	if fnSel, ok := sel.PossibleSelects["fn.test"].(map[string]any); ok {
		for k, v := range fnSel {
			fmt.Printf("  %s: %T\n", k, v)
		}
		if unionSel, ok := fnSel["union.ExUnion"].(map[string]any); ok {
			for k, v := range unionSel {
				fmt.Printf("    union %s: %v\n", k, v)
			}
		}
	}
}
