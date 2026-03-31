module github.com/telepact/telepact/example/go-websocket

go 1.22

require (
	github.com/gorilla/websocket v1.5.3
	github.com/telepact/telepact/lib/go v0.0.0
)

require (
	github.com/vmihailenco/msgpack/v5 v5.4.1 // indirect
	github.com/vmihailenco/tagparser/v2 v2.0.0 // indirect
	gopkg.in/yaml.v3 v3.0.0-20200313102051-9f266ea9e77c // indirect
)

replace github.com/telepact/telepact/lib/go => ../../lib/go
