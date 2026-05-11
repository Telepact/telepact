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
import { connect, NatsConnection, Subscription } from "nats";
import * as fs from "node:fs";
import * as path from "node:path";
import process from "node:process";
import { telepact as proto } from "./generated/benchmark.js";

type JsonMap = Record<string, any>;

type Scenario = {
    networkLatency: string;
    dataShape: string;
    collectionShape: string;
    method: string;
};

type Sample = {
    clientRequestSerializationTimeNs: number;
    serializedRequestSizeBytes: number;
    requestNetworkTransitTimeNs: number;
    serverRequestDeserializationTimeNs: number;
    serverResponseSerializationTimeNs: number;
    serializedResponseSizeBytes: number;
    responseNetworkTransitTimeNs: number;
    clientResponseDeserializationTimeNs: number;
};

type ServerMetrics = {
    requestNetworkArrivalNs: number;
    serverRequestDeserializationTimeNs: number;
    serverResponseSerializationTimeNs: number;
    responseSentAtNs: number;
};

const NETWORKS = ["close", "far"];
const DATA_SHAPES = ["typical", "all-strings", "all-numbers"];
const COLLECTION_SHAPES = ["single", "small-list", "big-list", "really-big-list", "huge-list"];
const METHODS = ["telepact-json", "telepact-binary", "telepact-packed-binary", "protobuf", "plain-json"];
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
const NATS_REQUEST_TIMEOUT_MS = 15000;
const NATS_REQUEST_ADDITIONAL_RETRIES = 2;
const NATS_REQUEST_RETRY_DELAY_MS = 250;

class MetricsQueue {
    private items: ServerMetrics[] = [];
    private waiters: Array<(value: ServerMetrics) => void> = [];

    push(value: ServerMetrics): void {
        const waiter = this.waiters.shift();
        if (waiter) {
            waiter(value);
            return;
        }
        this.items.push(value);
    }

    async shift(): Promise<ServerMetrics> {
        const value = this.items.shift();
        if (value) {
            return value;
        }
        return await new Promise<ServerMetrics>((resolve) => this.waiters.push(resolve));
    }
}

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

