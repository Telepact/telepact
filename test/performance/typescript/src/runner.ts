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

import fs from "fs";
import path from "path";
import protobuf from "protobufjs";
import { connect, Msg, NatsConnection, Subscription } from "nats";
import {
    Client,
    ClientOptions,
    FunctionRouter,
    Message,
    Server,
    ServerOptions,
    TelepactSchema,
} from "telepact";

type PayloadItem = {
    kind: "typical" | "all_strings" | "all_numbers";
    data: Record<string, string | number>;
};

type Payload = {
    items: PayloadItem[];
};

type Sample = {
    request_serialization_ms: number;
    request_size_bytes: number;
    request_network_transit_ms: number;
    server_request_deserialization_ms: number;
    server_response_serialization_ms: number;
    response_size_bytes: number;
    response_network_transit_ms: number;
    response_deserialization_ms: number;
};

type Args = {
    method: string;
    collectionShape: string;
    dataShape: string;
    natsUrl: string;
    subject: string;
    iterations: number;
    warmup: number;
    payloads: string;
    schemaDir: string;
};

function nowMs(): number {
    return Number(process.hrtime.bigint()) / 1_000_000;
}

class PlainJsonCodec {
    static encode(payload: Payload): Uint8Array {
        return new TextEncoder().encode(JSON.stringify(payload));
    }

    static decode(bytes: Uint8Array): Payload {
        return JSON.parse(new TextDecoder().decode(bytes)) as Payload;
    }
}

class ProtobufCodec {
    private readonly requestType: protobuf.Type;
    private readonly responseType: protobuf.Type;

    constructor(schemaDir: string) {
        const root = protobuf.loadSync(path.join(schemaDir, "protobuf", "benchmark.proto"));
        this.requestType = root.lookupType("telepact.performance.EchoRequest") as protobuf.Type;
        this.responseType = root.lookupType("telepact.performance.EchoResponse") as protobuf.Type;
    }

    encodeRequest(payload: Payload): Uint8Array {
        return this.requestType.encode(this.requestType.fromObject(this.toProtobufPayload(payload))).finish();
    }

    decodeRequest(bytes: Uint8Array): Payload {
        return this.fromProtobufPayload(this.requestType.toObject(this.requestType.decode(bytes), { longs: Number }));
    }

    encodeResponse(payload: Payload): Uint8Array {
        return this.responseType.encode(this.responseType.fromObject(this.toProtobufPayload(payload))).finish();
    }

    decodeResponse(bytes: Uint8Array): Payload {
        return this.fromProtobufPayload(this.responseType.toObject(this.responseType.decode(bytes), { longs: Number }));
    }

    private toProtobufPayload(payload: Payload): object {
        return {
            items: payload.items.map((item) => {
                if (item.kind === "typical") {
                    return { typical: item.data };
                }
                if (item.kind === "all_strings") {
                    return { all_strings: item.data };
                }
                return { all_numbers: item.data };
            }),
        };
    }

    private fromProtobufPayload(payload: any): Payload {
        return {
            items: (payload.items ?? []).map((item: any) => {
                if (item.typical != null) {
                    return { kind: "typical", data: item.typical };
                }
                if (item.all_strings != null) {
                    return { kind: "all_strings", data: item.all_strings };
                }
                return { kind: "all_numbers", data: item.all_numbers };
            }),
        };
    }
}

function canonicalToTelepactPayload(payload: Payload): Record<string, unknown> {
    const tagMap: Record<PayloadItem["kind"], string> = {
        typical: "Typical",
        all_strings: "AllStrings",
        all_numbers: "AllNumbers",
    };
    return {
        items: payload.items.map((item) => ({
            [tagMap[item.kind]]: structuredClone(item.data),
        })),
    };
}

