import * as fs from 'node:fs';
import * as path from 'node:path';
import { Client, ClientOptions, FunctionRouter, Message, Server, ServerOptions, TelepactSchema } from 'telepact';
import { connect, headers as createHeaders, NatsConnection, Subscription } from 'nats';
import protobuf from 'protobufjs';

const metricHeaders = {
  requestTransit: 'x-request-transit-ns',
  serverDeserialize: 'x-server-request-deserialize-ns',
  serverSerialize: 'x-server-response-serialize-ns',
  serverSent: 'x-server-sent-ns',
};

type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];
type JsonObject = { [key: string]: JsonValue };

type CaseDefinition = {
  dataShape: string;
  collectionShape: string;
  telepactFunction: string;
  envelopeField: string;
  payload: JsonObject;
};

type Sample = Record<string, number>;

function nowNs(): number {
  return Number(process.hrtime.bigint());
}

class PlainJsonCodec {
  private readonly requestObject: JsonObject;
  private readonly responseObject: JsonObject;

  constructor(private readonly envelopeField: string, payload: JsonObject) {
    this.requestObject = { [envelopeField]: payload };
    this.responseObject = { [envelopeField]: payload };
  }

  encodeRequest(): Uint8Array {
    return new TextEncoder().encode(JSON.stringify(this.requestObject));
  }

  decodeRequest(data: Uint8Array): JsonObject {
    const obj = JSON.parse(new TextDecoder().decode(data)) as JsonObject;
    if (Object.keys(obj)[0] !== this.envelopeField) {
      throw new Error('unexpected plain json request envelope');
    }
    return obj;
  }

  encodeResponse(): Uint8Array {
    return new TextEncoder().encode(JSON.stringify(this.responseObject));
  }

  decodeResponse(data: Uint8Array): JsonObject {
    const obj = JSON.parse(new TextDecoder().decode(data)) as JsonObject;
    if (Object.keys(obj)[0] !== this.envelopeField) {
      throw new Error('unexpected plain json response envelope');
    }
    return obj;
  }
}

class ProtobufCodec {
  private readonly requestType: protobuf.Type;
  private readonly responseType: protobuf.Type;
  private readonly requestMessage: protobuf.Message<{}>;
  private readonly responseMessage: protobuf.Message<{}>;

  constructor(protoPath: string, private readonly envelopeField: string, payload: JsonObject) {
    const root = protobuf.loadSync(protoPath);
    this.requestType = root.lookupType('telepact.performance.Request') as protobuf.Type;
    this.responseType = root.lookupType('telepact.performance.Response') as protobuf.Type;
    this.requestMessage = this.requestType.fromObject({ [envelopeField]: payload });
    this.responseMessage = this.responseType.fromObject({ [envelopeField]: payload });
  }

  encodeRequest(): Uint8Array {
    return this.requestType.encode(this.requestMessage).finish();
  }

  decodeRequest(data: Uint8Array): protobuf.Message<{}> {
    const message = this.requestType.decode(data);
    const object = this.requestType.toObject(message, { defaults: false }) as Record<string, unknown>;
    if (!(this.envelopeField in object)) {
      throw new Error('unexpected protobuf request envelope');
    }
    return message;
  }

  encodeResponse(): Uint8Array {
    return this.responseType.encode(this.responseMessage).finish();
  }

  decodeResponse(data: Uint8Array): protobuf.Message<{}> {
    const message = this.responseType.decode(data);
    const object = this.responseType.toObject(message, { defaults: false }) as Record<string, unknown>;
    if (!(this.envelopeField in object)) {
      throw new Error('unexpected protobuf response envelope');
    }
    return message;
  }
}

