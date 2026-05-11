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

import { AsyncLocalStorage } from 'node:async_hooks';
import fs from 'node:fs';
import path from 'node:path';
import protobuf from 'protobufjs';
import { connect, headers as createHeaders, Msg, NatsConnection, Subscription } from 'nats';
import { Client, ClientOptions, FunctionRouter, Message, Serializer, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

const BENCHMARK_HEADER = 'x-benchmark-id';

type Json = Record<string, any>;
type Sample = Record<string, any>;

function nowNs(): number {
    return Number(process.hrtime.bigint());
}

function uniqueRunId(): string {
    return Math.random().toString(16).slice(2, 14);
}

function loadJson(filePath: string): any {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath: string, payload: any): void {
    fs.writeFileSync(filePath, JSON.stringify(payload, null, 2));
}

function payloadEntry(payload: Json): [string, any] {
    return Object.entries(payload)[0] as [string, any];
}

class ProtobufCodec {
    private requestType: protobuf.Type;
    private responseType: protobuf.Type;

    constructor(protoPath: string) {
        const root = protobuf.loadSync(protoPath);
        this.requestType = root.lookupType('telepact.performance.RoundTripRequest') as protobuf.Type;
        this.responseType = root.lookupType('telepact.performance.RoundTripResponse') as protobuf.Type;
    }

    private payloadToObject(payload: Json): Json {
        const [variant, value] = payloadEntry(payload);
        switch (variant) {
            case 'typicalSingle':
                return { typicalSingle: value };
            case 'typicalList':
                return { typicalList: value };
            case 'stringSingle':
                return { stringSingle: value };
            case 'stringList':
                return { stringList: value };
            case 'numberSingle':
                return { numberSingle: value };
            case 'numberList':
                return { numberList: value };
            default:
                throw new Error(`unknown payload variant: ${variant}`);
        }
    }

    private payloadFromObject(payload: Json): Json {
        if (payload.typicalSingle != null) return { typicalSingle: payload.typicalSingle };
        if (payload.typicalList != null) return { typicalList: payload.typicalList };
        if (payload.stringSingle != null) return { stringSingle: payload.stringSingle };
        if (payload.stringList != null) return { stringList: payload.stringList };
        if (payload.numberSingle != null) return { numberSingle: payload.numberSingle };
        return { numberList: payload.numberList };
    }

    encodeRequest(request: Json): Uint8Array {
        return this.requestType.encode(this.requestType.create({
            payload: this.payloadToObject(request),
        })).finish();
    }

    decodeRequest(payload: Uint8Array): Json {
        const decoded = this.requestType.toObject(this.requestType.decode(payload), { defaults: false });
        return this.payloadFromObject(decoded.payload as Json);
    }

    encodeResponse(response: Json): Uint8Array {
        return this.responseType.encode(this.responseType.create({
            payload: this.payloadToObject(response),
        })).finish();
    }

    decodeResponse(payload: Uint8Array): Json {
        const decoded = this.responseType.toObject(this.responseType.decode(payload), { defaults: false });
        return this.payloadFromObject(decoded.payload as Json);
    }
}

class TelepactBenchClient {
    private client: Client;
    private activeSample: Sample | null = null;

    constructor(
        private connection: NatsConnection,
        private subject: string,
        private packed: boolean,
        private state: Map<string, Sample>,
    ) {
        const options = new ClientOptions();
        options.useBinary = subject.includes('telepact-binary') || subject.includes('telepact-packed');
        options.alwaysSendJson = !options.useBinary;
        this.client = new Client(async (message: Message, serializer: Serializer): Promise<Message> => {
            if (this.activeSample == null) {
                throw new Error('active sample missing');
            }
            const sample = this.activeSample;
            const benchmarkId = uniqueRunId();
            this.state.set(benchmarkId, sample);
            const serializeStart = nowNs();
            const requestBytes = serializer.serialize(message);
            sample.client_request_serialize_ns = nowNs() - serializeStart;
            sample.request_size_bytes = requestBytes.length;
            sample.client_request_sent_ns = nowNs();
            const headers = createHeaders();
            headers.set(BENCHMARK_HEADER, benchmarkId);
            const response = await this.connection.request(this.subject, requestBytes, { timeout: 30_000, headers });
            sample.client_response_received_ns = nowNs();
            sample.response_size_bytes = response.data.length;
            const deserializeStart = nowNs();
            const decoded = serializer.deserialize(response.data);
            sample.client_response_deserialize_ns = nowNs() - deserializeStart;
            sample.request_network_transit_ns = sample.server_request_received_ns - sample.client_request_sent_ns;
            sample.response_network_transit_ns = sample.client_response_received_ns - sample.server_response_sent_ns;
            this.state.delete(benchmarkId);
            return decoded;
        }, options);
    }

    async roundTrip(functionName: string, request: Json, sample: Sample): Promise<void> {
        const headers: Json = {};
        if (this.packed) {
            headers['@pac_'] = true;
        }
        this.activeSample = sample;
        try {
            const response = await this.client.request(new Message(headers, { [functionName]: Object.values(request)[0] }));
            if (JSON.stringify(response.body['Ok_']) !== JSON.stringify(Object.values(request)[0])) {
                throw new Error('telepact response mismatch');
            }
        } finally {
            this.activeSample = null;
        }
    }
}

async function buildTelepactServer(schemaDir: string, state: Map<string, Sample>): Promise<{ server: Server; context: AsyncLocalStorage<string> }> {
    const files = new TelepactSchemaFiles(schemaDir, fs, path);
    const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
    const context = new AsyncLocalStorage<string>();
    const options = new ServerOptions();
    options.authRequired = false;
    options.onRequest = (_message: Message) => {
        const benchmarkId = context.getStore();
        if (benchmarkId == null) {
            return;
        }
        const sample = state.get(benchmarkId);
        if (sample != null) {
            sample.server_request_deserialize_ns = nowNs() - sample.server_request_received_ns;
        }
    };
    options.onResponse = (_message: Message) => {
        const benchmarkId = context.getStore();
        if (benchmarkId == null) {
            return;
        }
        const sample = state.get(benchmarkId);
        if (sample != null) {
            sample.server_response_ready_ns = nowNs();
        }
    };
    const functionNames = [
        'fn.typicalSingle',
        'fn.typicalList',
        'fn.stringSingle',
        'fn.stringList',
        'fn.numberSingle',
        'fn.numberList',
    ];
    const routes = Object.fromEntries(functionNames.map((name) => [name, async (functionName: string, requestMessage: Message): Promise<Message> => {
        return new Message({}, { 'Ok_': requestMessage.body[functionName] });
    }]));
    const server = new Server(schema, new FunctionRouter(routes), options);
    return { server, context };
}

async function runPlainJson(connection: NatsConnection, subject: string, request: Json, sample: Sample, state: Map<string, Sample>): Promise<Json> {
    const benchmarkId = uniqueRunId();
    state.set(benchmarkId, sample);
    const serializeStart = nowNs();
    const requestBytes = new TextEncoder().encode(JSON.stringify(request));
    sample.client_request_serialize_ns = nowNs() - serializeStart;
    sample.request_size_bytes = requestBytes.length;
    sample.client_request_sent_ns = nowNs();
    const headers = createHeaders();
    headers.set(BENCHMARK_HEADER, benchmarkId);
    const response = await connection.request(subject, requestBytes, { timeout: 30_000, headers });
    sample.client_response_received_ns = nowNs();
    sample.response_size_bytes = response.data.length;
    const deserializeStart = nowNs();
    const decoded = JSON.parse(new TextDecoder().decode(response.data));
    sample.client_response_deserialize_ns = nowNs() - deserializeStart;
    sample.request_network_transit_ns = sample.server_request_received_ns - sample.client_request_sent_ns;
    sample.response_network_transit_ns = sample.client_response_received_ns - sample.server_response_sent_ns;
    state.delete(benchmarkId);
    return decoded;
}

async function runProtobuf(connection: NatsConnection, subject: string, request: Json, sample: Sample, state: Map<string, Sample>, codec: ProtobufCodec): Promise<Json> {
    const benchmarkId = uniqueRunId();
    state.set(benchmarkId, sample);
    const serializeStart = nowNs();
    const requestBytes = codec.encodeRequest(request);
    sample.client_request_serialize_ns = nowNs() - serializeStart;
    sample.request_size_bytes = requestBytes.length;
    sample.client_request_sent_ns = nowNs();
    const headers = createHeaders();
    headers.set(BENCHMARK_HEADER, benchmarkId);
    const response = await connection.request(subject, requestBytes, { timeout: 30_000, headers });
    sample.client_response_received_ns = nowNs();
    sample.response_size_bytes = response.data.length;
    const deserializeStart = nowNs();
    const decoded = codec.decodeResponse(response.data);
    sample.client_response_deserialize_ns = nowNs() - deserializeStart;
    sample.request_network_transit_ns = sample.server_request_received_ns - sample.client_request_sent_ns;
    sample.response_network_transit_ns = sample.client_response_received_ns - sample.server_response_sent_ns;
    state.delete(benchmarkId);
    return decoded;
}

async function benchmark(args: Json): Promise<Sample[]> {
    const manifest = loadJson(args.manifest);
    const state = new Map<string, Sample>();
    const connection = await connect({ servers: args.natsUrl });
    const subjectPrefix = `telepact.performance.${args.language}.${args.latency}.${uniqueRunId()}`;
    const telepactJsonSubject = `${subjectPrefix}.telepact-json`;
    const telepactBinarySubject = `${subjectPrefix}.telepact-binary`;
    const telepactPackedSubject = `${subjectPrefix}.telepact-packed`;
    const protobufSubject = `${subjectPrefix}.protobuf`;
    const jsonSubject = `${subjectPrefix}.json`;
    const codec = new ProtobufCodec(args.protoFile);
    const { server, context } = await buildTelepactServer(args.telepactSchemaDir, state);

    const telepactHandler = async (msg: Msg): Promise<void> => {
        const benchmarkId = msg.headers?.get(BENCHMARK_HEADER);
        if (benchmarkId == null) {
            throw new Error('missing benchmark header');
        }
        const sample = state.get(benchmarkId);
        if (sample == null) {
            throw new Error('missing sample for benchmark');
        }
        sample.server_request_received_ns = nowNs();
        const response = await context.run(benchmarkId, async () => await server.process(msg.data));
        sample.server_response_serialize_ns = nowNs() - sample.server_response_ready_ns;
        sample.server_response_sent_ns = nowNs();
        await connection.publish(msg.reply!, response.bytes);
    };

    const protobufHandler = async (msg: Msg): Promise<void> => {
        const benchmarkId = msg.headers?.get(BENCHMARK_HEADER);
        if (benchmarkId == null) {
            throw new Error('missing benchmark header');
        }
        const sample = state.get(benchmarkId)!;
        sample.server_request_received_ns = nowNs();
        const deserializeStart = nowNs();
        const request = codec.decodeRequest(msg.data);
        sample.server_request_deserialize_ns = nowNs() - deserializeStart;
        const serializeStart = nowNs();
        const responseBytes = codec.encodeResponse(request);
        sample.server_response_serialize_ns = nowNs() - serializeStart;
        sample.server_response_sent_ns = nowNs();
        await connection.publish(msg.reply!, responseBytes);
    };

    const jsonHandler = async (msg: Msg): Promise<void> => {
        const benchmarkId = msg.headers?.get(BENCHMARK_HEADER);
        if (benchmarkId == null) {
            throw new Error('missing benchmark header');
        }
        const sample = state.get(benchmarkId)!;
        sample.server_request_received_ns = nowNs();
        const deserializeStart = nowNs();
        const request = JSON.parse(new TextDecoder().decode(msg.data));
        sample.server_request_deserialize_ns = nowNs() - deserializeStart;
        const serializeStart = nowNs();
        const responseBytes = new TextEncoder().encode(JSON.stringify(request));
        sample.server_response_serialize_ns = nowNs() - serializeStart;
        sample.server_response_sent_ns = nowNs();
        await connection.publish(msg.reply!, responseBytes);
    };

    const subscriptions: Subscription[] = [
        connection.subscribe(telepactJsonSubject, { callback: (_err, msg) => { void telepactHandler(msg); } }),
        connection.subscribe(telepactBinarySubject, { callback: (_err, msg) => { void telepactHandler(msg); } }),
        connection.subscribe(telepactPackedSubject, { callback: (_err, msg) => { void telepactHandler(msg); } }),
        connection.subscribe(protobufSubject, { callback: (_err, msg) => { void protobufHandler(msg); } }),
        connection.subscribe(jsonSubject, { callback: (_err, msg) => { void jsonHandler(msg); } }),
    ];
    await connection.flush();

    const telepactJsonClient = new TelepactBenchClient(connection, telepactJsonSubject, false, state);
    const telepactBinaryClient = new TelepactBenchClient(connection, telepactBinarySubject, false, state);
    const telepactPackedClient = new TelepactBenchClient(connection, telepactPackedSubject, true, state);

    const samples: Sample[] = [];
    for (const scenario of manifest.scenarios as Json[]) {
        const functionName = scenario.functionName as string;
        for (let index = 0; index < manifest.warmupIterations; index += 1) {
            await telepactJsonClient.roundTrip(functionName, scenario.request, {} as Sample);
            await telepactBinaryClient.roundTrip(functionName, scenario.request, {} as Sample);
            await telepactPackedClient.roundTrip(functionName, scenario.request, {} as Sample);
            const protoWarmup = await runProtobuf(connection, protobufSubject, scenario.request, {} as Sample, state, codec);
            const jsonWarmup = await runPlainJson(connection, jsonSubject, scenario.request, {} as Sample, state);
            if (JSON.stringify(protoWarmup) !== JSON.stringify(scenario.response) || JSON.stringify(jsonWarmup) !== JSON.stringify(scenario.response)) {
                throw new Error('warmup mismatch');
            }
        }

        for (const method of manifest.methods as string[]) {
            for (let iteration = 0; iteration < manifest.measureIterations; iteration += 1) {
                const sample: Sample = {
                    language: args.language,
                    latency: args.latency,
                    method,
                    scenario: scenario.name,
                    collection_shape: scenario.collectionShape,
                    data_shape: scenario.dataShape,
                    iteration,
                };
                if (method === 'telepact_json') {
                    await telepactJsonClient.roundTrip(functionName, scenario.request, sample);
                } else if (method === 'telepact_binary') {
                    await telepactBinaryClient.roundTrip(functionName, scenario.request, sample);
                } else if (method === 'telepact_packed_binary') {
                    await telepactPackedClient.roundTrip(functionName, scenario.request, sample);
                } else if (method === 'protobuf') {
                    const response = await runProtobuf(connection, protobufSubject, scenario.request, sample, state, codec);
                    if (JSON.stringify(response) !== JSON.stringify(scenario.response)) {
                        throw new Error('protobuf response mismatch');
                    }
                } else {
                    const response = await runPlainJson(connection, jsonSubject, scenario.request, sample, state);
                    if (JSON.stringify(response) !== JSON.stringify(scenario.response)) {
                        throw new Error('json response mismatch');
                    }
                }
                samples.push(sample);
            }
        }
    }

    for (const subscription of subscriptions) {
        subscription.unsubscribe();
    }
    await connection.drain();
    return samples;
}

function parseArgs(argv: string[]): Json {
    const result: Json = {};
    for (let index = 0; index < argv.length; index += 2) {
        const key = argv[index]?.replace(/^--/, '');
        const value = argv[index + 1];
        if (key != null && value != null) {
            result[key.replace(/-([a-z])/g, (_full, char: string) => char.toUpperCase())] = value;
        }
    }
    return result;
}

const args = parseArgs(process.argv.slice(2));
const samples = await benchmark(args);
writeJson(args.output, samples);