function scenarioRecord(scenario: Scenario, iterations: number, warmupIterations: number, samples: Sample[]) {
    return {
        language: "typescript",
        networkLatency: scenario.networkLatency,
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

async function requestWithRetry(connection: NatsConnection, subject: string, payload: Uint8Array) {
    for (let attempt = 0; attempt <= NATS_REQUEST_ADDITIONAL_RETRIES; attempt += 1) {
        try {
            return await connection.request(subject, payload, { timeout: NATS_REQUEST_TIMEOUT_MS });
        } catch (error) {
            if (attempt >= NATS_REQUEST_ADDITIONAL_RETRIES) {
                throw error;
            }
            await new Promise((resolve) => setTimeout(resolve, NATS_REQUEST_RETRY_DELAY_MS));
        }
    }
    throw new Error("unreachable");
}

async function createPlainJsonRunner(serverConnection: NatsConnection, clientConnection: NatsConnection, subject: string, scenario: Scenario, queue: MetricsQueue) {
    const sub = serverConnection.subscribe(subject);
    (async () => {
        for await (const msg of sub) {
            const receivedAt = nowNs();
            const requestObject = JSON.parse(new TextDecoder().decode(msg.data));
            const afterDeserialize = nowNs();
            const responseObject = { function: requestObject.function, items: requestObject.items };
            const beforeSerialize = nowNs();
            const responseBytes = new TextEncoder().encode(JSON.stringify(responseObject));
            const responseSentAt = nowNs();
            queue.push({
                requestNetworkArrivalNs: receivedAt,
                serverRequestDeserializationTimeNs: afterDeserialize - receivedAt,
                serverResponseSerializationTimeNs: responseSentAt - beforeSerialize,
                responseSentAtNs: responseSentAt,
            });
            msg.respond(responseBytes);
        }
    })();

    return {
        subscription: sub,
        requestOnce: async (payload: JsonMap[]): Promise<Sample> => {
            const requestObject = { function: PLAIN_FUNCTION_NAMES[scenario.dataShape], items: payload };
            const serializeStart = nowNs();
            const requestBytes = new TextEncoder().encode(JSON.stringify(requestObject));
            const serializeEnd = nowNs();
            const sentAt = nowNs();
            const response = await requestWithRetry(clientConnection, subject, requestBytes);
            const receivedAt = nowNs();
            const deserializeStart = nowNs();
            const responseObject = JSON.parse(new TextDecoder().decode(response.data));
            const deserializeEnd = nowNs();
            if (JSON.stringify(responseObject.items) !== JSON.stringify(payload)) {
                throw new Error("plain-json payload mismatch");
            }
            const serverMetrics = await queue.shift();
            return {
                clientRequestSerializationTimeNs: serializeEnd - serializeStart,
                serializedRequestSizeBytes: requestBytes.length,
                requestNetworkTransitTimeNs: serverMetrics.requestNetworkArrivalNs - sentAt,
                serverRequestDeserializationTimeNs: serverMetrics.serverRequestDeserializationTimeNs,
                serverResponseSerializationTimeNs: serverMetrics.serverResponseSerializationTimeNs,
                serializedResponseSizeBytes: response.data.length,
                responseNetworkTransitTimeNs: receivedAt - serverMetrics.responseSentAtNs,
                clientResponseDeserializationTimeNs: deserializeEnd - deserializeStart,
            };
        },
    };
}

async function createProtobufRunner(serverConnection: NatsConnection, clientConnection: NatsConnection, subject: string, scenario: Scenario, queue: MetricsQueue) {
    const requestType = PROTO_TYPES[scenario.dataShape]!.request;
    const responseType = PROTO_TYPES[scenario.dataShape]!.response;
    const sub = serverConnection.subscribe(subject);
    (async () => {
        for await (const msg of sub) {
            const receivedAt = nowNs();
            const requestMessage = requestType.decode(msg.data);
            const afterDeserialize = nowNs();
            const responseMessage = responseType.create({ items: requestMessage.items });
            const beforeSerialize = nowNs();
            const responseBytes = responseType.encode(responseMessage).finish();
            const responseSentAt = nowNs();
            queue.push({
                requestNetworkArrivalNs: receivedAt,
                serverRequestDeserializationTimeNs: afterDeserialize - receivedAt,
                serverResponseSerializationTimeNs: responseSentAt - beforeSerialize,
                responseSentAtNs: responseSentAt,
            });
            msg.respond(responseBytes);
        }
    })();

    return {
        subscription: sub,
        requestOnce: async (payload: JsonMap[]): Promise<Sample> => {
            const requestMessage = requestType.create({ items: payload });
            const serializeStart = nowNs();
            const requestBytes = requestType.encode(requestMessage).finish();
            const serializeEnd = nowNs();
            const sentAt = nowNs();
            const response = await requestWithRetry(clientConnection, subject, requestBytes);
            const receivedAt = nowNs();
            const deserializeStart = nowNs();
            const responseMessage = responseType.decode(response.data);
            const deserializeEnd = nowNs();
            if ((responseMessage.items ?? []).length !== payload.length) {
                throw new Error("protobuf payload mismatch");
            }
            const serverMetrics = await queue.shift();
            return {
                clientRequestSerializationTimeNs: serializeEnd - serializeStart,
                serializedRequestSizeBytes: requestBytes.length,
                requestNetworkTransitTimeNs: serverMetrics.requestNetworkArrivalNs - sentAt,
                serverRequestDeserializationTimeNs: serverMetrics.serverRequestDeserializationTimeNs,
                serverResponseSerializationTimeNs: serverMetrics.serverResponseSerializationTimeNs,
                serializedResponseSizeBytes: response.data.length,
                responseNetworkTransitTimeNs: receivedAt - serverMetrics.responseSentAtNs,
                clientResponseDeserializationTimeNs: deserializeEnd - deserializeStart,
            };
        },
    };
}

async function createTelepactRunner(serverConnection: NatsConnection, clientConnection: NatsConnection, subject: string, scenario: Scenario, queue: MetricsQueue) {
    const telepactSchema = TelepactSchema.fromDirectory(schemaPath(), fs, path);
    const serverState: { afterDeserializeNs?: number; beforeSerializeNs?: number } = {};
    const functionRoutes = {
        "fn.roundTripTypical": async (functionName: string, requestMessage: Message): Promise<Message> => new Message({}, { Ok_: { items: requestMessage.body[functionName].items } }),
        "fn.roundTripStrings": async (functionName: string, requestMessage: Message): Promise<Message> => new Message({}, { Ok_: { items: requestMessage.body[functionName].items } }),
        "fn.roundTripNumbers": async (functionName: string, requestMessage: Message): Promise<Message> => new Message({}, { Ok_: { items: requestMessage.body[functionName].items } }),
    };
    const options = new ServerOptions();
    options.authRequired = false;
    options.onRequest = () => { serverState.afterDeserializeNs = nowNs(); };
    options.onResponse = () => { serverState.beforeSerializeNs = nowNs(); };
    const server = new Server(telepactSchema, new FunctionRouter(functionRoutes), options);

    const sub = serverConnection.subscribe(subject);
    (async () => {
        for await (const msg of sub) {
            const receivedAt = nowNs();
            serverState.afterDeserializeNs = undefined;
            serverState.beforeSerializeNs = undefined;
            const response = await server.process(msg.data);
            const responseSentAt = nowNs();
            queue.push({
                requestNetworkArrivalNs: receivedAt,
                serverRequestDeserializationTimeNs: (serverState.afterDeserializeNs ?? responseSentAt) - receivedAt,
                serverResponseSerializationTimeNs: responseSentAt - (serverState.beforeSerializeNs ?? receivedAt),
                responseSentAtNs: responseSentAt,
            });
            msg.respond(response.bytes);
        }
    })();

    let lastSample: Sample | null = null;
    const adapter = async (message: Message, serializer: any): Promise<Message> => {
        const serializeStart = nowNs();
        const requestBytes = serializer.serialize(message);
        const serializeEnd = nowNs();
        const sentAt = nowNs();
        const response = await requestWithRetry(clientConnection, subject, requestBytes);
        const receivedAt = nowNs();
        const deserializeStart = nowNs();
        const responseMessage = serializer.deserialize(response.data);
        const deserializeEnd = nowNs();
        const serverMetrics = await queue.shift();
        lastSample = {
            clientRequestSerializationTimeNs: serializeEnd - serializeStart,
            serializedRequestSizeBytes: requestBytes.length,
            requestNetworkTransitTimeNs: serverMetrics.requestNetworkArrivalNs - sentAt,
            serverRequestDeserializationTimeNs: serverMetrics.serverRequestDeserializationTimeNs,
            serverResponseSerializationTimeNs: serverMetrics.serverResponseSerializationTimeNs,
            serializedResponseSizeBytes: response.data.length,
            responseNetworkTransitTimeNs: receivedAt - serverMetrics.responseSentAtNs,
            clientResponseDeserializationTimeNs: deserializeEnd - deserializeStart,
        };
        return responseMessage;
    };
    const clientOptions = new ClientOptions();
    clientOptions.useBinary = scenario.method !== "telepact-json";
    clientOptions.alwaysSendJson = scenario.method === "telepact-json";
    const client = new Client(adapter, clientOptions);

    return {
        subscription: sub,
        requestOnce: async (payload: JsonMap[]): Promise<Sample> => {
            const headers = scenario.method === "telepact-packed-binary" ? { "@pac_": true } : {};
            const functionName = FUNCTION_NAMES[scenario.dataShape]!;
            const response = await client.request(new Message(headers, { [functionName]: { items: payload } }));
            if (JSON.stringify(response.body.Ok_.items) !== JSON.stringify(payload)) {
                throw new Error("telepact payload mismatch");
            }
            return lastSample!;
        },
    };
}

async function createRunner(serverConnection: NatsConnection, clientConnection: NatsConnection, subject: string, scenario: Scenario, queue: MetricsQueue) {
    switch (scenario.method) {
        case "plain-json":
            return await createPlainJsonRunner(serverConnection, clientConnection, subject, scenario, queue);
        case "protobuf":
            return await createProtobufRunner(serverConnection, clientConnection, subject, scenario, queue);
        default:
            return await createTelepactRunner(serverConnection, clientConnection, subject, scenario, queue);
    }
}

async function main() {
    const args = parseArgs();
    const iterations = Number(args["iterations"]);
    const warmupIterations = Number(args["warmup-iterations"]);
    const localNatsUrl = args["local-nats-url"];
    const remoteNatsUrl = args["remote-nats-url"];
    const output = args["output"];
    const payloads = loadPayloads();
    const scenarios: any[] = [];

    for (const networkLatency of NETWORKS) {
        const natsUrl = networkLatency === "close" ? localNatsUrl : remoteNatsUrl;
        const clientConnection = await connect({ servers: natsUrl });
        const serverConnection = await connect({ servers: natsUrl });
        try {
            for (const dataShape of DATA_SHAPES) {
                for (const collectionShape of COLLECTION_SHAPES) {
                    for (const method of METHODS) {
                        const scenario: Scenario = { networkLatency, dataShape, collectionShape, method };
                        const queue = new MetricsQueue();
                        const subject = `perf.ts.${Date.now()}.${Math.random().toString(16).slice(2)}`;
                        const runner = await createRunner(serverConnection, clientConnection, subject, scenario, queue);
                        const payload = payloads[dataShape]![collectionShape]!;
                        try {
                            for (let index = 0; index < warmupIterations; index += 1) {
                                await runner.requestOnce(payload);
                            }
                            const samples: Sample[] = [];
                            for (let index = 0; index < iterations; index += 1) {
                                samples.push(await runner.requestOnce(payload));
                            }
                            scenarios.push(scenarioRecord(scenario, iterations, warmupIterations, samples));
                        } finally {
                            await runner.subscription.drain();
                        }
                    }
                }
            }
        } finally {
            await clientConnection.close();
            await serverConnection.close();
        }
    }

    fs.writeFileSync(output, JSON.stringify({
        metadata: {
            language: "typescript",
            generatedAt: new Date().toISOString(),
            iterations,
            warmupIterations,
            localNatsUrl,
            remoteNatsUrl,
        },
        scenarios,
    }, null, 2) + "\n");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
