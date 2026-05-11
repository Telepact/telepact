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

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import protobuf from 'protobufjs';
import { connect, headers, Msg, NatsConnection, Subscription } from 'nats';
import { Client, ClientOptions, FunctionRouter, Message, Server, ServerOptions, TelepactSchema } from 'telepact';

const ROOT = '/home/runner/work/telepact/telepact/test/performance';
const CONFIG = JSON.parse(fs.readFileSync(path.join(ROOT, 'config', 'benchmark-config.json'), 'utf8'));
const PAYLOADS = JSON.parse(fs.readFileSync(path.join(ROOT, 'config', 'payloads.json'), 'utf8'));
const LANGUAGE = 'typescript';
const NATS_URL = process.env.NATS_URL ?? CONFIG.natsUrl;
const SERVER_HEADER_NAMES = {
    receivedWallNs: 'x-telepact-perf-server-received-wall-ns',
    requestDeserializeNs: 'x-telepact-perf-server-request-deserialize-ns',
    responseSerializeNs: 'x-telepact-perf-server-response-serialize-ns',
    sentWallNs: 'x-telepact-perf-server-sent-wall-ns',
};

type Sample = {
    client_request_serialize_ns: number;
    request_size_bytes: number;
    request_network_transit_ns: number;
    server_request_deserialize_ns: number;
    server_response_serialize_ns: number;
    response_size_bytes: number;
    response_network_transit_ns: number;
    client_response_deserialize_ns: number;
    round_trip_ns: number;
};

type BenchmarkCase = {
    language: string;
    method: string;
    data_shape: string;
    collection_shape: string;
    samples: Sample[];
};

type ServerMeasurement = {
    startPerfNs: bigint;
    receivedWallNs: bigint;
    requestDeserializeNs?: bigint;
    serializeStartNs?: bigint;
    responseSerializeNs?: bigint;
    sentWallNs?: bigint;
};

function subjectFor(method: string, dataShape: string): string {
    return `${CONFIG.subjectPrefix}.${LANGUAGE}.${method}.${CONFIG.dataShapes[dataShape].subjectSuffix}`;
}

function nowWallNs(): bigint {
    return BigInt(Date.now()) * 1_000_000n;
}

function metricHeaders(measurement: ServerMeasurement) {
    const h = headers();
    h.set(SERVER_HEADER_NAMES.receivedWallNs, measurement.receivedWallNs.toString());
    h.set(SERVER_HEADER_NAMES.requestDeserializeNs, (measurement.requestDeserializeNs ?? 0n).toString());
    h.set(SERVER_HEADER_NAMES.responseSerializeNs, (measurement.responseSerializeNs ?? 0n).toString());
    h.set(SERVER_HEADER_NAMES.sentWallNs, (measurement.sentWallNs ?? 0n).toString());
    return h;
}

function parseMetricHeaders(msg: Msg) {
    if (!msg.headers) {
        throw new Error('Missing NATS headers on benchmark response');
    }
    return {
        receivedWallNs: BigInt(msg.headers.get(SERVER_HEADER_NAMES.receivedWallNs) ?? '0'),
        requestDeserializeNs: BigInt(msg.headers.get(SERVER_HEADER_NAMES.requestDeserializeNs) ?? '0'),
        responseSerializeNs: BigInt(msg.headers.get(SERVER_HEADER_NAMES.responseSerializeNs) ?? '0'),
        sentWallNs: BigInt(msg.headers.get(SERVER_HEADER_NAMES.sentWallNs) ?? '0'),
    };
}

function toNumber(value: bigint): number {
    return Number(value);
}

function sampleFromTimings(
    requestSerializeNs: bigint,
    requestSizeBytes: number,
    requestSentWallNs: bigint,
    serverMetrics: ReturnType<typeof parseMetricHeaders>,
    responseSizeBytes: number,
    responseReceivedWallNs: bigint,
    responseDeserializeNs: bigint,
    roundTripNs: bigint,
): Sample {
    return {
        client_request_serialize_ns: toNumber(requestSerializeNs),
        request_size_bytes: requestSizeBytes,
        request_network_transit_ns: toNumber(
            serverMetrics.receivedWallNs > requestSentWallNs ? serverMetrics.receivedWallNs - requestSentWallNs : 0n,
        ),
        server_request_deserialize_ns: toNumber(serverMetrics.requestDeserializeNs),
        server_response_serialize_ns: toNumber(serverMetrics.responseSerializeNs),
        response_size_bytes: responseSizeBytes,
        response_network_transit_ns: toNumber(
            responseReceivedWallNs > serverMetrics.sentWallNs ? responseReceivedWallNs - serverMetrics.sentWallNs : 0n,
        ),
        client_response_deserialize_ns: toNumber(responseDeserializeNs),
        round_trip_ns: toNumber(roundTripNs),
    };
}

