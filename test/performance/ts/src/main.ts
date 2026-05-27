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

import { Client, ClientOptions, FunctionRouter, Message, Server, ServerOptions, TelepactSchema } from "telepact";
import * as fs from "node:fs";
import * as path from "node:path";
import process from "node:process";
import { telepact as proto } from "./generated/benchmark.js";

type JsonMap = Record<string, any>;

type Scenario = {
    dataShape: string;
    collectionShape: string;
    method: string;
};

type Sample = {
    requestSerializationTimeNs: number;
    requestDeserializationTimeNs: number;
    responseSerializationTimeNs: number;
    responseDeserializationTimeNs: number;
    serializedRequestSizeBytes: number;
    serializedResponseSizeBytes: number;
};

const DATA_SHAPES = ["typical", "all-strings", "all-numbers"] as const;
const COLLECTION_SHAPES = ["single", "small-list", "big-list", "really-big-list", "huge-list"] as const;
const METHODS = ["telepact-json", "telepact-binary", "telepact-packed-binary", "protobuf", "plain-json"] as const;
const FUNCTION_NAMES: Record<string, string> = {
    "typical": "fn.roundTripTypical",
    "all-strings": "fn.roundTripStrings",
    "all-numbers": "fn.roundTripNumbers",
};
const PLAIN_FUNCTION_NAMES: Record<string, string> = {
    "typical": "roundTripTypical",
    "all-strings": "roundTripStrings",
    "all-numbers": "roundTripNumbers",
};
const PROTO_TYPES: Record<string, { request: any; response: any }> = {
    "typical": { request: proto.performance.v1.TypicalRequest, response: proto.performance.v1.TypicalResponse },
    "all-strings": { request: proto.performance.v1.StringsRequest, response: proto.performance.v1.StringsResponse },
    "all-numbers": { request: proto.performance.v1.NumbersRequest, response: proto.performance.v1.NumbersResponse },
};

function nowNs(): number {
    return Number(process.hrtime.bigint());
}

function parseArgs(): Record<string, string> {
    const parsed: Record<string, string> = {};
    for (let index = 2; index < process.argv.length; index += 2) {
        parsed[process.argv[index]!.replace(/^--/, "")] = process.argv[index + 1]!;
    }
    return parsed;
}

function parseCsv(value: string | undefined, fallback: readonly string[]): string[] {
    if (!value) {
        return [...fallback];
    }
    const selected = value.split(",").filter(Boolean);
    return selected.length > 0 ? selected : [...fallback];
}

function scenarioRecord(scenario: Scenario, iterations: number, warmupIterations: number, samples: Sample[]) {
    return {
        language: "typescript",
        dataShape: scenario.dataShape,
        collectionShape: scenario.collectionShape,
        method: scenario.method,
        iterations,
        warmupIterations,
        samples,
    };
}

function loadPayloads(): Record<string, Record<string, JsonMap[]>> {
    const payloadPath = path.resolve(process.cwd(), "../payloads/cases.json");
    return JSON.parse(fs.readFileSync(payloadPath, "utf-8"));
}

function schemaPath(): string {
    return path.resolve(process.cwd(), "../schema/telepact");
}

function warmupIterationsForScenario(scenario: Scenario, warmupIterations: number): number {
    return scenario.method === "telepact-binary" || scenario.method === "telepact-packed-binary"
        ? warmupIterations
        : 0;
}