class BenchmarkRunner {
    private readonly args: Args;
    private readonly payload: Payload;
    private readonly telepactPayload: Record<string, unknown>;
    private readonly protobuf: ProtobufCodec;
    private readonly telepactSchema: TelepactSchema;
    private telepactClient: Client | null = null;
    private connection!: NatsConnection;
    private subscription!: Subscription;
    private currentSample: Sample | null = null;
    private currentSendMs = 0;
    private serverReplySentMs = 0;
    private serverRequestHookMs = 0;
    private serverResponseHookMs = 0;
    private lastRequestWasBinary = false;
    private lastResponseWasBinary = false;

    constructor(args: Args) {
        this.args = args;
        const scenarios = JSON.parse(fs.readFileSync(args.payloads, "utf-8"));
        this.payload = scenarios[args.collectionShape][args.dataShape] as Payload;
        this.telepactPayload = canonicalToTelepactPayload(this.payload);
        this.protobuf = new ProtobufCodec(args.schemaDir);
        this.telepactSchema = TelepactSchema.fromDirectory(path.join(args.schemaDir, "telepact"), fs, path);
    }

    async setup(): Promise<void> {
        this.connection = await connect({ servers: this.args.natsUrl });
        await this.startServer();
        if (this.args.method.startsWith("telepact")) {
            this.startTelepactClient();
        }
    }

    async teardown(): Promise<void> {
        await this.subscription.unsubscribe();
        await this.connection.close();
    }

    async run(): Promise<Record<string, unknown>> {
        let warmup = this.args.warmup;
        if (this.args.method === "telepact-binary" || this.args.method === "telepact-packed-binary") {
            warmup = Math.max(warmup, 1);
        }

        let steadyState = this.args.method === "telepact-json" || this.args.method === "protobuf" || this.args.method === "plain-json";
        for (let i = 0; i < warmup; i += 1) {
            const [, isSteady] = await this.runOnce(false);
            steadyState = steadyState || isSteady;
        }
        while (!steadyState) {
            const [, isSteady] = await this.runOnce(false);
            steadyState = isSteady;
        }

        const samples: Sample[] = [];
        for (let i = 0; i < this.args.iterations; i += 1) {
            const [sample] = await this.runOnce(true);
            samples.push(sample);
        }

        return {
            language: "typescript",
            method: this.args.method,
            collection_shape: this.args.collectionShape,
            data_shape: this.args.dataShape,
            network_latency: this.args.natsUrl.includes("127.0.0.1") ? "close" : "far",
            warmup_iterations: warmup,
            measured_iterations: this.args.iterations,
            samples,
        };
    }

