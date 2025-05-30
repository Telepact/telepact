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

import {
    TelepactSchemaParseError,
    Client,
    ClientOptions,
    Server,
    ServerOptions,
    Message,
    SerializationError,
    Serializer,
    MockServer,
    MockServerOptions,
    TelepactSchema,
    MockTelepactSchema,
    TelepactSchemaFiles
} from "telepact";
import { NatsConnection, connect, Subscription } from "nats";
import * as fs from "fs";
import * as path from 'path';
import { min, max, mean, median, quantile } from "simple-statistics";
import { ClientInterface_, test } from "./gen/all_.js";
import { CodeGenHandler } from "./codeGenHandler.js";

class Timer {
    public values: number[] = [];

    public startTimer(): () => void {
        const start = performance.now();
        return () => {
            const end = performance.now();
            this.values.push(end - start);
        };
    }
}

class Registry {
    public timers: Record<string, Timer> = {};

    public createTimer(name: string): Timer {
        const timer = new Timer();
        this.timers[name] = timer;
        return timer;
    }

    public report() {
        for (const [name, timer] of Object.entries(this.timers)) {
            const fileName = `./metrics/${name}.csv`;

            if (!fs.existsSync(fileName)) {
                try {
                    fs.mkdirSync("./metrics");
                } catch (e) {}

                const header = "count,min,max,mean,median,p75,p95,p99\n";
                fs.writeFileSync(fileName, header);
            }

            const v = timer.values;
            const row = `${v.length},${min(v)},${max(v)},${mean(v)},${median(
                v,
            )},${quantile(v, 0.75)},${quantile(v, 0.95)},${quantile(v, 0.99)}\n`;

            fs.appendFileSync(fileName, row);
        }
    }
}

function uint8ArrayToBase64Replacer(key: string, value: object) {
    if (value instanceof Uint8Array) {
      return btoa(String.fromCharCode(...value));
    }
    return value;
  }

function startClientTestServer(
    connection: NatsConnection,
    registry: Registry,
    clientFrontdoorTopic: string,
    clientBackdoorTopic: string,
    defaultBinary: boolean,
    useCodegen: boolean
): Subscription {
    const timer = registry.createTimer(clientBackdoorTopic);

    const adapter: (m: Message, s: Serializer) => Promise<Message> = async (m, s) => {
        try {
            let requestBytes: Uint8Array;
            try {
                requestBytes = s.serialize(m);
            } catch (e) {
                if (e instanceof SerializationError) {
                    return new Message({ numberTooBig: true }, { ErrorUnknown_: {} });
                } else {
                    throw e;
                }
            }

            console.log(`   <-c  ${new TextDecoder().decode(requestBytes)}`);
            const natsResponseMessage = await connection.request(clientBackdoorTopic, requestBytes, { timeout: 5000 });
            const responseBytes = natsResponseMessage.data;

            console.log(`   ->c  ${new TextDecoder().decode(responseBytes)}`);

            const responseMessage = s.deserialize(responseBytes);
            return responseMessage;
        } catch (e) {
            console.error(e);
            throw e;
        }
    };

    const options = new ClientOptions();

    options.useBinary = defaultBinary;
    options.alwaysSendJson = !defaultBinary;
    const client = new Client(adapter, options);

    const genClient = new ClientInterface_(client); 

    const sub: Subscription = connection.subscribe(clientFrontdoorTopic);

    (async () => {
        for await (const msg of sub) {
            const requestBytes = msg.data;
            const requestJson = new TextDecoder().decode(requestBytes);

            console.log(`   ->C  ${requestJson}`);

            const requestPseudoJson = JSON.parse(requestJson);
            const requestHeaders = requestPseudoJson[0] as Record<string, any>;
            const requestBody = requestPseudoJson[1] as Record<string, any>;
            const request = new Message(requestHeaders, requestBody);

            const [functionName, argument] = Object.entries(requestBody)[0] as [string, any];

            let response: Message;
            const time = timer.startTimer();
            try {
                if (useCodegen && functionName === "fn.test") {
                    const [responseHeaders, outputBody] = await genClient.test(requestHeaders, new test.Input(requestBody));
                    responseHeaders["@codegenc_"] = true;
                    response = new Message(responseHeaders, outputBody.pseudoJson);
                } else {
                    response = await client.request(request);
                }
            } finally {
                time();
            }

            const responsePseudoJson = [response.headers, response.body];

            const responseJson = JSON.stringify(responsePseudoJson, uint8ArrayToBase64Replacer);

            const responseBytes = new TextEncoder().encode(responseJson);

            console.log(`   <-C  ${new TextDecoder().decode(responseBytes)}`);

            msg.respond(responseBytes);
        }
    })();

    return sub;
}

