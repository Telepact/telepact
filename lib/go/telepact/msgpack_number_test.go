package telepact

import (
	"encoding/json"
	"testing"

	"github.com/vmihailenco/msgpack/v5"
)

func TestMsgpackJSONNumberEncoding(t *testing.T) {
	num := json.Number("9223372036854775808")

	bytes, err := msgpack.Marshal(wrapJSONNumbers(num))
	if err != nil {
		t.Fatalf("marshal failed: %v", err)
	}

	var decoded any
	if err := msgpack.Unmarshal(bytes, &decoded); err != nil {
		t.Fatalf("unmarshal failed: %v", err)
	}

	decoded = unwrapJSONNumbers(decoded)

	numDecoded, ok := decoded.(json.Number)
	if !ok {
		t.Fatalf("expected json.Number, got %T", decoded)
	}
	if numDecoded.String() != num.String() {
		t.Fatalf("expected %s, got %s", num.String(), numDecoded.String())
	}
}