function telepactMessage(functionName: string, payload: any, packed: boolean): Message {
    const msg = new Message(packed ? { '@pac_': true } : {}, { [functionName]: JSON.parse(JSON.stringify(payload)) });
    return msg;
}

async function startServers(connection: NatsConnection, root: protobuf.Root): Promise<Subscription[]> {
    const subscriptions: Subscription[] = [];
    const telepactSchema = TelepactSchema.fromFileJsonMap({
        'benchmark.telepact.json': fs.readFileSync(path.join(ROOT, 'schema', 'benchmark.telepact.json'), 'utf8'),
    });
    let currentTelepactMeasurement: ServerMeasurement | null = null;

    const telepactOptions = new ServerOptions();
    telepactOptions.authRequired = false;
    telepactOptions.onRequest = (_message: Message) => {
        if (currentTelepactMeasurement) {
            currentTelepactMeasurement.requestDeserializeNs = process.hrtime.bigint() - currentTelepactMeasurement.startPerfNs;
        }
    };
    telepactOptions.onResponse = (_message: Message) => {
        if (currentTelepactMeasurement) {
            currentTelepactMeasurement.serializeStartNs = process.hrtime.bigint();
        }
    };
    const telepactServer = new Server(
        telepactSchema,
        new FunctionRouter({
            'fn.echoTypical': async (_functionName: string, requestMessage: Message) => {
                return new Message({}, { Ok_: JSON.parse(JSON.stringify(requestMessage.getBodyPayload())) });
            },
            'fn.echoAllStrings': async (_functionName: string, requestMessage: Message) => {
                return new Message({}, { Ok_: JSON.parse(JSON.stringify(requestMessage.getBodyPayload())) });
            },
            'fn.echoAllNumbers': async (_functionName: string, requestMessage: Message) => {
                return new Message({}, { Ok_: JSON.parse(JSON.stringify(requestMessage.getBodyPayload())) });
            },
        }),
        telepactOptions,
    );

    const telepactHandler = async (msg: Msg) => {
        const measurement: ServerMeasurement = {
            startPerfNs: process.hrtime.bigint(),
            receivedWallNs: nowWallNs(),
        };
        currentTelepactMeasurement = measurement;
        const response = await telepactServer.process(msg.data);
        const serializeStartNs = measurement.serializeStartNs ?? process.hrtime.bigint();
        measurement.responseSerializeNs = process.hrtime.bigint() - serializeStartNs;
        measurement.sentWallNs = nowWallNs();
        currentTelepactMeasurement = null;
        connection.publish(msg.reply!, response.bytes, { headers: metricHeaders(measurement) });
    };

    const plainJsonHandler = async (msg: Msg) => {
        const measurement: ServerMeasurement = { startPerfNs: process.hrtime.bigint(), receivedWallNs: nowWallNs() };
        const deserializeStartNs = process.hrtime.bigint();
        const parsed = JSON.parse(new TextDecoder().decode(msg.data));
        measurement.requestDeserializeNs = process.hrtime.bigint() - deserializeStartNs;
        const serializeStartNs = process.hrtime.bigint();
        const responseBytes = new TextEncoder().encode(JSON.stringify(parsed));
        measurement.responseSerializeNs = process.hrtime.bigint() - serializeStartNs;
        measurement.sentWallNs = nowWallNs();
        connection.publish(msg.reply!, responseBytes, { headers: metricHeaders(measurement) });
    };

    const protobufHandlers = new Map<string, (msg: Msg) => void>();
    for (const dataShape of Object.keys(CONFIG.dataShapes)) {
        const requestType = root.lookupType(CONFIG.dataShapes[dataShape].protobufRequestType) as protobuf.Type;
        const responseType = root.lookupType(CONFIG.dataShapes[dataShape].protobufResponseType) as protobuf.Type;
        protobufHandlers.set(dataShape, (msg: Msg) => {
            const measurement: ServerMeasurement = { startPerfNs: process.hrtime.bigint(), receivedWallNs: nowWallNs() };
            const deserializeStartNs = process.hrtime.bigint();
            const parsedRequest = requestType.decode(msg.data);
            measurement.requestDeserializeNs = process.hrtime.bigint() - deserializeStartNs;
            const serializeStartNs = process.hrtime.bigint();
            const responseBytes = responseType.encode(responseType.create(responseType.toObject(parsedRequest))).finish();
            measurement.responseSerializeNs = process.hrtime.bigint() - serializeStartNs;
            measurement.sentWallNs = nowWallNs();
            connection.publish(msg.reply!, responseBytes, { headers: metricHeaders(measurement) });
        });
    }

    for (const method of ['telepact_json', 'telepact_binary', 'telepact_packed_binary']) {
        for (const dataShape of Object.keys(CONFIG.dataShapes)) {
            subscriptions.push(connection.subscribe(subjectFor(method, dataShape), { callback: (_err, msg) => void telepactHandler(msg) }));
        }
    }

    for (const dataShape of Object.keys(CONFIG.dataShapes)) {
        subscriptions.push(connection.subscribe(subjectFor('plain_json', dataShape), { callback: (_err, msg) => void plainJsonHandler(msg) }));
        const protobufHandler = protobufHandlers.get(dataShape)!;
        subscriptions.push(connection.subscribe(subjectFor('protobuf', dataShape), { callback: (_err, msg) => void protobufHandler(msg) }));
    }

    await connection.flush();
    return subscriptions;
}