function startMockTestServer(
    connection: NatsConnection,
    registry: Registry,
    apiSchemaPath: string,
    frontdoorTopic: string,
    config: Record<string, any>,
): Subscription {
    const telepact = MockTelepactSchema.fromDirectory(apiSchemaPath, fs, path);

    const options: MockServerOptions = new MockServerOptions();
    options.onError = (e: Error) => console.error(e);
    options.enableMessageResponseGeneration = false;

    if (config) {
        options.generatedCollectionLengthMin = config.minLength;
        options.generatedCollectionLengthMax = config.maxLength;
        options.enableMessageResponseGeneration = config.enableGen;
    }

    const timer = registry.createTimer(frontdoorTopic);

    const server: MockServer = new MockServer(telepact, options); // Assuming MockServer constructor requires telepact and options

    const subscription: Subscription = connection.subscribe(frontdoorTopic);
    (async () => {
        for await (const msg of subscription) {
            const requestBytes = msg.data;

            console.log(`    ->S ${new TextDecoder().decode(requestBytes)}`);

            let responseBytes: Uint8Array;
            const time = timer.startTimer();
            try {
                responseBytes = await server.process(requestBytes);
            } finally {
                time();
            }

            console.log(`    <-S ${new TextDecoder().decode(responseBytes)}`);

            msg.respond(responseBytes);
        }
    })();

    return subscription;
}

function startSchemaTestServer(
    connection: NatsConnection,
    registry: Registry,
    apiSchemaPath: string,
    frontdoorTopic: string,
    config?: Record<string, any>,
): Subscription {
    const telepact: TelepactSchema = TelepactSchema.fromDirectory(apiSchemaPath, fs, path);

    const timer = registry.createTimer(frontdoorTopic);

    const handler = async (requestMessage: Message): Promise<Message> => {
        const requestBody = requestMessage.body;

        const arg: { [key: string]: any } = requestBody["fn.validateSchema"];

        const input: { [key: string]: any } = arg["input"];
        const inputTag = Object.keys(input)[0];

        try {
            if (inputTag === "PseudoJson") {
                const unionValue: { [key: string]: any } = input[inputTag];
                const schemaJson = unionValue["schema"];
                const extendJson = unionValue["extend!"];

                if (extendJson != null) {
                    TelepactSchema.fromFileJsonMap({'default': schemaJson, 'extend': extendJson});
                } else {
                    TelepactSchema.fromJson(schemaJson);
                }
            } else if (inputTag === "Json") {
                const unionValue = input[inputTag];
                const schemaJson = unionValue["schema"];
                TelepactSchema.fromJson(schemaJson);
            } else if (inputTag === "Directory") {
                const unionValue = input[inputTag];
                const schemaDirectory = unionValue["schemaDirectory"];
                TelepactSchema.fromDirectory(schemaDirectory, fs, path);
            } else {
                throw new Error("Invalid input tag");
            }
        } catch (e) {
            console.error(e);
            return new Message(
                {},
                {
                    ErrorValidationFailure: {
                        cases: (e as TelepactSchemaParseError).schemaParseFailuresPseudoJson,
                    },
                },
            );
        }

        return new Message({}, { Ok_: {} });
    };

    const options: ServerOptions = new ServerOptions();
    options.onError = (e: Error) => console.error(e);
    options.authRequired = false;

    const server: Server = new Server(telepact, handler, options);

    const sub: Subscription = connection.subscribe(frontdoorTopic);
    (async () => {
        for await (const msg of sub) {
            const requestBytes = msg.data;

            console.log(`    ->S ${new TextDecoder().decode(requestBytes)}`);

            let responseBytes: Uint8Array;
            const time = timer.startTimer();
            try {
                responseBytes = await server.process(requestBytes);
            } finally {
                time();
            }

            console.log(`    <-S ${new TextDecoder().decode(responseBytes)}`);

            msg.respond(responseBytes);
        }
    })();

    return sub;
}