function createPlainJsonBenchmark(scenario: Scenario) {
    return (payload: JsonMap[]): Sample => {
        const requestObject = { function: PLAIN_FUNCTION_NAMES[scenario.dataShape], items: payload };
        const requestSerializeStart = nowNs();
        const requestBytes = new TextEncoder().encode(JSON.stringify(requestObject));
        const requestSerializeEnd = nowNs();
        const requestDeserializeStart = nowNs();
        const requestRoundTrip = JSON.parse(new TextDecoder().decode(requestBytes));
        const requestDeserializeEnd = nowNs();
        if (JSON.stringify(requestRoundTrip.items) !== JSON.stringify(payload)) {
            throw new Error("plain-json payload mismatch");
        }

        const responseObject = { function: requestRoundTrip.function, items: requestRoundTrip.items };
        const responseSerializeStart = nowNs();
        const responseBytes = new TextEncoder().encode(JSON.stringify(responseObject));
        const responseSerializeEnd = nowNs();
        const responseDeserializeStart = nowNs();
        const responseRoundTrip = JSON.parse(new TextDecoder().decode(responseBytes));
        const responseDeserializeEnd = nowNs();
        if (JSON.stringify(responseRoundTrip.items) !== JSON.stringify(payload)) {
            throw new Error("plain-json response mismatch");
        }

        return {
            requestSerializationTimeNs: requestSerializeEnd - requestSerializeStart,
            requestDeserializationTimeNs: requestDeserializeEnd - requestDeserializeStart,
            responseSerializationTimeNs: responseSerializeEnd - responseSerializeStart,
            responseDeserializationTimeNs: responseDeserializeEnd - responseDeserializeStart,
            serializedRequestSizeBytes: requestBytes.length,
            serializedResponseSizeBytes: responseBytes.length,
        };
    };
}

function createProtobufBenchmark(scenario: Scenario) {
    const requestType = PROTO_TYPES[scenario.dataShape]!.request;
    const responseType = PROTO_TYPES[scenario.dataShape]!.response;

    return (payload: JsonMap[]): Sample => {
        const requestMessage = requestType.create({ items: payload });
        const requestSerializeStart = nowNs();
        const requestBytes = requestType.encode(requestMessage).finish();
        const requestSerializeEnd = nowNs();
        const requestDeserializeStart = nowNs();
        const requestRoundTrip = requestType.decode(requestBytes);
        const requestDeserializeEnd = nowNs();
        if ((requestRoundTrip.items ?? []).length !== payload.length) {
            throw new Error("protobuf payload mismatch");
        }

        const responseMessage = responseType.create({ items: requestRoundTrip.items });
        const responseSerializeStart = nowNs();
        const responseBytes = responseType.encode(responseMessage).finish();
        const responseSerializeEnd = nowNs();
        const responseDeserializeStart = nowNs();
        const responseRoundTrip = responseType.decode(responseBytes);
        const responseDeserializeEnd = nowNs();
        if ((responseRoundTrip.items ?? []).length !== payload.length) {
            throw new Error("protobuf response mismatch");
        }

        return {
            requestSerializationTimeNs: requestSerializeEnd - requestSerializeStart,
            requestDeserializationTimeNs: requestDeserializeEnd - requestDeserializeStart,
            responseSerializationTimeNs: responseSerializeEnd - responseSerializeStart,
            responseDeserializationTimeNs: responseDeserializeEnd - responseDeserializeStart,
            serializedRequestSizeBytes: requestBytes.length,
            serializedResponseSizeBytes: responseBytes.length,
        };
    };
}