async function buildTelepactCase(
  clientConnection: NatsConnection,
  serverConnection: NatsConnection,
  schema: TelepactSchema,
  caseDefinition: CaseDefinition,
  method: string,
): Promise<{ run: () => Promise<Sample>; finish: () => Promise<void> }> {
  const subject = `telepact.performance.typescript.${Math.random().toString(16).slice(2)}`;
  const functionRouter = new FunctionRouter({
    [caseDefinition.telepactFunction]: async () => new Message({}, { Ok_: caseDefinition.payload }),
  });
  const serverOptions = new ServerOptions();
  serverOptions.authRequired = false;
  const server = new Server(schema, functionRouter, serverOptions);
  const subscription: Subscription = serverConnection.subscribe(subject);

  (async () => {
    for await (const msg of subscription) {
      const requestTransit = nowNs() - Number(msg.headers?.get('x-client-sent-ns'));
      const deserializeStart = nowNs();
      const requestMessage = server.serializer.deserialize(msg.data);
      const deserializeDuration = nowNs() - deserializeStart;
      const responseHeaders: Record<string, any> = {};
      if ('@bin_' in requestMessage.headers) {
        responseHeaders['@binary_'] = true;
        responseHeaders['@clientKnownBinaryChecksums_'] = requestMessage.headers['@bin_'];
        if ('@pac_' in requestMessage.headers) {
          responseHeaders['@pac_'] = requestMessage.headers['@pac_'];
        }
      }
      const responseMessage = new Message(responseHeaders, { Ok_: caseDefinition.payload });
      const serializeStart = nowNs();
      const responseBytes = server.serializer.serialize(responseMessage);
      const serializeDuration = nowNs() - serializeStart;
      const replyHeaders = createHeaders();
      replyHeaders.set(metricHeaders.requestTransit, String(requestTransit));
      replyHeaders.set(metricHeaders.serverDeserialize, String(deserializeDuration));
      replyHeaders.set(metricHeaders.serverSerialize, String(serializeDuration));
      replyHeaders.set(metricHeaders.serverSent, String(nowNs()));
      serverConnection.publish(msg.reply!, responseBytes, { headers: replyHeaders });
    }
  })();
  await serverConnection.flush();

  const clientOptions = new ClientOptions();
  clientOptions.useBinary = method === 'telepact_binary' || method === 'telepact_packed_binary';
  clientOptions.alwaysSendJson = method === 'telepact_json';
  const client = new Client(async (requestMessage, serializer) => {
    const serializeStart = nowNs();
    const requestBytes = serializer.serialize(requestMessage);
    const clientRequestSerialize = nowNs() - serializeStart;
    const requestHeaders = createHeaders();
    requestHeaders.set('x-client-sent-ns', String(nowNs()));
    const response = await clientConnection.request(subject, requestBytes, { headers: requestHeaders, timeout: 30000 });
    const responseNetworkTransit = nowNs() - Number(response.headers?.get(metricHeaders.serverSent));
    const deserializeStart = nowNs();
    const responseMessage = serializer.deserialize(response.data);
    const clientResponseDeserialize = nowNs() - deserializeStart;
    return new Message(
      {
        clientRequestSerializeNs: clientRequestSerialize,
        requestSizeBytes: requestBytes.length,
        requestNetworkTransitNs: Number(response.headers?.get(metricHeaders.requestTransit)),
        serverRequestDeserializeNs: Number(response.headers?.get(metricHeaders.serverDeserialize)),
        serverResponseSerializeNs: Number(response.headers?.get(metricHeaders.serverSerialize)),
        responseSizeBytes: response.data.length,
        responseNetworkTransitNs: responseNetworkTransit,
        clientResponseDeserializeNs: clientResponseDeserialize,
      },
      responseMessage.body,
    );
  }, clientOptions);

  return {
    run: async (): Promise<Sample> => {
      const headers: Record<string, any> = {};
      if (method === 'telepact_packed_binary') {
        headers['@pac_'] = true;
      }
      const response = await client.request(new Message(headers, { [caseDefinition.telepactFunction]: caseDefinition.payload }));
      if (JSON.stringify(response.body) !== JSON.stringify({ Ok_: caseDefinition.payload })) {
        throw new Error('unexpected telepact response');
      }
      return response.headers as unknown as Sample;
    },
    finish: async (): Promise<void> => {
      subscription.unsubscribe();
      await serverConnection.flush();
    },
  };
}

