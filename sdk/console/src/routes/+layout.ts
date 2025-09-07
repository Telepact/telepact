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
	Client,
	ClientOptions,
	MockServer,
	MockServerOptions,
	ServerOptions,
	Server,
	Serializer,
	TelepactSchema,
	Message,
	MockTelepactSchema
} from '$lib/telepact/index.esm';
import type { LayoutLoad } from './$types';
import demoSchemaPseudoJson from './demo.telepact.json';
import prettier from 'prettier/standalone';
import telepactPlugin from '$lib/prettier-plugin-telepact/index.esm';
import markdownPlugin from 'prettier/plugins/markdown';
import estreePlugin from 'prettier/plugins/estree';
import babelPlugin from 'prettier/plugins/babel';
//import { createJsonSchema } from '$lib';

export const prerender = true;
export const ssr = false;

declare global {
	interface Window {
		overrideAuthHeader: (schemaSource: string, next: (newAuthHeader: Record<string, object>) => Promise<Message>) => Promise<Message>
		overrideDefaultSchema: () => string
	}
}

export const load: LayoutLoad = async ({ url, params, route, fetch }) => {
	console.log('layout load');
	let schemaSource = url.searchParams.get('s') ?? '';
	let showInternalApi = url.searchParams.get('i') === '1';

	const authManaged = window.overrideAuthHeader !== undefined;
	const overrideDefaultSchema = window.overrideDefaultSchema !== undefined;

	console.log(`authManaged ${authManaged}`);
	console.log(`overrideDefaultSchema ${overrideDefaultSchema}`);

	let result: {
		client?: Client;
		showInternalApi?: boolean;
		readonlyEditor?: boolean;
		schemaSource?: string;
	} = {};
	if (schemaSource === '') {
		let defaultSchema = overrideDefaultSchema ? window.overrideDefaultSchema() : '[{"///": "No schema loaded.\\n\\nTry [editing the schema](/?v=ds), or loading a schema from a live running Telepact server by entering a URL in the `Live URL` text box.", "info.Example":{}}]';

		let schemaDraft = (url.searchParams.get('sd') as string) ?? defaultSchema;

		let telepactSchema = MockTelepactSchema.fromJson(schemaDraft);

		let mockServerOptions = new MockServerOptions();
		mockServerOptions.generatedCollectionLengthMin = 2;
		mockServerOptions.randomizeOptionalFieldGeneration = false;
		mockServerOptions.onError = (e) => {
			console.log(e);
		};
		let mockServer = new MockServer(telepactSchema, mockServerOptions);

		let mockClient = new Client(async (m: Message, s: Serializer) => {
			let req = s.serialize(m);
			let res = await mockServer.process(req);
			return s.deserialize(res);
		}, new ClientOptions());

		result = {
			schemaSource: 'draft',
			client: mockClient,
			showInternalApi: showInternalApi,
			readonlyEditor: false
		};
	} else if (schemaSource?.startsWith('http')) {
		let client = new Client(async (m: Message, s: Serializer) => {
			const maybeOverrideAuthHeader = async (newAuthHeader: Record<string, object> | undefined, next: () => Promise<Message>) => {
				if (newAuthHeader !== undefined) {
					m.headers['@auth_'] = newAuthHeader;
				}

				return next();
			};

			const finish = async () => {
				let req = s.serialize(m);
				let res = await fetch(schemaSource, {
					method: 'POST',
					body: req
				});
				let buf = await res.arrayBuffer();
				let responseBytes = new Uint8Array(buf);
				return s.deserialize(responseBytes);
			}

			const fn = m.getBodyTarget();

			if (fn.endsWith('_') || window.overrideAuthHeader === undefined) {
				return maybeOverrideAuthHeader(undefined, finish);
			} else {
				return window.overrideAuthHeader(schemaSource, (a) => maybeOverrideAuthHeader(a, finish));
			}


		}, new ClientOptions());

		result = {
			schemaSource: 'http',
			client: client,
			showInternalApi: showInternalApi,
			readonlyEditor: true
		};
	} else if (schemaSource === 'demo') {
		let telepactSchema = TelepactSchema.fromJson(JSON.stringify(demoSchemaPseudoJson));

		let serverOptions = new ServerOptions();
		serverOptions.authRequired = false;
		serverOptions.onError = (e) => {
			console.log(e);
		};
		let handler = async (m: Message) => {
			if (m.getBodyTarget() === 'fn.compute') {
				let args = m.getBodyPayload();
				let x = args['x']['Constant']['value'];
				let y = args['y']['Constant']['value'];
				let op = args['op'];
				let opKey = Object.keys(op)[0];

				switch (opKey) {
					case 'Add':
						return new Message({}, { Ok_: { result: x + y } });
					case 'Sub':
						return new Message({}, { Ok_: { result: x - y } });
					case 'Mul':
						return new Message({}, { Ok_: { result: x * y } });
					case 'Div':
						return new Message({}, { Ok_: { result: x / y } });
					default:
						throw new Error('Invalid operation');
				}
			} else {
				throw new Error('Not implemented');
			}
		};
		let server = new Server(telepactSchema, handler, serverOptions);

		let client = new Client(async (m: Message, s: Serializer) => {
			let req = s.serialize(m);
			let res = await server.process(req);
			return s.deserialize(res);
		}, new ClientOptions());

		result = {
			schemaSource: 'demo',
			client: client,
			showInternalApi: showInternalApi,
			readonlyEditor: true
		};
	} else {
		result = {
			schemaSource: 'unknown',
			client: undefined
		};
	}

	if (result.client !== undefined) {
		console.log(`Getting schema from ${schemaSource}`);
		const schemaPseudoJson: Promise<any[]> = result.client
			.request(new Message({}, { 'fn.api_': {} }))
			.then((schemaResponse) => schemaResponse.body['Ok_']['api'])
			.catch((e) => {
				console.log(`Failed to get schema: ${e}`);
			});

		const finalFullTelepactSchemaRef = schemaPseudoJson.then((e) =>
			TelepactSchema.fromJson(JSON.stringify(e, null, 2))
		);

		const filteredSchemaPseudoJson = schemaPseudoJson.then((e) =>
			e.filter((item) => {
				if (result.showInternalApi) {
					return true;
				} else {
					if (
						typeof item === 'object' &&
						Object.keys(item).find((i) => i.endsWith('_')) !== undefined
					) {
						return false;
					} else {
						return true;
					}
				}
			})
		);

		const formattedSchemaDraft = filteredSchemaPseudoJson.then((e) => {
			console.log(`Successfully got schema from ${schemaSource}`);
			let filteredJson = JSON.stringify(e, null, 2);
			return prettier.format(filteredJson, {
				parser: 'telepact-parse',
				printWidth: 78,
				proseWrap: 'always',
				plugins: [babelPlugin, estreePlugin, markdownPlugin, telepactPlugin]
			});
		});

		return {
			...result,
			fullTelepactSchemaRef: finalFullTelepactSchemaRef,
			filteredSchemaPseudoJson: filteredSchemaPseudoJson,
			schemaDraft: formattedSchemaDraft,
			authManaged: authManaged
		};
	} else {
		return {
			...result,
			authManaged: authManaged
		};
	}
};
