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

import { Client, Message } from './telepact/index.esm.js';

export function submitRequest(client: Client, requestJson: string): Promise<string> {
	const requestPseudoJson = JSON.parse(requestJson);
	const requestMessage = new Message(requestPseudoJson[0], requestPseudoJson[1]);

	const startTime = Date.now();

	return new Promise<string>((resolve, reject) => {
		setTimeout(async () => {
			try {
				const rs = await client.request(requestMessage);
				resolve(JSON.stringify([rs.headers, rs.body], null, 2));
			} catch (error) {
				reject(error);
			}
		}, Math.max(0, 500 - (Date.now() - startTime)));
	});
}

