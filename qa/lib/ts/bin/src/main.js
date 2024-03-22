import { Client, ClientOptions, Server, ServerOptions, Message, SerializationError, MockServer, MockServerOptions, UApiSchema, } from "uapi";
import { connect } from "nats";
import fs from "fs";
import { min, max, mean, median, quantile } from "simple-statistics";
class Timer {
    values = [];
    startTimer() {
        const start = performance.now();
        return () => {
            const end = performance.now();
            this.values.push(end - start);
        };
    }
}
class Registry {
    timers = {};
    createTimer(name) {
        const timer = new Timer();
        this.timers[name] = timer;
        return timer;
    }
    report() {
        for (const [name, timer] of Object.entries(this.timers)) {
            const fileName = `./metrics/${name}.csv`;
            if (!fs.existsSync(fileName)) {
                try {
                    fs.mkdirSync("./metrics");
                }
                catch (e) { }
                const header = "count,min,max,mean,median,p75,p95,p99\n";
                fs.writeFileSync(fileName, header);
            }
            const v = timer.values;
            const row = `${v.length},${min(v)},${max(v)},${mean(v)},${median(v)},${quantile(v, 0.75)},${quantile(v, 0.95)},${quantile(v, 0.99)}\n`;
            fs.appendFileSync(fileName, row);
        }
    }
}
function startClientTestServer(connection, registry, clientFrontdoorTopic, clientBackdoorTopic, defaultBinary) {
    const timer = registry.createTimer(clientBackdoorTopic);
    const adapter = async (m, s) => {
        try {
            let requestBytes;
            try {
                requestBytes = s.serialize(m);
            }
            catch (e) {
                if (e instanceof SerializationError) {
                    return new Message({ numberTooBig: true }, { _ErrorUnknown: {} });
                }
                else {
                    throw e;
                }
            }
            console.log(`   <-c  ${new TextDecoder().decode(requestBytes)}`);
            const natsResponseMessage = await connection.request(clientBackdoorTopic, requestBytes, { timeout: 5000 });
            const responseBytes = natsResponseMessage.data;
            console.log(`   ->c  ${new TextDecoder().decode(responseBytes)}`);
            const responseMessage = s.deserialize(responseBytes);
            return responseMessage;
        }
        catch (e) {
            console.error(e);
            throw e;
        }
    };
    const options = new ClientOptions();
    options.useBinary = defaultBinary;
    const client = new Client(adapter, options);
    const sub = connection.subscribe(clientFrontdoorTopic);
    (async () => {
        for await (const msg of sub) {
            const requestBytes = msg.data;
            const requestJson = new TextDecoder().decode(requestBytes);
            console.log(`   ->C  ${requestJson}`);
            const requestPseudoJson = JSON.parse(requestJson);
            const requestHeaders = requestPseudoJson[0];
            const requestBody = requestPseudoJson[1];
            const request = new Message(requestHeaders, requestBody);
            let response;
            const time = timer.startTimer();
            try {
                response = await client.request(request);
            }
            finally {
                time();
            }
            const responsePseudoJson = [response.header, response.body];
            const responseJson = JSON.stringify(responsePseudoJson);
            const responseBytes = new TextEncoder().encode(responseJson);
            console.log(`   <-C  ${new TextDecoder().decode(responseBytes)}`);
            msg.respond(responseBytes);
        }
    })();
    return sub;
}
function startMockTestServer(connection, registry, apiSchemaPath, frontdoorTopic, config) {
    const json = fs.readFileSync(apiSchemaPath, "utf-8");
    const uApi = UApiSchema.fromJson(json);
    const options = new MockServerOptions();
    options.onError = (e) => console.error(e);
    options.enableMessageResponseGeneration = false;
    if (config) {
        options.generatedCollectionLengthMin = config.minLength;
        options.generatedCollectionLengthMax = config.maxLength;
        options.enableMessageResponseGeneration = config.enableGen;
    }
    const timer = registry.createTimer(frontdoorTopic);
    const server = new MockServer(uApi, options); // Assuming MockServer constructor requires uApi and options
    const subscription = connection.subscribe(frontdoorTopic);
    (async () => {
        for await (const msg of subscription) {
            const requestBytes = msg.data;
            console.log(`    ->S ${new TextDecoder().decode(requestBytes)}`);
            let responseBytes;
            const time = timer.startTimer();
            try {
                responseBytes = await server.process(requestBytes);
            }
            finally {
                time();
            }
            console.log(`    <-S ${new TextDecoder().decode(responseBytes)}`);
            msg.respond(responseBytes);
        }
    })();
    return subscription;
}
function startSchemaTestServer(connection, registry, apiSchemaPath, frontdoorTopic, config) {
    const json = fs.readFileSync(apiSchemaPath, "utf-8");
    const uApi = UApiSchema.fromJson(json);
    const timer = registry.createTimer(frontdoorTopic);
    const handler = async (requestMessage) => {
        const requestBody = requestMessage.body;
        const arg = requestBody["fn.validateSchema"];
        const schemaPseudoJson = arg["schema"];
        const extendSchemaJson = arg["extend!"];
        const serializeSchema = requestMessage.header["_serializeSchema"] !== false;
        let schemaJson;
        if (serializeSchema) {
            try {
                schemaJson = JSON.stringify(schemaPseudoJson);
            }
            catch (e) {
                throw e;
            }
        }
        else {
            schemaJson = schemaPseudoJson;
        }
        try {
            const schema = UApiSchema.fromJson(schemaJson);
            if (extendSchemaJson != null) {
                UApiSchema.extend(schema, extendSchemaJson);
            }
            return new Message({}, { Ok: {} });
        }
        catch (e) {
            console.error(e);
            return new Message({}, {
                ErrorValidationFailure: {
                    cases: e.schemaParseFailuresPseudoJson,
                },
            });
        }
    };
    const options = new ServerOptions();
    options.onError = (e) => console.error(e);
    options.authRequired = false;
    const server = new Server(uApi, handler, options);
    const sub = connection.subscribe(frontdoorTopic);
    (async () => {
        for await (const msg of sub) {
            const requestBytes = msg.data;
            console.log(`    ->S ${new TextDecoder().decode(requestBytes)}`);
            let responseBytes;
            const time = timer.startTimer();
            try {
                responseBytes = await server.process(requestBytes);
            }
            finally {
                time();
            }
            console.log(`    <-S ${new TextDecoder().decode(responseBytes)}`);
            msg.respond(responseBytes);
        }
    })();
    return sub;
}
function startTestServer(connection, registry, apiSchemaPath, frontdoorTopic, backdoorTopic, authRequired) {
    const json = fs.readFileSync(apiSchemaPath, "utf-8");
    let uApi = UApiSchema.fromJson(json);
    const alternateUApi = UApiSchema.extend(uApi, `
        [
            {
                "struct.BackwardsCompatibleChange": {}
            }
        ]
    `);
    const timer = registry.createTimer(frontdoorTopic);
    const serveAlternateServer = { value: false };
    class ThisError extends Error {
    }
    const handler = async (requestMessage) => {
        const requestHeaders = requestMessage.header;
        const requestBody = requestMessage.body;
        const requestPseudoJson = [requestHeaders, requestBody];
        const requestJson = JSON.stringify(requestPseudoJson);
        const requestBytes = new TextEncoder().encode(requestJson);
        console.log(`    <-s ${new TextDecoder().decode(requestBytes)}`);
        const natsResponseMessage = await connection.request(backdoorTopic, requestBytes, { timeout: 5000 });
        console.log(`    ->s ${new TextDecoder().decode(natsResponseMessage.data)}`);
        const responseJson = new TextDecoder().decode(natsResponseMessage.data);
        const responsePseudoJson = JSON.parse(responseJson);
        const responseHeaders = responsePseudoJson[0];
        const responseBody = responsePseudoJson[1];
        if (requestHeaders["_toggleAlternateServer"] === true) {
            serveAlternateServer.value = !serveAlternateServer.value;
        }
        if (requestHeaders["_throwError"] === true) {
            throw new ThisError();
        }
        return new Message(responseHeaders, responseBody);
    };
    const options = new ServerOptions();
    options.onError = (e) => {
        console.error(e);
        if (e instanceof ThisError) {
            throw new Error();
        }
    };
    options.onRequest = (m) => {
        if (m.header["_onRequestError"] === true) {
            throw new Error();
        }
    };
    options.onResponse = (m) => {
        if (m.header["_onResponseError"] === true) {
            throw new Error();
        }
    };
    options.authRequired = authRequired;
    const server = new Server(uApi, handler, options);
    const alternateOptions = new ServerOptions();
    alternateOptions.onError = (e) => console.error(e);
    alternateOptions.authRequired = authRequired;
    const alternateServer = new Server(alternateUApi, handler, alternateOptions);
    const subscription = connection.subscribe(frontdoorTopic);
    (async () => {
        for await (const msg of subscription) {
            const requestBytes = msg.data;
            console.log(`    ->S ${new TextDecoder().decode(requestBytes)}`);
            let responseBytes;
            const time = timer.startTimer();
            try {
                if (serveAlternateServer.value) {
                    responseBytes = await alternateServer.process(requestBytes);
                }
                else {
                    responseBytes = await server.process(requestBytes);
                }
            }
            finally {
                time();
            }
            console.log(`    <-S ${new TextDecoder().decode(responseBytes)}`);
            msg.respond(responseBytes);
        }
    })();
    console.log(`Test server listening on ${frontdoorTopic}`);
    return subscription;
}
async function runDispatcherServer() {
    const natsUrl = process.env.NATS_URL;
    if (!natsUrl) {
        throw new Error("NATS_URL env var not set");
    }
    const registry = new Registry();
    const servers = {};
    const connection = await connect({ servers: natsUrl });
    let finish;
    const done = new Promise((resolve) => {
        finish = resolve;
    });
    const subscription = connection.subscribe("ts");
    (async () => {
        for await (const msg of subscription) {
            const requestBytes = msg.data;
            const requestJson = new TextDecoder().decode(requestBytes);
            console.log(`    ->S ${requestJson}`);
            let responseBytes;
            try {
                const request = JSON.parse(requestJson);
                const body = request[1];
                const entry = Object.entries(body)[0];
                const target = entry[0];
                const payload = entry[1];
                switch (target) {
                    case "Ping": {
                        break;
                    }
                    case "End": {
                        finish();
                        break;
                    }
                    case "Stop": {
                        const id = payload["id"];
                        const s = servers[id];
                        if (s != null) {
                            s.drain();
                        }
                        break;
                    }
                    case "StartServer": {
                        const id = payload["id"];
                        const apiSchemaPath = payload["apiSchemaPath"];
                        const frontdoorTopic = payload["frontdoorTopic"];
                        const backdoorTopic = payload["backdoorTopic"];
                        const authRequired = payload["authRequired!"] ?? false;
                        const d = startTestServer(connection, registry, apiSchemaPath, frontdoorTopic, backdoorTopic, authRequired);
                        servers[id] = d;
                        break;
                    }
                    case "StartClientServer": {
                        const id = payload["id"];
                        const clientFrontdoorTopic = payload["clientFrontdoorTopic"];
                        const clientBackdoorTopic = payload["clientBackdoorTopic"];
                        const useBinary = payload["useBinary"] ?? false;
                        const d = startClientTestServer(connection, registry, clientFrontdoorTopic, clientBackdoorTopic, useBinary);
                        servers[id] = d;
                        break;
                    }
                    case "StartMockServer": {
                        const id = payload["id"];
                        const apiSchemaPath = payload["apiSchemaPath"];
                        const frontdoorTopic = payload["frontdoorTopic"];
                        const config = payload["config"];
                        const d = startMockTestServer(connection, registry, apiSchemaPath, frontdoorTopic, config);
                        servers[id] = d;
                        break;
                    }
                    case "StartSchemaServer": {
                        const id = payload["id"];
                        const apiSchemaPath = payload["apiSchemaPath"];
                        const frontdoorTopic = payload["frontdoorTopic"];
                        const d = startSchemaTestServer(connection, registry, apiSchemaPath, frontdoorTopic);
                        servers[id] = d;
                        break;
                    }
                    default: {
                        throw new Error("no matching server");
                    }
                }
                const responseJson = JSON.stringify([
                    new Map(),
                    new Map([["Ok", new Map()]]),
                ]);
                responseBytes = new TextEncoder().encode(responseJson);
            }
            catch (e) {
                console.error(e);
                try {
                    const responseJson = JSON.stringify([
                        new Map(),
                        new Map([["ErrorUnknown", new Map()]]),
                    ]);
                    responseBytes = new TextEncoder().encode(responseJson);
                }
                catch (e1) {
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
