//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	telepact "github.com/telepact/telepact/lib/go"
)

var dataShapes = []string{"typical", "all-strings", "all-numbers"}
var collectionShapes = []string{"single", "small-list", "big-list", "really-big-list", "huge-list"}
var methods = []string{"telepact-json", "telepact-binary", "plain-json"}

var functionNames = map[string]string{
	"typical":     "fn.roundTripTypical",
	"all-strings": "fn.roundTripStrings",
	"all-numbers": "fn.roundTripNumbers",
}

var plainFunctionNames = map[string]string{
	"typical":     "roundTripTypical",
	"all-strings": "roundTripStrings",
	"all-numbers": "roundTripNumbers",
}

type scenario struct {
	dataShape       string
	collectionShape string
	method          string
}

type sample struct {
	RequestSerializationTimeNs    int64 `json:"requestSerializationTimeNs"`
	RequestDeserializationTimeNs  int64 `json:"requestDeserializationTimeNs"`
	ResponseSerializationTimeNs   int64 `json:"responseSerializationTimeNs"`
	ResponseDeserializationTimeNs int64 `json:"responseDeserializationTimeNs"`
	SerializedRequestSizeBytes    int   `json:"serializedRequestSizeBytes"`
	SerializedResponseSizeBytes   int   `json:"serializedResponseSizeBytes"`
}

type scenarioResult struct {
	Language         string   `json:"language"`
	DataShape        string   `json:"dataShape"`
	CollectionShape  string   `json:"collectionShape"`
	Method           string   `json:"method"`
	Iterations       int      `json:"iterations"`
	WarmupIterations int      `json:"warmupIterations"`
	Samples          []sample `json:"samples"`
}

func main() {
	iterations := flag.Int("iterations", 0, "")
	warmupIterations := flag.Int("warmup-iterations", 0, "")
	dataShapeArg := flag.String("data-shapes", "", "")
	collectionShapeArg := flag.String("collection-shapes", "", "")
	methodArg := flag.String("methods", "", "")
	output := flag.String("output", "", "")
	flag.Parse()

	selectedDataShapes := parseCSV(*dataShapeArg, dataShapes)
	selectedCollectionShapes := parseCSV(*collectionShapeArg, collectionShapes)
	selectedMethods := parseCSV(*methodArg, methods)

	payloads, err := loadPayloads()
	if err != nil {
		panic(err)
	}

	schema, err := telepact.TelepactSchemaFromDirectory(filepath.Join("..", "schema", "telepact"))
	if err != nil {
		panic(err)
	}

	results := make([]scenarioResult, 0)
	for _, dataShape := range selectedDataShapes {
		for _, collectionShape := range selectedCollectionShapes {
			payload := payloads[dataShape][collectionShape]
			for _, method := range selectedMethods {
				scenario := scenario{dataShape: dataShape, collectionShape: collectionShape, method: method}
				benchmarkOnce, err := createBenchmark(schema, scenario)
				if err != nil {
					panic(err)
				}
				scenarioWarmupIterations := 0
				if method == "telepact-binary" {
					scenarioWarmupIterations = *warmupIterations
				}
				for index := 0; index < scenarioWarmupIterations; index++ {
					if _, err := benchmarkOnce(payload); err != nil {
						panic(err)
					}
				}
				samples := make([]sample, 0, *iterations)
				for index := 0; index < *iterations; index++ {
					sample, err := benchmarkOnce(payload)
					if err != nil {
						panic(err)
					}
					samples = append(samples, sample)
				}
				results = append(results, scenarioResult{
					Language:         "go",
					DataShape:        dataShape,
					CollectionShape:  collectionShape,
					Method:           method,
					Iterations:       *iterations,
					WarmupIterations: scenarioWarmupIterations,
					Samples:          samples,
				})
			}
		}
	}

	outputData := map[string]any{
		"metadata": map[string]any{
			"language":         "go",
			"generatedAt":      time.Now().UTC().Format(time.RFC3339Nano),
			"iterations":       *iterations,
			"warmupIterations": *warmupIterations,
			"dataShapes":       selectedDataShapes,
			"collectionShapes": selectedCollectionShapes,
			"methods":          selectedMethods,
		},
		"scenarios": results,
	}
	encoded, err := json.MarshalIndent(outputData, "", "  ")
	if err != nil {
		panic(err)
	}
	encoded = append(encoded, '\n')
	if err := os.WriteFile(*output, encoded, 0o644); err != nil {
		panic(err)
	}
}