async function runTelepactCase(connection: NatsConnection, method: string, dataShape: string, collectionShape: string): Promise<BenchmarkCase> {
    const payload = PAYLOADS[dataShape][collectionShape];
    const functionName = CONFIG.dataShapes[dataShape].telepactFunction as string;
    const packed = method === 'telepact_packed_binary';
    const useBinary = method !== 'telepact_json';
    const samples: Sample[] = [];

    const clientOptions = new ClientOptions();
    clientOptions.useBinary = useBinary;
    clientOptions.alwaysSendJson = !useBinary ? true : false;

    const client = new Client(async (message: Message, serializer) => {
        const requestStartNs = process.hrtime.bigint();
        const requestBytes = serializer.serialize(message);
        const requestSerializeNs = process.hrtime.bigint() - requestStartNs;
        const requestSentWallNs = nowWallNs();
        const responseMsg = await connection.request(subjectFor(method, dataShape), requestBytes, {
            timeout: CONFIG.requestTimeoutMs,
        });
        const responseReceivedWallNs = nowWallNs();
        const serverMetrics = parseMetricHeaders(responseMsg);
        const responseDeserializeStartNs = process.hrtime.bigint();
        const response = serializer.deserialize(responseMsg.data);
        const responseDeserializeNs = process.hrtime.bigint() - responseDeserializeStartNs;
        samples.push(
            sampleFromTimings(
                requestSerializeNs,
                requestBytes.length,
                requestSentWallNs,
                serverMetrics,
                responseMsg.data.length,
                responseReceivedWallNs,
                responseDeserializeNs,
                process.hrtime.bigint() - requestStartNs,
            ),
        );
        return response;
    }, clientOptions);

    const handshakeIterations = useBinary ? CONFIG.binaryNegotiationWarmupIterations : 0;
    const totalIterations = handshakeIterations + CONFIG.warmupIterations + CONFIG.steadyStateIterations;
    for (let index = 0; index < totalIterations; index += 1) {
        const response = await client.request(telepactMessage(functionName, payload, packed));
        const expected = { Ok_: payload };
        if (JSON.stringify(response.body) !== JSON.stringify(expected)) {
            throw new Error(`Unexpected Telepact response for ${method}/${dataShape}/${collectionShape}`);
        }
    }

    return {
        language: LANGUAGE,
        method,
        data_shape: dataShape,
        collection_shape: collectionShape,
        samples: samples.slice(handshakeIterations + CONFIG.warmupIterations),
    };
}

