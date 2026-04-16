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

import { Client, ClientOptions, Message } from '/vendor/telepact/index.esm.js';

const sessionStatus = document.querySelector('#session-status');
const binaryStatus = document.querySelector('#binary-status');
const dashboardOutput = document.querySelector('#dashboard-output');
const detailsOutput = document.querySelector('#details-output');

let binaryResponsesObserved = 0;
let nextCall = null;

function replaceBinary(_, value) {
  if (value instanceof Uint8Array) {
    return {
      type: 'bytes',
      length: value.length,
      preview: new TextDecoder().decode(value),
    };
  }
  return value;
}

function render(element, message) {
  element.textContent = JSON.stringify(message, replaceBinary, 2);
}

const adapter = async (message, serializer) => {
  const requestBytes = serializer.serialize(message);
  const response = await fetch('/api/telepact', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: requestBytes,
  });

  const responseBytes = new Uint8Array(await response.arrayBuffer());
  const telepactResponse = serializer.deserialize(responseBytes);
  if ('@bin_' in telepactResponse.headers) {
    binaryResponsesObserved += 1;
    binaryStatus.textContent = `Binary responses observed: ${binaryResponsesObserved}`;
  }
  return telepactResponse;
};

const options = new ClientOptions();
options.useBinary = true;
options.alwaysSendJson = false;
options.localStorageCacheNamespace = 'telepact-example-node-browser-docker';
const client = new Client(adapter, options);

async function requestDashboard() {
  const response = await client.request(new Message({
    '@select_': {
      'struct.OrderSummary': ['id', 'status'],
    },
  }, {
    'fn.getDashboard': {},
  }));

  render(dashboardOutput, [response.headers, response.body]);
  nextCall = response.getBodyPayload()['firstOrderDetails!'] ?? null;
}

async function requestDetails() {
  if (nextCall == null) {
    detailsOutput.textContent = 'Load the dashboard first.';
    return;
  }

  const response = await client.request(new Message({}, nextCall));
  render(detailsOutput, [response.headers, response.body]);
}

document.querySelector('#start-session').addEventListener('click', async () => {
  await fetch('/session/demo', {
    credentials: 'include',
  });
  sessionStatus.textContent = 'Session: demo-session cookie issued by the gateway';
});

document.querySelector('#load-dashboard').addEventListener('click', async () => {
  try {
    await requestDashboard();
  } catch (error) {
    dashboardOutput.textContent = String(error);
  }
});

document.querySelector('#follow-link').addEventListener('click', async () => {
  try {
    await requestDetails();
  } catch (error) {
    detailsOutput.textContent = String(error);
  }
});