func createBenchmark(schema *telepact.TelepactSchema, scenario scenario) (func([]any) (sample, error), error) {
	switch scenario.method {
	case "plain-json":
		return createPlainJSONBenchmark(scenario), nil
	case "telepact-json", "telepact-binary":
		return createTelepactBenchmark(schema, scenario)
	default:
		return nil, fmt.Errorf("unsupported go performance method: %s", scenario.method)
	}
}

func createPlainJSONBenchmark(scenario scenario) func([]any) (sample, error) {
	functionName := plainFunctionNames[scenario.dataShape]
	return func(payload []any) (sample, error) {
		requestObject := map[string]any{"function": functionName, "items": payload}
		requestSerializeStart := time.Now()
		requestBytes, err := json.Marshal(requestObject)
		requestSerializeEnd := time.Now()
		if err != nil {
			return sample{}, err
		}

		requestDeserializeStart := time.Now()
		requestRoundTrip, err := decodeJSONMap(requestBytes)
		requestDeserializeEnd := time.Now()
		if err != nil {
			return sample{}, err
		}
		if itemCount(requestRoundTrip["items"]) != len(payload) {
			return sample{}, errors.New("plain-json request mismatch")
		}

		responseObject := map[string]any{"function": requestRoundTrip["function"], "items": requestRoundTrip["items"]}
		responseSerializeStart := time.Now()
		responseBytes, err := json.Marshal(responseObject)
		responseSerializeEnd := time.Now()
		if err != nil {
			return sample{}, err
		}

		responseDeserializeStart := time.Now()
		responseRoundTrip, err := decodeJSONMap(responseBytes)
		responseDeserializeEnd := time.Now()
		if err != nil {
			return sample{}, err
		}
		if itemCount(responseRoundTrip["items"]) != len(payload) {
			return sample{}, errors.New("plain-json response mismatch")
		}

		return sample{
			RequestSerializationTimeNs:    requestSerializeEnd.Sub(requestSerializeStart).Nanoseconds(),
			RequestDeserializationTimeNs:  requestDeserializeEnd.Sub(requestDeserializeStart).Nanoseconds(),
			ResponseSerializationTimeNs:   responseSerializeEnd.Sub(responseSerializeStart).Nanoseconds(),
			ResponseDeserializationTimeNs: responseDeserializeEnd.Sub(responseDeserializeStart).Nanoseconds(),
			SerializedRequestSizeBytes:    len(requestBytes),
			SerializedResponseSizeBytes:   len(responseBytes),
		}, nil
	}
}