async function runPlainJsonCase(connection: NatsConnection, dataShape: string, collectionShape: string): Promise<BenchmarkCase> {
    const payload = PAYLOADS[dataShape][collectionShape];
    const samples: Sample[] = [];
    for (let index = 0; index < CONFIG.warmupIterations + CONFIG.steadyStateIterations; index += 1) {
        const requestStartNs = process.hrtime.bigint();
        const requestBytes = new TextEncoder().encode(JSON.stringify(payload));
        const requestSerializeNs = process.hrtime.bigint() - requestStartNs;
        const requestSentWallNs = nowWallNs();
        const responseMsg = await connection.request(subjectFor('plain_json', dataShape), requestBytes, {
            timeout: CONFIG.requestTimeoutMs,
        });
        const responseReceivedWallNs = nowWallNs();
        const serverMetrics = parseMetricHeaders(responseMsg);
        const responseDeserializeStartNs = process.hrtime.bigint();
        const parsedResponse = JSON.parse(new TextDecoder().decode(responseMsg.data));
        const responseDeserializeNs = process.hrtime.bigint() - responseDeserializeStartNs;
        if (JSON.stringify(parsedResponse) !== JSON.stringify(payload)) {
            throw new Error(`Unexpected JSON response for ${dataShape}/${collectionShape}`);
        }
        samples.push(
            sampleFromTimings(
                requestSerializeNs,
                requestBytes.length,
                requestSentWallNs,
                serverMetrics,
                responseMsg.data.length,
                responseReceivedWallNs,
                responseDeserializeNs,
                process.hrtime.bigint() - requestStartNs,
            ),
        );
    }

    return {
        language: LANGUAGE,
        method: 'plain_json',
        data_shape: dataShape,
        collection_shape: collectionShape,
        samples: samples.slice(CONFIG.warmupIterations),
    };
}

async function runProtobufCase(connection: NatsConnection, root: protobuf.Root, dataShape: string, collectionShape: string): Promise<BenchmarkCase> {
    const payload = PAYLOADS[dataShape][collectionShape];
    const requestType = root.lookupType(CONFIG.dataShapes[dataShape].protobufRequestType) as protobuf.Type;
    const responseType = root.lookupType(CONFIG.dataShapes[dataShape].protobufResponseType) as protobuf.Type;
    const requestMessage = requestType.create(payload);
    const expected = JSON.parse(JSON.stringify(payload));
    const samples: Sample[] = [];

    for (let index = 0; index < CONFIG.warmupIterations + CONFIG.steadyStateIterations; index += 1) {
        const requestStartNs = process.hrtime.bigint();
        const requestBytes = requestType.encode(requestMessage).finish();
        const requestSerializeNs = process.hrtime.bigint() - requestStartNs;
        const requestSentWallNs = nowWallNs();
        const responseMsg = await connection.request(subjectFor('protobuf', dataShape), requestBytes, {
            timeout: CONFIG.requestTimeoutMs,
        });
        const responseReceivedWallNs = nowWallNs();
        const serverMetrics = parseMetricHeaders(responseMsg);
        const responseDeserializeStartNs = process.hrtime.bigint();
        const parsedResponse = responseType.decode(responseMsg.data);
        const responseDeserializeNs = process.hrtime.bigint() - responseDeserializeStartNs;
        const responsePayload = responseType.toObject(parsedResponse, { longs: Number });
        if (JSON.stringify(responsePayload) !== JSON.stringify(expected)) {
            throw new Error(`Unexpected protobuf response for ${dataShape}/${collectionShape}`);
        }
        samples.push(
            sampleFromTimings(
                requestSerializeNs,
                requestBytes.length,
                requestSentWallNs,
                serverMetrics,
                responseMsg.data.length,
                responseReceivedWallNs,
                responseDeserializeNs,
                process.hrtime.bigint() - requestStartNs,
            ),
        );
    }

    return {
        language: LANGUAGE,
        method: 'protobuf',
        data_shape: dataShape,
        collection_shape: collectionShape,
        samples: samples.slice(CONFIG.warmupIterations),
    };
}

async function main() {
    const outputIndex = process.argv.indexOf('--output');
    if (outputIndex < 0 || outputIndex === process.argv.length - 1) {
        throw new Error('Expected --output <path>');
    }
    const outputPath = process.argv[outputIndex + 1]!;
    const root = await protobuf.load(path.join(ROOT, 'schema', 'benchmark.proto'));
    const connection = await connect({ servers: NATS_URL });
    await startServers(connection, root);

    const cases: BenchmarkCase[] = [];
    try {
        for (const dataShape of Object.keys(CONFIG.dataShapes)) {
            for (const collectionShape of Object.keys(CONFIG.collectionShapes)) {
                cases.push(await runTelepactCase(connection, 'telepact_json', dataShape, collectionShape));
                cases.push(await runTelepactCase(connection, 'telepact_binary', dataShape, collectionShape));
                cases.push(await runTelepactCase(connection, 'telepact_packed_binary', dataShape, collectionShape));
                cases.push(await runProtobufCase(connection, root, dataShape, collectionShape));
                cases.push(await runPlainJsonCase(connection, dataShape, collectionShape));
            }
        }
    } finally {
        await connection.drain();
    }

    fs.writeFileSync(
        outputPath,
        `${JSON.stringify({ language: LANGUAGE, nats_url: NATS_URL, cases }, null, 2)}\n`,
        'utf8',
    );
}

void main();