async function buildNonTelepactCase(
  clientConnection: NatsConnection,
  serverConnection: NatsConnection,
  caseDefinition: CaseDefinition,
  method: string,
  protoPath: string,
): Promise<{ run: () => Promise<Sample>; finish: () => Promise<void> }> {
  const subject = `telepact.performance.typescript.${Math.random().toString(16).slice(2)}`;
  const codec = method === 'plain_json'
    ? new PlainJsonCodec(caseDefinition.envelopeField, caseDefinition.payload)
    : new ProtobufCodec(protoPath, caseDefinition.envelopeField, caseDefinition.payload);
  const subscription = serverConnection.subscribe(subject);
  (async () => {
    for await (const msg of subscription) {
      const requestTransit = nowNs() - Number(msg.headers?.get('x-client-sent-ns'));
      const deserializeStart = nowNs();
      codec.decodeRequest(msg.data);
      const deserializeDuration = nowNs() - deserializeStart;
      const serializeStart = nowNs();
      const responseBytes = codec.encodeResponse();
      const serializeDuration = nowNs() - serializeStart;
      const replyHeaders = createHeaders();
      replyHeaders.set(metricHeaders.requestTransit, String(requestTransit));
      replyHeaders.set(metricHeaders.serverDeserialize, String(deserializeDuration));
      replyHeaders.set(metricHeaders.serverSerialize, String(serializeDuration));
      replyHeaders.set(metricHeaders.serverSent, String(nowNs()));
      serverConnection.publish(msg.reply!, responseBytes, { headers: replyHeaders });
    }
  })();
  await serverConnection.flush();

  return {
    run: async (): Promise<Sample> => {
      const serializeStart = nowNs();
      const requestBytes = codec.encodeRequest();
      const clientRequestSerialize = nowNs() - serializeStart;
      const requestHeaders = createHeaders();
      requestHeaders.set('x-client-sent-ns', String(nowNs()));
      const response = await clientConnection.request(subject, requestBytes, { headers: requestHeaders, timeout: 30000 });
      const responseNetworkTransit = nowNs() - Number(response.headers?.get(metricHeaders.serverSent));
      const deserializeStart = nowNs();
      codec.decodeResponse(response.data);
      const clientResponseDeserialize = nowNs() - deserializeStart;
      return {
        clientRequestSerializeNs: clientRequestSerialize,
        requestSizeBytes: requestBytes.length,
        requestNetworkTransitNs: Number(response.headers?.get(metricHeaders.requestTransit)),
        serverRequestDeserializeNs: Number(response.headers?.get(metricHeaders.serverDeserialize)),
        serverResponseSerializeNs: Number(response.headers?.get(metricHeaders.serverSerialize)),
        responseSizeBytes: response.data.length,
        responseNetworkTransitNs: responseNetworkTransit,
        clientResponseDeserializeNs: clientResponseDeserialize,
      };
    },
    finish: async (): Promise<void> => {
      subscription.unsubscribe();
      await serverConnection.flush();
    },
  };
}

async function executeCase(
  clientConnection: NatsConnection,
  serverConnection: NatsConnection,
  schema: TelepactSchema,
  caseDefinition: CaseDefinition,
  method: string,
  warmup: number,
  iterations: number,
  protoPath: string,
): Promise<Record<string, unknown>> {
  const bench = method.startsWith('telepact_')
    ? await buildTelepactCase(clientConnection, serverConnection, schema, caseDefinition, method)
    : await buildNonTelepactCase(clientConnection, serverConnection, caseDefinition, method, protoPath);
  try {
    for (let i = 0; i < warmup; i += 1) {
      await bench.run();
    }
    const samples: Sample[] = [];
    for (let i = 0; i < iterations; i += 1) {
      samples.push(await bench.run());
    }
    return {
      method,
      dataShape: caseDefinition.dataShape,
      collectionShape: caseDefinition.collectionShape,
      samples,
    };
  } finally {
    await bench.finish();
  }
}

function parseArgs(): Record<string, string> {
  const args = process.argv.slice(2);
  const parsed: Record<string, string> = {};
  for (let i = 0; i < args.length; i += 2) {
    parsed[args[i].replace(/^--/, '')] = args[i + 1];
  }
  return parsed;
}

async function main(): Promise<void> {
  const args = parseArgs();
  const payloads = JSON.parse(fs.readFileSync(args.payloads, 'utf8')) as { cases: CaseDefinition[] };
  const schema = TelepactSchema.fromDirectory(args['schema-dir'], fs, path);
  const clientConnection = await connect({ servers: args['nats-url'] });
  const serverConnection = await connect({ servers: args['nats-url'] });
  try {
    const results: Record<string, unknown>[] = [];
    const protoPath = path.join(path.dirname(args['schema-dir']), 'protobuf', 'performance.proto');
    for (const method of ['telepact_json', 'telepact_binary', 'telepact_packed_binary', 'protobuf', 'plain_json']) {
      for (const caseDefinition of payloads.cases) {
        results.push(
          await executeCase(
            clientConnection,
            serverConnection,
            schema,
            caseDefinition,
            method,
            Number(args.warmup),
            Number(args.iterations),
            protoPath,
          ),
        );
      }
    }
    fs.writeFileSync(
      args.output,
      `${JSON.stringify(
        {
          language: 'typescript',
          natsUrl: args['nats-url'],
          warmupIterations: Number(args.warmup),
          measuredIterations: Number(args.iterations),
          cases: results,
        },
        null,
        2,
      )}\n`,
    );
  } finally {
    await clientConnection.close();
    await serverConnection.close();
  }
}

void main();