function startTestServer(
    connection: NatsConnection,
    registry: Registry,
    apiSchemaPath: string,
    frontdoorTopic: string,
    backdoorTopic: string,
    authRequired: boolean,
    useCodegen: boolean
): Subscription {
    const files = new TelepactSchemaFiles(apiSchemaPath, fs, path);
    const alternateMap: Record<string, string> = { ...files.filenamesToJson };
    alternateMap['backwardsCompatibleChange'] = `
        [
            {
                "struct.BackwardsCompatibleChange": {}
            }
        ]
    `;

    const telepact: TelepactSchema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
    const alternateTelepact: TelepactSchema = TelepactSchema.fromFileJsonMap(alternateMap);

    const timer = registry.createTimer(frontdoorTopic);
    const serveAlternateServer = { value: false };

    const codeGenHandler = new CodeGenHandler();

    class ThisError extends Error {}

    const handler = async (requestMessage: Message): Promise<Message> => {
        const requestHeaders = requestMessage.headers;
        const requestBody = requestMessage.body;
        const requestPseudoJson = [requestHeaders, requestBody];
        const requestJson = JSON.stringify(requestPseudoJson, uint8ArrayToBase64Replacer);
        const requestBytes = new TextEncoder().encode(requestJson);

        let message: Message;
        if (useCodegen) {
            console.log(`     :H ${new TextDecoder().decode(requestBytes)}`);
            message = await codeGenHandler.handler(requestMessage);
            message.headers["@codegens_"] = true;
        } else {
            console.log(`    <-s ${new TextDecoder().decode(requestBytes)}`);
            const natsResponseMessage = await connection.request(backdoorTopic, requestBytes, { timeout: 5000 });

            console.log(`    ->s ${new TextDecoder().decode(natsResponseMessage.data)}`);

            const responseJson = new TextDecoder().decode(natsResponseMessage.data);
            const responsePseudoJson = JSON.parse(responseJson);
            const responseHeaders = responsePseudoJson[0] as { [key: string]: any };
            const responseBody = responsePseudoJson[1] as { [key: string]: any };

            message = new Message(responseHeaders, responseBody);
        }

        if (requestHeaders["@toggleAlternateServer_"] === true) {
            serveAlternateServer.value = !serveAlternateServer.value;
        }

        if (requestHeaders["@throwError_"] === true) {
            throw new ThisError();
        }

        return message;
    };

    const options: ServerOptions = new ServerOptions();
    options.onError = (e: Error) => {
        console.error(e);
        if (e instanceof ThisError) {
            throw new Error();
        }
    };
    options.onRequest = (m: Message) => {
        if (m.headers["@onRequestError_"] === true) {
            throw new Error();
        }
    };
    options.onResponse = (m: Message) => {
        if (m.headers["@onResponseError_"] === true) {
            throw new Error();
        }
    };
    options.authRequired = authRequired;

    const server: Server = new Server(telepact, handler, options);

    const alternateOptions = new ServerOptions();
    alternateOptions.onError = (e) => console.error(e);
    alternateOptions.authRequired = authRequired;
    const alternateServer: Server = new Server(alternateTelepact, handler, alternateOptions);

    const subscription: Subscription = connection.subscribe(frontdoorTopic);
    (async () => {
        for await (const msg of subscription) {
            const requestBytes = msg.data;

            console.log(`    ->S ${new TextDecoder().decode(requestBytes)}`);
            let responseBytes: Uint8Array;
            const time = timer.startTimer();
            try {
                if (serveAlternateServer.value) {
                    responseBytes = await alternateServer.process(requestBytes);
                } else {
                    responseBytes = await server.process(requestBytes);
                }
            } finally {
                time();
            }

            console.log(`    <-S ${new TextDecoder().decode(responseBytes)}`);

            msg.respond(responseBytes);
        }
    })();

    console.log(`Test server listening on ${frontdoorTopic}`);

    return subscription;
}

