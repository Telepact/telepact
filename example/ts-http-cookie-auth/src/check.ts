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

async function post(url: string, cookie?: string): Promise<any> {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            ...(cookie ? { cookie } : {}),
        },
        body: JSON.stringify([{}, { 'fn.me': {} }]),
    });

    if (!response.ok) {
        throw new Error(`Unexpected HTTP ${response.status}`);
    }

    return await response.json();
}

async function main(): Promise<void> {
    const url = process.argv[2];
    if (!url) {
        throw new Error('Usage: node dist/check.js <url>');
    }

    const unauthenticated = await post(url);
    if (unauthenticated[1]?.ErrorUnauthenticated_?.['message!'] !== 'missing or invalid session cookie') {
        throw new Error(`Expected unauthenticated response, got ${JSON.stringify(unauthenticated)}`);
    }

    const authenticated = await post(url, 'session=demo-session');
    if (authenticated[1]?.Ok_?.userId !== 'user-123') {
        throw new Error(`Expected authenticated response, got ${JSON.stringify(authenticated)}`);
    }

    console.log('ts-http-cookie-auth check passed');
}

void main();