function createTelepactBenchmark(scenario: Scenario) {
    const client = new Client(async () => { throw new Error("unused benchmark adapter"); }, new ClientOptions());
    const serverOptions = new ServerOptions();
    serverOptions.authRequired = false;
    const server = new Server(TelepactSchema.fromDirectory(schemaPath(), fs, path), new FunctionRouter({}), serverOptions);
    const clientSerializer = (client as any).serializer;
    const serverSerializer = (server as any).serializer;
    const functionName = FUNCTION_NAMES[scenario.dataShape]!;

    return (payload: JsonMap[]): Sample => {
        const requestHeaders: Record<string, any> = {};
        if (scenario.method !== "telepact-json") {
            requestHeaders["@binary_"] = true;
        }
        if (scenario.method === "telepact-packed-binary") {
            requestHeaders["@pac_"] = true;
        }

        const requestMessage = new Message(requestHeaders, { [functionName]: { items: payload } });
        const requestSerializeStart = nowNs();
        const requestBytes = clientSerializer.serialize(requestMessage);
        const requestSerializeEnd = nowNs();
        const requestDeserializeStart = nowNs();
        const requestRoundTrip = serverSerializer.deserialize(requestBytes);
        const requestDeserializeEnd = nowNs();
        if (JSON.stringify(requestRoundTrip.body[functionName].items) !== JSON.stringify(payload)) {
            throw new Error("telepact payload mismatch");
        }

        const responseHeaders: Record<string, any> = {};
        if ("@bin_" in requestRoundTrip.headers) {
            responseHeaders["@binary_"] = true;
            responseHeaders["@clientKnownBinaryChecksums_"] = requestRoundTrip.headers["@bin_"];
        }
        if ("@pac_" in requestRoundTrip.headers) {
            responseHeaders["@pac_"] = requestRoundTrip.headers["@pac_"];
        }
        const responseMessage = new Message(responseHeaders, { Ok_: { items: requestRoundTrip.body[functionName].items } });
        const responseSerializeStart = nowNs();
        const responseBytes = serverSerializer.serialize(responseMessage);
        const responseSerializeEnd = nowNs();
        const responseDeserializeStart = nowNs();
        const responseRoundTrip = clientSerializer.deserialize(responseBytes);
        const responseDeserializeEnd = nowNs();
        if (JSON.stringify(responseRoundTrip.body.Ok_.items) !== JSON.stringify(payload)) {
            throw new Error("telepact response mismatch");
        }

        return {
            requestSerializationTimeNs: requestSerializeEnd - requestSerializeStart,
            requestDeserializationTimeNs: requestDeserializeEnd - requestDeserializeStart,
            responseSerializationTimeNs: responseSerializeEnd - responseSerializeStart,
            responseDeserializationTimeNs: responseDeserializeEnd - responseDeserializeStart,
            serializedRequestSizeBytes: requestBytes.length,
            serializedResponseSizeBytes: responseBytes.length,
        };
    };
}

function createBenchmark(scenario: Scenario) {
    switch (scenario.method) {
        case "plain-json":
            return createPlainJsonBenchmark(scenario);
        case "protobuf":
            return createProtobufBenchmark(scenario);
        default:
            return createTelepactBenchmark(scenario);
    }
}

async function main() {
    const args = parseArgs();
    const iterations = Number(args["iterations"]);
    const warmupIterations = Number(args["warmup-iterations"]);
    const dataShapes = parseCsv(args["data-shapes"], DATA_SHAPES);
    const collectionShapes = parseCsv(args["collection-shapes"], COLLECTION_SHAPES);
    const methods = parseCsv(args["methods"], METHODS);
    const output = args["output"];
    const payloads = loadPayloads();
    const scenarios: any[] = [];

    for (const dataShape of dataShapes) {
        for (const collectionShape of collectionShapes) {
            for (const method of methods) {
                const scenario: Scenario = { dataShape, collectionShape, method };
                const benchmarkOnce = createBenchmark(scenario);
                const payload = payloads[dataShape]![collectionShape]!;
                const scenarioWarmupIterations = warmupIterationsForScenario(scenario, warmupIterations);
                for (let index = 0; index < scenarioWarmupIterations; index += 1) {
                    benchmarkOnce(payload);
                }
                const samples: Sample[] = [];
                for (let index = 0; index < iterations; index += 1) {
                    samples.push(benchmarkOnce(payload));
                }
                scenarios.push(scenarioRecord(scenario, iterations, scenarioWarmupIterations, samples));
            }
        }
    }

    fs.writeFileSync(output, JSON.stringify({
        metadata: {
            language: "typescript",
            generatedAt: new Date().toISOString(),
            iterations,
            warmupIterations,
            dataShapes,
            collectionShapes,
            methods,
        },
        scenarios,
    }, null, 2) + "\n");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