    private async startServer(): Promise<void> {
        if (this.args.method.startsWith("telepact")) {
            const options = new ServerOptions();
            options.authRequired = false;
            options.onRequest = () => {
                this.serverRequestHookMs = nowMs();
            };
            options.onResponse = () => {
                this.serverResponseHookMs = nowMs();
            };
            const server = new Server(
                this.telepactSchema,
                new FunctionRouter({
                    "fn.echo": async () => new Message({}, { Ok_: structuredClone(this.telepactPayload) }),
                }),
                options,
            );
            this.subscription = this.connection.subscribe(this.args.subject, {
                callback: async (_error: Error | null, msg: Msg) => {
                    const serverReceivedMs = nowMs();
                    const response = await server.process(msg.data);
                    const responseReadyMs = nowMs();
                    if (this.currentSample == null) {
                        throw new Error("missing sample");
                    }
                    this.currentSample.request_network_transit_ms = serverReceivedMs - this.currentSendMs;
                    this.currentSample.server_request_deserialization_ms = this.serverRequestHookMs - serverReceivedMs;
                    this.currentSample.server_response_serialization_ms = responseReadyMs - this.serverResponseHookMs;
                    this.currentSample.response_size_bytes = response.bytes.length;
                    this.lastResponseWasBinary = response.bytes[0] === 0x92;
                    this.serverReplySentMs = nowMs();
                    this.connection.publish(msg.reply!, response.bytes);
                },
            });
        } else if (this.args.method === "protobuf") {
            this.subscription = this.connection.subscribe(this.args.subject, {
                callback: (_error: Error | null, msg: Msg) => {
                    const serverReceivedMs = nowMs();
                    const decodeStartMs = nowMs();
                    const payload = this.protobuf.decodeRequest(msg.data);
                    const decodeEndMs = nowMs();
                    const encodeStartMs = nowMs();
                    const responseBytes = this.protobuf.encodeResponse(payload);
                    const encodeEndMs = nowMs();
                    if (this.currentSample == null) {
                        throw new Error("missing sample");
                    }
                    this.currentSample.request_network_transit_ms = serverReceivedMs - this.currentSendMs;
                    this.currentSample.server_request_deserialization_ms = decodeEndMs - decodeStartMs;
                    this.currentSample.server_response_serialization_ms = encodeEndMs - encodeStartMs;
                    this.currentSample.response_size_bytes = responseBytes.length;
                    this.serverReplySentMs = nowMs();
                    this.connection.publish(msg.reply!, responseBytes);
                },
            });
        } else {
            this.subscription = this.connection.subscribe(this.args.subject, {
                callback: (_error: Error | null, msg: Msg) => {
                    const serverReceivedMs = nowMs();
                    const decodeStartMs = nowMs();
                    const payload = PlainJsonCodec.decode(msg.data);
                    const decodeEndMs = nowMs();
                    const encodeStartMs = nowMs();
                    const responseBytes = PlainJsonCodec.encode(payload);
                    const encodeEndMs = nowMs();
                    if (this.currentSample == null) {
                        throw new Error("missing sample");
                    }
                    this.currentSample.request_network_transit_ms = serverReceivedMs - this.currentSendMs;
                    this.currentSample.server_request_deserialization_ms = decodeEndMs - decodeStartMs;
                    this.currentSample.server_response_serialization_ms = encodeEndMs - encodeStartMs;
                    this.currentSample.response_size_bytes = responseBytes.length;
                    this.serverReplySentMs = nowMs();
                    this.connection.publish(msg.reply!, responseBytes);
                },
            });
        }
        await this.connection.flush();
    }

    private startTelepactClient(): void {
        const adapter = async (message: Message, serializer: any): Promise<Message> => {
            if (this.currentSample == null) {
                throw new Error("missing sample");
            }
            const serializeStartMs = nowMs();
            const requestBytes: Uint8Array = serializer.serialize(message);
            const serializeEndMs = nowMs();
            this.currentSample.request_serialization_ms = serializeEndMs - serializeStartMs;
            this.currentSample.request_size_bytes = requestBytes.length;
            this.lastRequestWasBinary = requestBytes[0] === 0x92;
            this.currentSendMs = nowMs();
            const responseMessage = await this.connection.request(this.args.subject, requestBytes, { timeout: 10000 });
            const responseReceivedMs = nowMs();
            this.currentSample.response_network_transit_ms = responseReceivedMs - this.serverReplySentMs;
            const deserializeStartMs = nowMs();
            const decoded = serializer.deserialize(responseMessage.data);
            const deserializeEndMs = nowMs();
            this.currentSample.response_deserialization_ms = deserializeEndMs - deserializeStartMs;
            return decoded;
        };

        const options = new ClientOptions();
        options.useBinary = this.args.method !== "telepact-json";
        options.alwaysSendJson = this.args.method === "telepact-json";
        this.telepactClient = new Client(adapter, options);
    }

    private async runOnce(record: boolean): Promise<[Sample, boolean]> {
        let sample: Sample;
        let steadyState = true;
        if (this.args.method.startsWith("telepact")) {
            [sample, steadyState] = await this.runTelepactOnce();
        } else if (this.args.method === "protobuf") {
            sample = await this.runProtobufOnce();
        } else {
            sample = await this.runPlainJsonOnce();
        }
        return [sample, steadyState];
    }