func createTelepactBenchmark(schema *telepact.TelepactSchema, scenario scenario) (func([]any) (sample, error), error) {
	client, err := telepact.NewClient(func(context.Context, telepact.Message, *telepact.Serializer) (telepact.Message, error) {
		return telepact.Message{}, errors.New("unused benchmark adapter")
	}, telepact.NewClientOptions())
	if err != nil {
		return nil, err
	}

	serverOptions := telepact.NewServerOptions()
	serverOptions.AuthRequired = false
	server, err := telepact.NewServer(schema, telepact.NewFunctionRouter(map[string]telepact.FunctionRoute{}), serverOptions)
	if err != nil {
		return nil, err
	}

	clientSerializer := client.Serializer()
	serverSerializer := server.Serializer()
	functionName := functionNames[scenario.dataShape]

	return func(payload []any) (sample, error) {
		requestHeaders := map[string]any{}
		if scenario.method != "telepact-json" {
			requestHeaders["@binary_"] = true
		}
		requestMessage := telepact.Message{
			Headers: requestHeaders,
			Body:    map[string]any{functionName: map[string]any{"items": payload}},
		}

		requestSerializeStart := time.Now()
		requestBytes, err := clientSerializer.Serialize(requestMessage)
		requestSerializeEnd := time.Now()
		if err != nil {
			return sample{}, err
		}

		requestDeserializeStart := time.Now()
		requestRoundTrip, err := serverSerializer.Deserialize(requestBytes)
		requestDeserializeEnd := time.Now()
		if err != nil {
			return sample{}, err
		}
		requestItems := nestedItems(requestRoundTrip.Body, functionName)
		if itemCount(requestItems) != len(payload) {
			return sample{}, errors.New("telepact request mismatch")
		}

		responseHeaders := map[string]any{}
		if checksums, ok := requestRoundTrip.Headers["@bin_"]; ok {
			responseHeaders["@binary_"] = true
			responseHeaders["@clientKnownBinaryChecksums_"] = checksums
		}
		responseMessage := telepact.Message{
			Headers: responseHeaders,
			Body:    map[string]any{"Ok_": map[string]any{"items": requestItems}},
		}

		responseSerializeStart := time.Now()
		responseBytes, err := serverSerializer.Serialize(responseMessage)
		responseSerializeEnd := time.Now()
		if err != nil {
			return sample{}, err
		}

		responseDeserializeStart := time.Now()
		responseRoundTrip, err := clientSerializer.Deserialize(responseBytes)
		responseDeserializeEnd := time.Now()
		if err != nil {
			return sample{}, err
		}
		if itemCount(nestedItems(responseRoundTrip.Body, "Ok_")) != len(payload) {
			return sample{}, errors.New("telepact response mismatch")
		}

		return sample{
			RequestSerializationTimeNs:    requestSerializeEnd.Sub(requestSerializeStart).Nanoseconds(),
			RequestDeserializationTimeNs:  requestDeserializeEnd.Sub(requestDeserializeStart).Nanoseconds(),
			ResponseSerializationTimeNs:   responseSerializeEnd.Sub(responseSerializeStart).Nanoseconds(),
			ResponseDeserializationTimeNs: responseDeserializeEnd.Sub(responseDeserializeStart).Nanoseconds(),
			SerializedRequestSizeBytes:    len(requestBytes),
			SerializedResponseSizeBytes:   len(responseBytes),
		}, nil
	}, nil
}

func loadPayloads() (map[string]map[string][]any, error) {
	file, err := os.Open(filepath.Join("..", "payloads", "cases.json"))
	if err != nil {
		return nil, err
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	decoder.UseNumber()
	var payloads map[string]map[string][]any
	if err := decoder.Decode(&payloads); err != nil {
		return nil, err
	}
	for _, byCollectionShape := range payloads {
		for collectionShape, items := range byCollectionShape {
			for index, item := range items {
				items[index] = normalizeLoadedValue(item)
			}
			byCollectionShape[collectionShape] = items
		}
	}
	return payloads, nil
}

func decodeJSONMap(data []byte) (map[string]any, error) {
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.UseNumber()
	var out map[string]any
	err := decoder.Decode(&out)
	return out, err
}

func nestedItems(body map[string]any, key string) any {
	payload, ok := body[key].(map[string]any)
	if !ok {
		return nil
	}
	return payload["items"]
}

func itemCount(value any) int {
	switch typed := value.(type) {
	case []any:
		return len(typed)
	default:
		return -1
	}
}

func normalizeLoadedValue(value any) any {
	switch typed := value.(type) {
	case map[string]any:
		for key, val := range typed {
			typed[key] = normalizeLoadedValue(val)
		}
		return typed
	case []any:
		for index, val := range typed {
			typed[index] = normalizeLoadedValue(val)
		}
		return typed
	case json.Number:
		raw := string(typed)
		if !strings.ContainsAny(raw, ".eE") {
			if parsed, err := strconv.ParseInt(raw, 10, 64); err == nil {
				return parsed
			}
		}
		if parsed, err := strconv.ParseFloat(raw, 64); err == nil {
			return parsed
		}
		return typed
	default:
		return value
	}
}

func parseCSV(value string, fallback []string) []string {
	if value == "" {
		return append([]string(nil), fallback...)
	}
	parts := strings.Split(value, ",")
	selected := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			selected = append(selected, part)
		}
	}
	if len(selected) == 0 {
		return append([]string(nil), fallback...)
	}
	return selected
}
