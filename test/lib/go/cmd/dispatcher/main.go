package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	telepact "github.com/telepact/telepact/lib/go"
	nats "github.com/telepact/telepact/test/lib/go/internal/stdionats"
	"github.com/vmihailenco/msgpack/v5"
)

const backwardsCompatibleChangeSchema = `
[
    {
        "struct.BackwardsCompatibleChange": {}
    }
]
`

func main() {
	logger := log.New(os.Stderr, "[telepact-go] ", log.LstdFlags|log.Lmicroseconds)

	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		logger.Fatal("NATS_URL env var not set")
	}

	subject := os.Getenv("TP_HARNESS_SUBJECT")
	if subject == "" {
		subject = "go"
	}

	metricsFile := "metrics.txt"

	nc, err := nats.Connect(natsURL, nats.Name("telepact-go-test-harness"))
	if err != nil {
		logger.Fatalf("failed to connect to NATS: %v", err)
	}
	defer func() {
		_ = nc.Drain()
	}()

	dispatcher := NewDispatcher(nc, logger, metricsFile)
	if err := dispatcher.Start(subject); err != nil {
		logger.Fatalf("failed to start dispatcher: %v", err)
	}

	<-dispatcher.Done()

	if err := dispatcher.Close(); err != nil {
		logger.Printf("error while shutting down dispatcher: %v", err)
	}

	if err := dispatcher.WriteMetrics(); err != nil {
		logger.Printf("failed to write metrics: %v", err)
	}
}

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

type metricRegistry struct {
	file   string
	mu     sync.Mutex
	reg    *prometheus.Registry
	timers map[string]prometheus.Summary
}

func newMetricRegistry(file string) *metricRegistry {
	return &metricRegistry{
		file:   file,
		reg:    prometheus.NewRegistry(),
		timers: make(map[string]prometheus.Summary),
	}
}

func (m *metricRegistry) Observe(topic string, duration time.Duration) {
	if m == nil {
		return
	}

	summary := m.summaryForTopic(topic)
	if summary == nil {
		return
	}

	summary.Observe(duration.Seconds())
}

func (m *metricRegistry) summaryForTopic(topic string) prometheus.Summary {
	m.mu.Lock()
	defer m.mu.Unlock()

	if summary, ok := m.timers[topic]; ok {
		return summary
	}

	name := sanitizeMetricName(topic)
	metric := prometheus.NewSummary(prometheus.SummaryOpts{
		Name: name,
		Help: fmt.Sprintf("Latency summary for topic %s", topic),
	})

	if err := m.reg.Register(metric); err != nil {
		return nil
	}

	m.timers[topic] = metric
	return metric
}

