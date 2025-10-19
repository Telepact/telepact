package main

import (
    "bytes"
    "fmt"
    "github.com/vmihailenco/msgpack/v5"
)

func main() {
    var buf bytes.Buffer
    enc := msgpack.NewEncoder(&buf)
    if err := enc.EncodeExtHeader(17, 0); err != nil {
        panic(err)
    }
    // No payload

    var decoded interface{}
    if err := msgpack.Unmarshal(buf.Bytes(), &decoded); err != nil {
        panic(err)
    }
    fmt.Printf("decoded type: %T, value: %[2]v\n", decoded, decoded)
}
