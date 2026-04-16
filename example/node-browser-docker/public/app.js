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

const sessionStatus = document.querySelector('#session-status');
const binaryStatus = document.querySelector('#binary-status');
const dashboardOutput = document.querySelector('#dashboard-output');
const detailsOutput = document.querySelector('#details-output');

let nextCall = null;

function render(element, message) {
  element.textContent = JSON.stringify(message, null, 2);
}

async function telepactRequest(headers, body) {
  const response = await fetch('/api/telepact', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify([headers, body]),
  });
  const binaryCount = response.headers.get('X-Telepact-Server-Binary-Count') ?? '0';
  binaryStatus.textContent = `Gateway binary responses observed: ${binaryCount}`;
  return await response.json();
}

async function requestDashboard() {
  const response = await telepactRequest({
    '@select_': {
      'struct.OrderSummary': ['id', 'status'],
    },
  }, {
    'fn.getDashboard': {},
  });
  render(dashboardOutput, response);
  nextCall = response[1]?.Ok_?.['firstOrderDetails!'] ?? null;
}

async function requestDetails() {
  if (nextCall == null) {
    detailsOutput.textContent = 'Load the dashboard first.';
    return;
  }

  const response = await telepactRequest({}, nextCall);
  render(detailsOutput, response);
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