func (m *metricRegistry) WriteToFile() error {
	if m == nil || m.file == "" {
		return nil
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	return prometheus.WriteToTextfile(m.file, m.reg)
}

func sanitizeMetricName(topic string) string {
	replacer := strings.NewReplacer(
		".", "_",
		"-", "_",
		":", "_",
		"/", "_",
		" ", "_",
	)

	sanitized := replacer.Replace(topic)
	sanitized = strings.Map(func(r rune) rune {
		if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '_' {
			return r
		}
		return '_'
	}, sanitized)

	if sanitized == "" {
		sanitized = "telepact_metric"
	}
	if sanitized[0] >= '0' && sanitized[0] <= '9' {
		sanitized = "telepact_" + sanitized
	}

	return sanitized
}

type serverConfig struct {
	ID              string
	APISchemaPath   string
	FrontdoorTopic  string
	BackdoorTopic   string
	ClientFrontdoor string
	ClientBackdoor  string
	AuthRequired    bool
	UseCodegen      bool
	UseBinary       bool
	UseTestClient   bool
	Config          map[string]any
}

func parseServerConfig(cfg map[string]any) (serverConfig, error) {
	if cfg == nil {
		return serverConfig{}, errors.New("nil server configuration")
	}

	result := serverConfig{Config: make(map[string]any)}
	result.ID = stringValue(cfg["id"])
	if result.ID == "" {
		return serverConfig{}, errors.New("missing id")
	}

	if raw, ok := cfg["apiSchemaPath"]; ok {
		result.APISchemaPath = stringValue(raw)
	}
	if raw, ok := cfg["frontdoorTopic"]; ok {
		result.FrontdoorTopic = stringValue(raw)
	}
	if raw, ok := cfg["backdoorTopic"]; ok {
		result.BackdoorTopic = stringValue(raw)
	}
	if raw, ok := cfg["clientFrontdoorTopic"]; ok {
		result.ClientFrontdoor = stringValue(raw)
	}
	if raw, ok := cfg["clientBackdoorTopic"]; ok {
		result.ClientBackdoor = stringValue(raw)
	}

	if raw, ok := cfg["authRequired!"]; ok {
		result.AuthRequired = boolValue(raw)
	} else if raw, ok := cfg["authRequired"]; ok {
		result.AuthRequired = boolValue(raw)
	}

	if raw, ok := cfg["useCodeGen"]; ok {
		result.UseCodegen = boolValue(raw)
	}
	if raw, ok := cfg["useBinary"]; ok {
		result.UseBinary = boolValue(raw)
	}
	if raw, ok := cfg["useTestClient"]; ok {
		result.UseTestClient = boolValue(raw)
	}

	if raw, ok := cfg["config!"]; ok {
		if converted, err := asMap(raw); err == nil {
			result.Config = converted
		}
	}

	return result, nil
}

func startClientTestServer(d *Dispatcher, rawCfg map[string]any) (*nats.Subscription, error) {
	cfg, err := parseServerConfig(rawCfg)
	if err != nil {
		return nil, err
	}
	if cfg.ClientFrontdoor == "" {
		return nil, errors.New("missing client frontdoor topic")
	}
	if cfg.ClientBackdoor == "" {
		return nil, errors.New("missing client backdoor topic")
	}

	adapter := func(ctx context.Context, request telepact.Message, serializer *telepact.Serializer) (telepact.Message, error) {
		bytes, err := serializer.Serialize(request)
		if err != nil {
			var serializationErr *telepact.SerializationError
			if errors.As(err, &serializationErr) && isNumberTooBigError(serializationErr.Unwrap()) {
				headers := map[string]any{"numberTooBig": true}
				return telepact.NewMessage(headers, map[string]any{"ErrorUnknown_": map[string]any{}}), nil
			}
			return telepact.Message{}, err
		}

		if ctx == nil {
			ctx = context.Background()
		}
		ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
		defer cancel()

		reply, err := d.conn.RequestWithContext(ctx, cfg.ClientBackdoor, bytes)
		if err != nil {
			return telepact.Message{}, err
		}

		return serializer.Deserialize(reply.Data)
	}

	clientOptions := telepact.NewClientOptions()
	clientOptions.UseBinary = cfg.UseBinary
	clientOptions.AlwaysSendJSON = !cfg.UseBinary
	client, err := telepact.NewClient(adapter, clientOptions)
	if err != nil {
		return nil, err
	}

	var testClient *telepact.TestClient
	if cfg.UseTestClient {
		testClient = telepact.NewTestClient(client, telepact.TestClientOptions{})
	}

	var generatedClient *generatedTypedClient
	if cfg.UseCodegen {
		generatedClient = newGeneratedTypedClient(client)
	}

	sub, err := d.conn.Subscribe(cfg.ClientFrontdoor, func(msg *nats.Msg) {
		d.handleClientRequest(msg, client, generatedClient, testClient, cfg)
	})
	if err != nil {
		return nil, err
	}

	d.logger.Printf("client-server %s listening on %s", cfg.ID, cfg.ClientFrontdoor)
	return sub, nil
}

func startMockTestServer(d *Dispatcher, rawCfg map[string]any) (*nats.Subscription, error) {
	cfg, err := parseServerConfig(rawCfg)
	if err != nil {
		return nil, err
	}
	if cfg.APISchemaPath == "" {
		return nil, errors.New("missing apiSchemaPath")
	}
	if cfg.FrontdoorTopic == "" {
		return nil, errors.New("missing frontdoor topic")
	}

	schema, err := telepact.MockTelepactSchemaFromDirectory(cfg.APISchemaPath)
	if err != nil {
		return nil, err
	}

	options := telepact.NewMockServerOptions()
	options.OnError = func(err error) {
		if err != nil {
			d.logger.Printf("mock server error: %v", err)
		}
	}
	options.EnableMessageResponseGeneration = false
	if min, ok := intFromAny(cfg.Config["minLength"]); ok {
		options.GeneratedCollectionLengthMin = min
	}
	if max, ok := intFromAny(cfg.Config["maxLength"]); ok {
		options.GeneratedCollectionLengthMax = max
	}
	if boolValue(cfg.Config["enableGen"]) {
		options.EnableMessageResponseGeneration = true
	}

	mockServer, err := telepact.NewMockServer(schema, options)
	if err != nil {
		return nil, err
	}

	sub, err := d.conn.Subscribe(cfg.FrontdoorTopic, func(msg *nats.Msg) {
		start := time.Now()
		resp, err := mockServer.Process(msg.Data)
		if err != nil {
			d.logger.Printf("mock server process error: %v", err)
			_ = msg.Respond(buildUnknownPayload())
			return
		}

		if d.metrics != nil {
			d.metrics.Observe(cfg.FrontdoorTopic, time.Since(start))
		}

		if err := respondWithBytes(msg, resp.Bytes); err != nil {
			d.logger.Printf("mock server respond error: %v", err)
		}
	})
	if err != nil {
		return nil, err
	}

	d.logger.Printf("mock server %s listening on %s", cfg.ID, cfg.FrontdoorTopic)
	return sub, nil
}

func startSchemaTestServer(d *Dispatcher, rawCfg map[string]any) (*nats.Subscription, error) {
	cfg, err := parseServerConfig(rawCfg)
	if err != nil {
		return nil, err
	}
	if cfg.APISchemaPath == "" {
		return nil, errors.New("missing apiSchemaPath")
	}
	if cfg.FrontdoorTopic == "" {
		return nil, errors.New("missing frontdoor topic")
	}

	schema, err := telepact.TelepactSchemaFromDirectory(cfg.APISchemaPath)
	if err != nil {
		return nil, err
	}

	handler := func(message telepact.Message) (telepact.Message, error) {
		body := message.Body
		payload, ok := body["fn.validateSchema"].(map[string]any)
		if !ok {
			return telepact.NewMessage(map[string]any{}, map[string]any{"ErrorUnknown_": map[string]any{}}), nil
		}

		input, ok := payload["input"].(map[string]any)
		if !ok {
			return telepact.NewMessage(map[string]any{}, map[string]any{"ErrorUnknown_": map[string]any{}}), nil
		}

		key := firstKey(input)
		switch key {
		case "PseudoJson":
			pseudo, _ := input[key].(map[string]any)
			failures, err := validatePseudoJSONSchema(pseudo)
			if err != nil {
				return telepact.Message{}, err
			}
			if len(failures) > 0 {
				body := map[string]any{"ErrorValidationFailure": map[string]any{"cases": failures}}
				return telepact.NewMessage(map[string]any{}, body), nil
			}
		case "Json":
			if union, _ := input[key].(map[string]any); union != nil {
				if schemaJSON, ok := union["schema"].(string); ok {
					if _, err := telepact.TelepactSchemaFromJSON(schemaJSON); err != nil {
						return schemaValidationFailureMessage(err), nil
					}
				}
			}
		case "Directory":
			if union, _ := input[key].(map[string]any); union != nil {
				if dir, ok := union["schemaDirectory"].(string); ok {
					if _, err := telepact.TelepactSchemaFromDirectory(dir); err != nil {
						return schemaValidationFailureMessage(err), nil
					}
				}
			}
		default:
			return telepact.NewMessage(map[string]any{}, map[string]any{"ErrorUnknown_": map[string]any{}}), nil
		}

		return telepact.NewMessage(map[string]any{}, map[string]any{"Ok_": map[string]any{}}), nil
	}

	options := telepact.NewServerOptions()
	options.OnError = func(err error) {
		if err != nil {
			d.logger.Printf("schema server error: %v", err)
		}
	}
	options.AuthRequired = false

	server, err := telepact.NewServer(schema, handler, options)
	if err != nil {
		return nil, err
	}

	sub, err := d.conn.Subscribe(cfg.FrontdoorTopic, func(msg *nats.Msg) {
		d.handleServerRequest(server, cfg.FrontdoorTopic, msg)
	})
	if err != nil {
		return nil, err
	}

	d.logger.Printf("schema server %s listening on %s", cfg.ID, cfg.FrontdoorTopic)
	return sub, nil
}

func startTestServer(d *Dispatcher, rawCfg map[string]any) (*nats.Subscription, error) {
	cfg, err := parseServerConfig(rawCfg)
	if err != nil {
		return nil, err
	}
	if cfg.APISchemaPath == "" {
		return nil, errors.New("missing apiSchemaPath")
	}
	if cfg.FrontdoorTopic == "" {
		return nil, errors.New("missing frontdoor topic")
	}
	if !cfg.UseCodegen && cfg.BackdoorTopic == "" {
		return nil, errors.New("missing backdoor topic")
	}

	files, err := telepact.NewTelepactSchemaFiles(cfg.APISchemaPath)
	if err != nil {
		return nil, err
	}

	tele, err := telepact.TelepactSchemaFromFileJSONMap(files.FilenamesToJSON)
	if err != nil {
		return nil, err
	}

	alternateMap := cloneStringStringMap(files.FilenamesToJSON)
	alternateMap["backwardsCompatibleChange"] = backwardsCompatibleChangeSchema
	alternateTele, err := telepact.TelepactSchemaFromFileJSONMap(alternateMap)
	if err != nil {
		return nil, err
	}

	var serveAlternate atomic.Bool
	codegenHandler := newCodeGenHandler(cfg.UseCodegen)

	const requestTimeout = 5 * time.Second

	forwardRequest := func(message telepact.Message) (telepact.Message, error) {
		payload := []any{message.Headers, message.Body}
		payloadBytes, err := json.Marshal(payload)
		if err != nil {
			return telepact.Message{}, err
		}

		ctx, cancel := context.WithTimeout(context.Background(), requestTimeout)
		defer cancel()

		reply, err := d.conn.RequestWithContext(ctx, cfg.BackdoorTopic, payloadBytes)
		if err != nil {
			return telepact.Message{}, err
		}

		var response []any
		decoder := json.NewDecoder(bytes.NewReader(reply.Data))
		decoder.UseNumber()
		if err := decoder.Decode(&response); err != nil {
			return telepact.Message{}, err
		}
		normalized := normalizeJSONNumbers(response)
		responseSlice, ok := normalized.([]any)
		if !ok {
			return telepact.Message{}, fmt.Errorf("invalid backdoor response payload")
		}
		response = responseSlice
		if len(response) != 2 {
			return telepact.Message{}, errors.New("invalid backdoor response payload")
		}

		headers, err := asMap(response[0])
		if err != nil {
			return telepact.Message{}, err
		}
		body, err := asMap(response[1])
		if err != nil {
			return telepact.Message{}, err
		}

		return telepact.NewMessage(headers, body), nil
	}

	type handlerError struct{}

	handler := func(message telepact.Message) (telepact.Message, error) {
		reqHeaders := message.Headers

		if boolValue(reqHeaders["@toggleAlternateServer_"]) {
			serveAlternate.Store(!serveAlternate.Load())
		}

		if boolValue(reqHeaders["@throwError_"]) {
			return telepact.Message{}, fmt.Errorf("telepact: requested server error")
		}

		var msg telepact.Message
		var err error
		if codegenHandler != nil {
			msg, err = codegenHandler.Handle(message)
			if err != nil {
				return telepact.Message{}, err
			}
		} else {
			if cfg.BackdoorTopic == "" {
				return telepact.Message{}, fmt.Errorf("telepact: backdoor topic not configured")
			}

			msg, err = forwardRequest(message)
			if err != nil {
				return telepact.Message{}, err
			}
		}

		return msg, nil
	}

	options := telepact.NewServerOptions()
	options.AuthRequired = cfg.AuthRequired
	options.OnError = func(err error) {
		if err != nil {
			d.logger.Printf("server error: %v", err)
		}
	}
	options.OnRequest = func(msg telepact.Message) {
		if boolValue(msg.Headers["@onRequestError_"]) {
			panic(handlerError{})
		}
	}
	options.OnResponse = func(msg telepact.Message) {
		if boolValue(msg.Headers["@onResponseError_"]) {
			panic(handlerError{})
		}
	}

	server, err := telepact.NewServer(tele, handler, options)
	if err != nil {
		return nil, err
	}

	alternateOptions := telepact.NewServerOptions()
	alternateOptions.AuthRequired = cfg.AuthRequired
	alternateOptions.OnError = func(err error) {
		if err != nil {
			d.logger.Printf("alternate server error: %v", err)
		}
	}
	alternateServer, err := telepact.NewServer(alternateTele, handler, alternateOptions)
	if err != nil {
		return nil, err
	}

	sub, err := d.conn.Subscribe(cfg.FrontdoorTopic, func(msg *nats.Msg) {
		start := time.Now()
		var (
			resp telepact.Response
			err  error
		)

		if serveAlternate.Load() {
			resp, err = alternateServer.Process(msg.Data)
		} else {
			override := map[string]any{"@override": "new"}
			resp, err = server.ProcessWithHeaders(msg.Data, override)
		}

		if err != nil {
			d.logger.Printf("server.process error: %v", err)
			_ = msg.Respond(buildUnknownPayload())
			return
		}

		if d.metrics != nil {
			d.metrics.Observe(cfg.FrontdoorTopic, time.Since(start))
		}

		if err := respondWithBytes(msg, resp.Bytes); err != nil {
			d.logger.Printf("server respond error: %v", err)
		}
	})
	if err != nil {
		return nil, err
	}

	d.logger.Printf("server %s listening on %s", cfg.ID, cfg.FrontdoorTopic)
	return sub, nil
}

func (d *Dispatcher) handleServerRequest(server *telepact.Server, topic string, msg *nats.Msg) {
	start := time.Now()
	resp, err := server.Process(msg.Data)
	if err != nil {
		d.logger.Printf("server.process error: %v", err)
		_ = msg.Respond(buildUnknownPayload())
		return
	}

	if d.metrics != nil {
		d.metrics.Observe(topic, time.Since(start))
	}

	if err := respondWithBytes(msg, resp.Bytes); err != nil {
		d.logger.Printf("server respond error: %v", err)
	}
}

func (d *Dispatcher) handleClientRequest(
	msg *nats.Msg,
	client *telepact.Client,
	generatedClient *generatedTypedClient,
	testClient *telepact.TestClient,
	cfg serverConfig,
) {
	start := time.Now()

	request, err := deserializePseudoJSON(msg.Data)
	if err != nil {
		d.logger.Printf("client request decode error: %v", err)
		_ = msg.Respond(buildUnknownPayload())
		return
	}

	headers, err := asMap(request[0])
	if err != nil {
		d.logger.Printf("client headers decode error: %v", err)
		_ = msg.Respond(buildUnknownPayload())
		return
	}

	body, err := asMap(request[1])
	if err != nil {
		d.logger.Printf("client body decode error: %v", err)
		_ = msg.Respond(buildUnknownPayload())
		return
	}

	message := telepact.NewMessage(headers, body)

	var response telepact.Message

	switch {
	case testClient != nil:
		if seed, ok := intFromAny(headers["@setSeed"]); ok {
			testClient.SetSeed(int32(seed))
		}
		expectMatch := true
		if raw, ok := headers["@expectMatch"]; ok {
			expectMatch = boolValue(raw)
		}

		var expected map[string]any
		if raw := headers["@expectedPseudoJsonBody"]; raw != nil {
			if converted, err := asMap(raw); err == nil {
				expected = converted
			}
		}

		resp, err := testClient.AssertRequest(message, expected, expectMatch)
		if err != nil {
			d.logger.Printf("test client assertion failed: %v", err)
			headers := map[string]any{"@assertionError": true}
			response = telepact.NewMessage(headers, map[string]any{"ErrorUnknown_": map[string]any{}})
		} else {
			response = resp
		}
	case generatedClient != nil:
		resp, err := generatedClient.Handle(message)
		if err != nil {
			d.logger.Printf("generated client error: %v", err)
			_ = msg.Respond(buildUnknownPayload())
			return
		}
		response = resp
	default:
		resp, err := client.Request(message)
		if err != nil {
			d.logger.Printf("client request error: %v", err)
			_ = msg.Respond(buildUnknownPayload())
			return
		}
		response = resp
	}

	if containsBytes(response.Body) {
		if response.Headers == nil {
			response.Headers = map[string]any{}
		}
		response.Headers["@clientReturnedBinary"] = true
	}

	if generatedClient != nil {
		if response.Headers == nil {
			response.Headers = map[string]any{}
		}
		if _, exists := response.Headers["@codegens_"]; !exists {
			response.Headers["@codegens_"] = true
		}
	}

	payload := []any{response.Headers, response.Body}
	data, err := json.Marshal(payload)
	if err != nil {
		d.logger.Printf("client response marshal error: %v", err)
		_ = msg.Respond(buildUnknownPayload())
		return
	}

	if d.metrics != nil {
		d.metrics.Observe(cfg.ClientFrontdoor, time.Since(start))
	}

	if err := msg.Respond(data); err != nil {
		d.logger.Printf("client respond error: %v", err)
	}
}

func deserializePseudoJSON(data []byte) ([]any, error) {
	var envelope []any
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.UseNumber()
	if err := decoder.Decode(&envelope); err != nil {
		decoder := msgpack.NewDecoder(bytes.NewReader(data))
		if err := decoder.Decode(&envelope); err != nil {
			return nil, fmt.Errorf("decode pseudo-json: %w", err)
		}
	}
	normalized := normalizeJSONNumbers(envelope)
	normalizedSlice, ok := normalized.([]any)
	if !ok {
		return nil, errors.New("invalid pseudo-json envelope type")
	}
	envelope = normalizedSlice
	if len(envelope) != 2 {
		return nil, errors.New("invalid pseudo-json envelope length")
	}
	return envelope, nil
}

func buildUnknownPayload() []byte {
	payload := []any{map[string]any{}, map[string]any{"ErrorUnknown_": map[string]any{}}}
	bytes, _ := json.Marshal(payload)
	return bytes
}

func respondWithBytes(msg *nats.Msg, data []byte) error {
	return msg.Respond(data)
}

func containsBytes(value any) bool {
	switch typed := value.(type) {
	case []byte:
		return true
	case map[string]any:
		for _, v := range typed {
			if containsBytes(v) {
				return true
			}
		}
	case map[any]any:
		for _, v := range typed {
			if containsBytes(v) {
				return true
			}
		}
	case []any:
		for _, v := range typed {
			if containsBytes(v) {
				return true
			}
		}
	case [][]byte:
		return true
	}
	return false
}

func normalizeJSONNumbers(value any) any {
	switch typed := value.(type) {
	case map[string]any:
		normalized := make(map[string]any, len(typed))
		for key, entry := range typed {
			normalized[key] = normalizeJSONNumbers(entry)
		}
		return normalized
	case []any:
		normalized := make([]any, len(typed))
		for i, entry := range typed {
			normalized[i] = normalizeJSONNumbers(entry)
		}
		return normalized
	case json.Number:
		if intval, err := typed.Int64(); err == nil {
			return intval
		}
		if str := typed.String(); !strings.ContainsAny(str, ".eE") && !strings.ContainsRune(str, '.') {
			return typed
		}
		if floatval, err := typed.Float64(); err == nil {
			return floatval
		}
		return typed
	default:
		return typed
	}
}

func boolValue(value any) bool {
	switch typed := value.(type) {
	case bool:
		return typed
	case string:
		flag, err := strconv.ParseBool(typed)
		return err == nil && flag
	case float64:
		return typed != 0
	case float32:
		return typed != 0
	case int:
		return typed != 0
	case int64:
		return typed != 0
	case json.Number:
		flag, err := strconv.ParseFloat(string(typed), 64)
		return err == nil && flag != 0
	default:
		return false
	}
}

func intFromAny(value any) (int, bool) {
	switch typed := value.(type) {
	case int:
		return typed, true
	case int32:
		return int(typed), true
	case int64:
		return int(typed), true
	case float64:
		return int(typed), true
	case float32:
		return int(typed), true
	case json.Number:
		parsed, err := typed.Int64()
		return int(parsed), err == nil
	case string:
		parsed, err := strconv.Atoi(typed)
		return parsed, err == nil
	default:
		return 0, false
	}
}

func cloneStringStringMap(source map[string]string) map[string]string {
	if source == nil {
		return nil
	}
	result := make(map[string]string, len(source))
	for key, value := range source {
		result[key] = value
	}
	return result
}

func firstKey(m map[string]any) string {
	for key := range m {
		return key
	}
	return ""
}

func isNumberTooBigError(err error) bool {
	if err == nil {
		return false
	}
	var numErr *strconv.NumError
	if errors.As(err, &numErr) && numErr.Err == strconv.ErrRange {
		return true
	}
	var unsupported *json.UnsupportedValueError
	if errors.As(err, &unsupported) {
		return true
	}
	var invalid *json.InvalidUTF8Error
	if errors.As(err, &invalid) {
		return true
	}
	var marshaler *json.MarshalerError
	if errors.As(err, &marshaler) {
		return true
	}
	msg := err.Error()
	return strings.Contains(msg, "range") || strings.Contains(msg, "too large") || strings.Contains(msg, "overflow") || strings.Contains(msg, "non-finite") || strings.Contains(msg, "not representable") || strings.Contains(msg, "cannot serialize") || strings.Contains(msg, "value must")
}

func schemaValidationFailureMessage(err error) telepact.Message {
	if err == nil {
		return telepact.NewMessage(map[string]any{}, map[string]any{"Ok_": map[string]any{}})
	}
	var parseErr *telepact.TelepactSchemaParseError
	if errors.As(err, &parseErr) {
		return telepact.NewMessage(
			map[string]any{},
			map[string]any{"ErrorValidationFailure": map[string]any{"cases": parseErr.SchemaParseFailuresPseudoJSON}},
		)
	}
	return telepact.NewMessage(map[string]any{}, map[string]any{"ErrorUnknown_": map[string]any{}})
}

func validatePseudoJSONSchema(input map[string]any) ([]map[string]any, error) {
	schemaRaw, ok := input["schema"]
	if !ok {
		return nil, errors.New("missing schema")
	}

	schemaJSON, err := toJSONString(schemaRaw)
	if err != nil {
		return nil, err
	}

	var extendJSON string
	if extendRaw, ok := input["extend!"]; ok {
		extendJSON, err = toJSONString(extendRaw)
		if err != nil {
			return nil, err
		}

		_, err = telepact.TelepactSchemaFromFileJSONMap(map[string]string{
			"default": schemaJSON,
			"extend":  extendJSON,
		})
	} else {
		_, err = telepact.TelepactSchemaFromJSON(schemaJSON)
	}
	if err == nil {
		return nil, nil
	}

	parseErr, ok := err.(*telepact.TelepactSchemaParseError)
	if !ok {
		return nil, err
	}

	var entries []map[string]any
	switch typed := parseErr.SchemaParseFailuresPseudoJSON.(type) {
	case []map[string]any:
		entries = typed
	case []any:
		entries = make([]map[string]any, 0, len(typed))
		for _, entry := range typed {
			if converted, err := asMap(entry); err == nil {
				entries = append(entries, converted)
			}
		}
	default:
		return nil, fmt.Errorf("unexpected parse failure pseudo json type %T", parseErr.SchemaParseFailuresPseudoJSON)
	}

	result := make([]map[string]any, 0, len(entries))
	for _, converted := range entries {
		failure := make(map[string]any, len(converted))
		if doc, ok := converted["document"].(string); ok {
			failure["document"] = doc
		}
		if loc, ok := converted["location"]; ok {
			failure["location"] = loc
		}
		if path, ok := converted["path"]; ok {
			failure["path"] = path
		}
		if reason, ok := converted["reason"].(map[string]any); ok {
			failure["reason"] = reason
		}
		result = append(result, failure)
	}

	return result, nil
}

func toJSONString(value any) (string, error) {
	switch typed := value.(type) {
	case string:
		return typed, nil
	case json.RawMessage:
		return string(typed), nil
	default:
		bytes, err := json.Marshal(typed)
		if err != nil {
			return "", err
		}
		return string(bytes), nil
	}
}