async function runDispatcherServer(): Promise<void> {
    const natsUrl = process.env.NATS_URL;
    if (!natsUrl) {
        throw new Error("NATS_URL env var not set");
    }

    const registry = new Registry();

    const servers: Record<string, Subscription> = {};

    const connection = await connect({ servers: natsUrl });

    let finish: (value: void | PromiseLike<void>) => void;
    const done = new Promise<void>((resolve) => {
        finish = resolve;
    });

    const subscription = connection.subscribe("ts");

    (async () => {
        for await (const msg of subscription) {
            const requestBytes = msg.data;
            const requestJson = new TextDecoder().decode(requestBytes);

            console.log(`    ->S ${requestJson}`);

            let responseBytes: Uint8Array;
            try {
                const request = JSON.parse(requestJson);
                const body = request[1]!;
                const entry = Object.entries(body)[0]!;
                const target = entry[0];
                const payload: Record<string, any> = entry[1]!;

                switch (target) {
                    case "Ping": {
                        break;
                    }
                    case "End": {
                        finish!();
                        break;
                    }
                    case "Stop": {
                        const id = payload["id"] as string;
                        const s = servers[id];
                        if (s != null) {
                            s.drain();
                        }
                        break;
                    }
                    case "StartServer": {
                        const id = payload["id"] as string;
                        const apiSchemaPath = payload["apiSchemaPath"] as string;
                        const frontdoorTopic = payload["frontdoorTopic"] as string;
                        const backdoorTopic = payload["backdoorTopic"] as string;
                        const authRequired: boolean = payload["authRequired!"] ?? false;
                        const useCodegen: boolean = payload["useCodeGen"] ?? false;

                        const d = startTestServer(
                            connection,
                            registry,
                            apiSchemaPath,
                            frontdoorTopic,
                            backdoorTopic,
                            authRequired,
                            useCodegen
                        );

                        servers[id] = d;
                        break;
                    }
                    case "StartClientServer": {
                        const id = payload["id"] as string;
                        const clientFrontdoorTopic = payload["clientFrontdoorTopic"] as string;
                        const clientBackdoorTopic = payload["clientBackdoorTopic"] as string;
                        const useBinary = (payload["useBinary"] as boolean) ?? false;
                        const useCodegen = (payload["useCodeGen"] as boolean) ?? false;

                        const d = startClientTestServer(
                            connection,
                            registry,
                            clientFrontdoorTopic,
                            clientBackdoorTopic,
                            useBinary,
                            useCodegen
                        );

                        servers[id] = d;
                        break;
                    }
                    case "StartMockServer": {
                        const id = payload["id"] as string;
                        const apiSchemaPath = payload["apiSchemaPath"] as string;
                        const frontdoorTopic = payload["frontdoorTopic"] as string;
                        const config = payload["config"] as Map<string, unknown>;
                        const d = startMockTestServer(connection, registry, apiSchemaPath, frontdoorTopic, config);

                        servers[id] = d;
                        break;
                    }
                    case "StartSchemaServer": {
                        const id = payload["id"] as string;
                        const apiSchemaPath = payload["apiSchemaPath"] as string;
                        const frontdoorTopic = payload["frontdoorTopic"] as string;
                        const d = startSchemaTestServer(connection, registry, apiSchemaPath, frontdoorTopic);

                        servers[id] = d;
                        break;
                    }
                    default: {
                        throw new Error("no matching server");
                    }
                }

                const responseJson = JSON.stringify([new Map(), new Map([["Ok_", new Map()]])]);
                responseBytes = new TextEncoder().encode(responseJson);
            } catch (e) {
                console.error(e);
                try {
                    const responseJson = JSON.stringify([new Map(), new Map([["ErrorUnknown", new Map()]])]);
                    responseBytes = new TextEncoder().encode(responseJson);
                } catch (e1) {
                    throw new Error();
                }
            }

            console.log(`    <-S ${new TextDecoder().decode(responseBytes)}`);

            msg.respond(responseBytes);
        }
    })();

    await done;

    registry.report();

    console.log("Dispatcher exiting");
}

export default async function main() {
    await runDispatcherServer();
}
