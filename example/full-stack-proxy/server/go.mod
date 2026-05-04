module github.com/telepact/telepact/example/full-stack-proxy/server

go 1.22.0

require (
	github.com/nats-io/nats.go v1.39.1
	github.com/telepact/telepact/lib/go v0.0.0
)

require (
	github.com/klauspost/compress v1.17.9 // indirect
	github.com/nats-io/nkeys v0.4.9 // indirect
	github.com/nats-io/nuid v1.0.1 // indirect
	github.com/vmihailenco/msgpack/v5 v5.4.1 // indirect
	github.com/vmihailenco/tagparser/v2 v2.0.0 // indirect
	golang.org/x/crypto v0.31.0 // indirect
	golang.org/x/sys v0.28.0 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)

replace github.com/telepact/telepact/lib/go => ../../../lib/go