    private async runTelepactOnce(): Promise<[Sample, boolean]> {
        if (this.telepactClient == null) {
            throw new Error("telepact client not initialized");
        }
        const sample: Sample = {
            request_serialization_ms: 0,
            request_size_bytes: 0,
            request_network_transit_ms: 0,
            server_request_deserialization_ms: 0,
            server_response_serialization_ms: 0,
            response_size_bytes: 0,
            response_network_transit_ms: 0,
            response_deserialization_ms: 0,
        };
        this.currentSample = sample;
        const headers: Record<string, unknown> = {};
        if (this.args.method === "telepact-packed-binary") {
            headers["@pac_"] = true;
        }
        await this.telepactClient.request(new Message(headers, { "fn.echo": structuredClone(this.telepactPayload) }));
        return [sample, this.args.method === "telepact-json" || (this.lastRequestWasBinary && this.lastResponseWasBinary)];
    }

    private async runProtobufOnce(): Promise<Sample> {
        const sample: Sample = {
            request_serialization_ms: 0,
            request_size_bytes: 0,
            request_network_transit_ms: 0,
            server_request_deserialization_ms: 0,
            server_response_serialization_ms: 0,
            response_size_bytes: 0,
            response_network_transit_ms: 0,
            response_deserialization_ms: 0,
        };
        this.currentSample = sample;
        const serializeStartMs = nowMs();
        const requestBytes = this.protobuf.encodeRequest(this.payload);
        const serializeEndMs = nowMs();
        sample.request_serialization_ms = serializeEndMs - serializeStartMs;
        sample.request_size_bytes = requestBytes.length;
        this.currentSendMs = nowMs();
        const responseMessage = await this.connection.request(this.args.subject, requestBytes, { timeout: 10000 });
        const responseReceivedMs = nowMs();
        sample.response_network_transit_ms = responseReceivedMs - this.serverReplySentMs;
        const deserializeStartMs = nowMs();
        this.protobuf.decodeResponse(responseMessage.data);
        const deserializeEndMs = nowMs();
        sample.response_deserialization_ms = deserializeEndMs - deserializeStartMs;
        return sample;
    }

    private async runPlainJsonOnce(): Promise<Sample> {
        const sample: Sample = {
            request_serialization_ms: 0,
            request_size_bytes: 0,
            request_network_transit_ms: 0,
            server_request_deserialization_ms: 0,
            server_response_serialization_ms: 0,
            response_size_bytes: 0,
            response_network_transit_ms: 0,
            response_deserialization_ms: 0,
        };
        this.currentSample = sample;
        const serializeStartMs = nowMs();
        const requestBytes = PlainJsonCodec.encode(this.payload);
        const serializeEndMs = nowMs();
        sample.request_serialization_ms = serializeEndMs - serializeStartMs;
        sample.request_size_bytes = requestBytes.length;
        this.currentSendMs = nowMs();
        const responseMessage = await this.connection.request(this.args.subject, requestBytes, { timeout: 10000 });
        const responseReceivedMs = nowMs();
        sample.response_network_transit_ms = responseReceivedMs - this.serverReplySentMs;
        const deserializeStartMs = nowMs();
        PlainJsonCodec.decode(responseMessage.data);
        const deserializeEndMs = nowMs();
        sample.response_deserialization_ms = deserializeEndMs - deserializeStartMs;
        return sample;
    }
}

function parseArgs(): Args {
    const args = process.argv.slice(2);
    const valueFor = (name: string): string => {
        const index = args.indexOf(name);
        if (index === -1 || index + 1 >= args.length) {
            throw new Error(`missing ${name}`);
        }
        return args[index + 1]!;
    };
    return {
        method: valueFor("--method"),
        collectionShape: valueFor("--collection-shape"),
        dataShape: valueFor("--data-shape"),
        natsUrl: valueFor("--nats-url"),
        subject: valueFor("--subject"),
        iterations: Number.parseInt(valueFor("--iterations"), 10),
        warmup: Number.parseInt(valueFor("--warmup"), 10),
        payloads: valueFor("--payloads"),
        schemaDir: valueFor("--schema-dir"),
    };
}

async function main(): Promise<void> {
    const runner = new BenchmarkRunner(parseArgs());
    await runner.setup();
    try {
        console.log(JSON.stringify(await runner.run()));
    } finally {
        await runner.teardown();
    }
}

await main();
