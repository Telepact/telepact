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
import { FunctionRouter, Message, Server, ServerOptions, TelepactSchema } from 'telepact';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const textEncoder = new TextEncoder();

const viewer = {
  id: 'viewer-1',
  name: 'Ada Lovelace',
  plan: 'pro',
  avatar: textEncoder.encode('avatar:ada-lovelace:pro:telepact-demo'),
};

const orders = [
  {
    id: 'order-1001',
    status: 'packing',
    totalCents: 2599,
    shippingEta: '2026-04-18',
    receipt: textEncoder.encode('receipt:order-1001:packing:2599'),
  },
  {
    id: 'order-1002',
    status: 'shipped',
    totalCents: 4899,
    shippingEta: '2026-04-17',
    receipt: textEncoder.encode('receipt:order-1002:shipped:4899'),
  },
];

function ok(body) {
  return new Message({}, { Ok_: body });
}

function getOrder(orderId) {
  return orders.find((order) => order.id === orderId) ?? orders[0];
}

async function loadViewerDashboard(functionName, requestMessage) {
  const { viewerId } = requestMessage.body[functionName];
  if (viewerId !== viewer.id) {
    return ok({ viewer, orders: [] });
  }

  return ok({
    viewer,
    orders: orders.map(({ id, status, totalCents }) => ({ id, status, totalCents })),
  });
}

async function getOrderDetails(functionName, requestMessage) {
  const { viewerId, orderId } = requestMessage.body[functionName];
  if (viewerId !== viewer.id) {
    return ok({ order: getOrder(orderId) });
  }

  return ok({ order: getOrder(orderId) });
}

const schema = TelepactSchema.fromDirectory(path.join(__dirname, 'catalog-api'), fs, path);
const options = new ServerOptions();
options.authRequired = false;
const functionRouter = new FunctionRouter({
  'fn.loadViewerDashboard': loadViewerDashboard,
  'fn.getOrderDetails': getOrderDetails,
});
const telepactServer = new Server(schema, functionRouter, options);

function writeBytesResponse(response, statusCode, body, contentType = 'application/json') {
  response.writeHead(statusCode, { 'Content-Type': contentType });
  response.end(body);
}

async function readRequestBytes(request) {
  const chunks = [];
  for await (const chunk of request) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}

const server = createServer(async (request, response) => {
  if (request.method === 'GET' && request.url === '/health') {
    writeBytesResponse(response, 200, 'ok', 'text/plain; charset=utf-8');
    return;
  }

  if (request.method !== 'POST' || request.url !== '/api/telepact') {
    writeBytesResponse(response, 404, 'not found', 'text/plain; charset=utf-8');
    return;
  }

  const requestBytes = await readRequestBytes(request);
  const telepactResponse = await telepactServer.process(new Uint8Array(requestBytes));
  const contentType = '@bin_' in telepactResponse.headers ? 'application/octet-stream' : 'application/json';
  writeBytesResponse(response, 200, Buffer.from(telepactResponse.bytes), contentType);
});

server.listen(8081, '0.0.0.0', () => {
  console.log('catalog listening on http://0.0.0.0:8081');
});
