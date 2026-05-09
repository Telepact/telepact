//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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

