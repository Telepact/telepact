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

import { createServer } from 'node:http';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Client, ClientOptions, FunctionRouter, Message, Server, ServerOptions, TelepactSchema } from 'telepact';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const gatewayPort = Number(process.env.PORT ?? 8080);
const catalogBaseUrl = process.env.CATALOG_BASE_URL ?? 'http://127.0.0.1:8081';
const validSessionToken = 'demo-session';
const viewerId = 'viewer-1';
let binaryResponsesObserved = 0;

function createTelepactHttpClient(baseUrl) {
  const adapter = async (message, serializer) => {
    const requestBytes = serializer.serialize(message);
    const response = await fetch(`${baseUrl}/api/telepact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: requestBytes,
    });
    const responseBytes = new Uint8Array(await response.arrayBuffer());
    const responseMessage = serializer.deserialize(responseBytes);
    if ('@bin_' in responseMessage.headers) {
      binaryResponsesObserved += 1;
    }
    return responseMessage;
  };

  const options = new ClientOptions();
  options.useBinary = true;
  options.alwaysSendJson = false;
  return new Client(adapter, options);
}

const catalogClient = createTelepactHttpClient(catalogBaseUrl);
const schema = TelepactSchema.fromDirectory(path.join(__dirname, 'gateway-api'), fs, path);
const serverOptions = new ServerOptions();
serverOptions.authRequired = false;
serverOptions.onAuth = (headers) => {
  const auth = headers['@auth_'];
  if (auth?.Session?.sessionToken === validSessionToken) {
    return { '@viewerId': viewerId };
  }
  return {};
};

function unauthenticated() {
  return new Message({}, {
    ErrorUnauthenticated_: {
      'message!': 'start the demo session first',
    },
  });
}

async function getDashboard() {
  const response = await catalogClient.request(new Message({}, {
    'fn.loadViewerDashboard': { viewerId },
  }));
  const payload = response.getBodyPayload();
  const orders = payload.orders ?? [];
  return new Message({}, {
    Ok_: {
      viewer: payload.viewer,
      orders,
      'firstOrderDetails!': {
        'fn.getOrderDetails': {
          orderId: orders[0]?.id ?? 'order-1001',
        },
      },
    },
  });
}

async function getOrderDetails(functionName, requestMessage) {
  if (requestMessage.headers['@viewerId'] !== viewerId) {
    return unauthenticated();
  }

  const { orderId } = requestMessage.body[functionName];
  const response = await catalogClient.request(new Message({}, {
    'fn.getOrderDetails': {
      viewerId,
      orderId,
    },
  }));
  return new Message({}, {
    Ok_: {
      order: response.getBodyPayload().order,
    },
  });
}

async function loadDashboard(functionName, requestMessage) {
  if (requestMessage.headers['@viewerId'] !== viewerId) {
    return unauthenticated();
  }

  return getDashboard();
}

const functionRouter = new FunctionRouter({
  'fn.getDashboard': loadDashboard,
  'fn.getOrderDetails': getOrderDetails,
});
const telepactServer = new Server(schema, functionRouter, serverOptions);

function readSessionCookie(cookieHeader) {
  if (!cookieHeader) {
    return null;
  }

  for (const cookie of cookieHeader.split(';')) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'session') {
      return value ?? null;
    }
  }

  return null;
}

async function readRequestBytes(request) {
  const chunks = [];
  for await (const chunk of request) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}

function writeResponse(response, statusCode, body, contentType = 'text/plain; charset=utf-8', extraHeaders = {}) {
  response.writeHead(statusCode, {
    'Content-Type': contentType,
    ...extraHeaders,
  });
  response.end(body);
}

function sendStaticFile(response, filename, contentType) {
  const filePath = path.join(__dirname, filename);
  writeResponse(response, 200, fs.readFileSync(filePath), contentType);
}

const server = createServer(async (request, response) => {
  const requestUrl = new URL(request.url ?? '/', `http://${request.headers.host ?? 'localhost'}`);

  if (request.method === 'GET' && requestUrl.pathname === '/health') {
    writeResponse(response, 200, 'ok');
    return;
  }

  if (request.method === 'GET' && requestUrl.pathname === '/') {
    sendStaticFile(response, 'public/index.html', 'text/html; charset=utf-8');
    return;
  }

  if (request.method === 'GET' && requestUrl.pathname === '/app.js') {
    sendStaticFile(response, 'public/app.js', 'text/javascript; charset=utf-8');
    return;
  }

  if (request.method === 'GET' && requestUrl.pathname === '/session/demo') {
    writeResponse(response, 204, '', 'text/plain; charset=utf-8', {
      'Set-Cookie': `session=${validSessionToken}; Path=/; HttpOnly; SameSite=Lax`,
    });
    return;
  }

  if (request.method !== 'POST' || requestUrl.pathname !== '/api/telepact') {
    writeResponse(response, 404, 'not found');
    return;
  }

  const requestBytes = await readRequestBytes(request);
  const sessionToken = readSessionCookie(request.headers.cookie);
  const telepactResponse = await telepactServer.process(new Uint8Array(requestBytes), (headers) => {
    if (sessionToken != null) {
      headers['@auth_'] = {
        Session: {
          sessionToken,
        },
      };
    }
  });
  const contentType = '@bin_' in telepactResponse.headers ? 'application/octet-stream' : 'application/json';
  writeResponse(response, 200, Buffer.from(telepactResponse.bytes), contentType, {
    'X-Telepact-Server-Binary-Count': String(binaryResponsesObserved),
  });
});

server.listen(gatewayPort, '0.0.0.0', () => {
  console.log(`gateway listening on http://0.0.0.0:${gatewayPort}`);
});
