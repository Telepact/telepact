package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"sync"

	"github.com/nats-io/nats.go"
)

type Dispatcher struct {
	conn          *nats.Conn
	logger        *log.Logger
	metrics       *metricRegistry
	dispatcherSub *nats.Subscription
	servers       map[string]*nats.Subscription
	serversMu     sync.Mutex
	done          chan struct{}
	doneOnce      sync.Once
}

func NewDispatcher(conn *nats.Conn, logger *log.Logger, metricsFile string) *Dispatcher {
	return &Dispatcher{
		conn:    conn,
		logger:  logger,
		metrics: newMetricRegistry(metricsFile),
		servers: make(map[string]*nats.Subscription),
		done:    make(chan struct{}),
	}
}

func (d *Dispatcher) Start(subject string) error {
	sub, err := d.conn.Subscribe(subject, d.handleMessage)
	if err != nil {
		return err
	}
	d.dispatcherSub = sub
	d.logger.Printf("dispatcher listening on subject %s", subject)
	return nil
}

func (d *Dispatcher) Done() <-chan struct{} {
	return d.done
}

func (d *Dispatcher) Close() error {
	d.stopAllServers()
	if d.dispatcherSub != nil {
		if err := d.dispatcherSub.Drain(); err != nil {
			d.logger.Printf("failed to drain dispatcher subscription: %v", err)
		}
	}
	return nil
}

func (d *Dispatcher) WriteMetrics() error {
	if d.metrics == nil {
		return nil
	}
	return d.metrics.WriteToFile()
}

func (d *Dispatcher) handleMessage(msg *nats.Msg) {
	response := buildErrorResponse()

	if err := d.processCommand(msg.Data); err != nil {
		d.logger.Printf("dispatcher command failed: %v", err)
	} else {
		response = buildOKResponse()
	}

	if err := respond(msg, response); err != nil {
		d.logger.Printf("failed to send dispatcher response: %v", err)
	}
}

func (d *Dispatcher) processCommand(data []byte) error {
	envelope, err := parseEnvelope(data)
	if err != nil {
		return err
	}

	target, payload, err := firstBodyEntry(envelope.Body)
	if err != nil {
		return err
	}

	switch target {
	case "Ping":
		return nil
	case "End":
		d.finish()
		return nil
	case "Stop":
		cfg, err := asMap(payload)
		if err != nil {
			return err
		}
		id := stringValue(cfg["id"])
		if id == "" {
			return errors.New("missing id in Stop payload")
		}
		return d.stopServer(id)
	case "StartServer":
		cfg, err := asMap(payload)
		if err != nil {
			return err
		}
		sub, err := startTestServer(d, cfg)
		if err != nil {
			return err
		}
		return d.trackServer(cfg, sub)
	case "StartClientServer":
		cfg, err := asMap(payload)
		if err != nil {
			return err
		}
		sub, err := startClientTestServer(d, cfg)
		if err != nil {
			return err
		}
		return d.trackServer(cfg, sub)
	case "StartMockServer":
		cfg, err := asMap(payload)
		if err != nil {
			return err
		}
		sub, err := startMockTestServer(d, cfg)
		if err != nil {
			return err
		}
		return d.trackServer(cfg, sub)
	case "StartSchemaServer":
		cfg, err := asMap(payload)
		if err != nil {
			return err
		}
		sub, err := startSchemaTestServer(d, cfg)
		if err != nil {
			return err
		}
		return d.trackServer(cfg, sub)
	default:
		return fmt.Errorf("unknown dispatcher target %s", target)
	}
}

func (d *Dispatcher) trackServer(cfg map[string]any, sub *nats.Subscription) error {
	id := stringValue(cfg["id"])
	if id == "" {
		return errors.New("missing id in payload")
	}

	d.serversMu.Lock()
	defer d.serversMu.Unlock()

	if old, exists := d.servers[id]; exists {
		_ = old.Drain()
	}
	d.servers[id] = sub
	return nil
}

func (d *Dispatcher) stopServer(id string) error {
	d.serversMu.Lock()
	sub, exists := d.servers[id]
	if exists {
		delete(d.servers, id)
	}
	d.serversMu.Unlock()

	if !exists {
		return fmt.Errorf("server %s not found", id)
	}

	return sub.Drain()
}

func (d *Dispatcher) stopAllServers() {
	d.serversMu.Lock()
	subs := make([]*nats.Subscription, 0, len(d.servers))
	for _, sub := range d.servers {
		subs = append(subs, sub)
	}
	d.servers = make(map[string]*nats.Subscription)
	d.serversMu.Unlock()

	for _, sub := range subs {
		_ = sub.Drain()
	}
}

func (d *Dispatcher) finish() {
	d.doneOnce.Do(func() {
		close(d.done)
	})
}

func buildOKResponse() envelope {
	return envelope{
		Headers: map[string]any{},
		Body:    map[string]any{"Ok_": map[string]any{}},
	}
}

func buildErrorResponse() envelope {
	return envelope{
		Headers: map[string]any{},
		Body:    map[string]any{"ErrorUnknown": map[string]any{}},
	}
}

type envelope struct {
	Headers map[string]any
	Body    map[string]any
}

func parseEnvelope(data []byte) (envelope, error) {
	var raw []any
	if err := json.Unmarshal(data, &raw); err != nil {
		return envelope{}, err
	}
	if len(raw) != 2 {
		return envelope{}, errors.New("invalid envelope length")
	}

	headers, err := asMap(raw[0])
	if err != nil {
		return envelope{}, err
	}

	body, err := asMap(raw[1])
	if err != nil {
		return envelope{}, err
	}

	return envelope{Headers: headers, Body: body}, nil
}

func respond(msg *nats.Msg, env envelope) error {
	payload := []any{env.Headers, env.Body}
	data, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	return msg.Respond(data)
}

func firstBodyEntry(body map[string]any) (string, any, error) {
	for key, value := range body {
		return key, value, nil
	}
	return "", nil, errors.New("empty body")
}

func asMap(value any) (map[string]any, error) {
	switch typed := value.(type) {
	case map[string]any:
		return typed, nil
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for k, v := range typed {
			converted[fmt.Sprint(k)] = v
		}
		return converted, nil
	default:
		return nil, errors.New("value is not a map")
	}
}

func stringValue(value any) string {
	switch typed := value.(type) {
	case string:
		return typed
	case fmt.Stringer:
		return typed.String()
	case json.Number:
		return typed.String()
	default:
		return ""
	}
}
