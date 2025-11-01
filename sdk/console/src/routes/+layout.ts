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
	let schemaSource = (url.searchParams.get('s') ?? '').trim();
	let showInternalApi = url.searchParams.get('i') === '1';
	const schemaProtocolParam = url.searchParams.get('p');
	const normalizedProtocol =
		schemaProtocolParam === 'http' || schemaProtocolParam === 'ws'
			? schemaProtocolParam
			: undefined;
	const lowerSchemaSource = schemaSource.toLowerCase();
	const inferredProtocol = lowerSchemaSource.startsWith('ws://') || lowerSchemaSource.startsWith('wss://')
		? 'ws'
		: lowerSchemaSource.startsWith('http://') || lowerSchemaSource.startsWith('https://')
			? 'http'
			: undefined;
	const schemaProtocol = normalizedProtocol ?? inferredProtocol;

	const authManaged = window.overrideAuthHeader !== undefined;
	const overrideDefaultSchema = window.overrideDefaultSchema !== undefined;

	console.log(`authManaged ${authManaged}`);
	console.log(`overrideDefaultSchema ${overrideDefaultSchema}`);

	let result: {
		client?: Client;
		showInternalApi?: boolean;
		readonlyEditor?: boolean;
		schemaSource?: string;
		schemaProtocol?: 'http' | 'ws';
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
			return s.deserialize(res.bytes);
		}, new ClientOptions());

		result = {
			schemaSource: 'draft',
			client: mockClient,
			showInternalApi: showInternalApi,
			readonlyEditor: false
		};
	} else if (schemaProtocol === 'http') {
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
			schemaProtocol: 'http',
			client: client,
			showInternalApi: showInternalApi,
			readonlyEditor: true
		};
	} else if (schemaProtocol === 'ws') {
		type PendingRequest = {
			resolve: (value: Message) => void;
			reject: (reason?: unknown) => void;
			serializer: Serializer;
		};

		const pendingRequests: PendingRequest[] = [];
		let socket: WebSocket | null = null;
		let connecting: Promise<void> | null = null;

		const failPending = (error: Error) => {
			while (pendingRequests.length > 0) {
				pendingRequests.shift()?.reject(error);
			}
		};

		const incomingDataToBytes = async (data: unknown): Promise<Uint8Array> => {
			if (data instanceof ArrayBuffer) {
				return new Uint8Array(data);
			}
			if (data instanceof Blob) {
				const buffer = await data.arrayBuffer();
				return new Uint8Array(buffer);
			}
			if (typeof data === 'string') {
				return new TextEncoder().encode(data);
			}
			if (ArrayBuffer.isView(data)) {
				const view = data as ArrayBufferView;
				return new Uint8Array(view.buffer, view.byteOffset, view.byteLength);
			}
			throw new Error('Unsupported WebSocket payload type');
		};

		const ensureSocket = async () => {
			if (socket && socket.readyState === WebSocket.OPEN) {
				return;
			}

			if (connecting) {
				return connecting;
			}

			const ws = new WebSocket(schemaSource);
			ws.binaryType = 'arraybuffer';
			socket = ws;
			let ready = false;

			const handleMessage = async (event: MessageEvent) => {
				if (ws !== socket) {
					return;
				}
				const pending = pendingRequests.shift();
				if (!pending) {
					console.warn('Received unexpected WebSocket message with no pending Telepact request.');
					return;
				}
				try {
					const payload = await incomingDataToBytes(event.data);
					const response = pending.serializer.deserialize(payload);
					pending.resolve(response);
				} catch (err) {
					pending.reject(err);
				}
			};

			const handleClose = (event: CloseEvent) => {
				if (ws !== socket) {
					return;
				}
				ws.removeEventListener('message', handleMessage);
				ws.removeEventListener('close', handleClose);
				ws.removeEventListener('error', handleError);
				socket = null;
				const reason = event.reason ? ` ${event.reason}` : '';
				const error = new Error(`WebSocket closed with code ${event.code}.${reason}`);
				if (ready) {
					failPending(error);
				}
			};

			const handleError = (_event: Event) => {
				if (ws !== socket) {
					return;
				}
				if (!ready) {
					return;
				}
				const error = new Error('WebSocket encountered an error');
				failPending(error);
				ws.close();
			};

			ws.addEventListener('message', handleMessage);
			ws.addEventListener('close', handleClose);
			ws.addEventListener('error', handleError);

			connecting = new Promise<void>((resolve, reject) => {
				const cleanup = () => {
					ws.removeEventListener('open', handleOpen);
					ws.removeEventListener('error', handleConnectError);
					ws.removeEventListener('close', handleConnectClose);
				};

				const handleOpen = () => {
					if (ws !== socket) {
						cleanup();
						return;
					}
					ready = true;
					cleanup();
					resolve();
				};

				const handleConnectError = (_event: Event) => {
					cleanup();
					if (ws === socket) {
						ws.removeEventListener('message', handleMessage);
						ws.removeEventListener('close', handleClose);
						ws.removeEventListener('error', handleError);
						socket = null;
					}
					const error = new Error('Failed to establish WebSocket connection');
					reject(error);
					failPending(error);
				};

				const handleConnectClose = (event: CloseEvent) => {
					cleanup();
					if (ws === socket) {
						ws.removeEventListener('message', handleMessage);
						ws.removeEventListener('close', handleClose);
						ws.removeEventListener('error', handleError);
						socket = null;
					}
					const reason = event.reason ? `: ${event.reason}` : '';
					const error = new Error(`WebSocket closed before ready (code ${event.code}${reason})`);
					reject(error);
					failPending(error);
				};

				ws.addEventListener('open', handleOpen, { once: true });
				ws.addEventListener('error', handleConnectError, { once: true });
				ws.addEventListener('close', handleConnectClose, { once: true });
			}).finally(() => {
				connecting = null;
			});

			return connecting;
		};

		const sendOverSocket = async (message: Message, serializer: Serializer) => {
			await ensureSocket();
			const ws = socket;
			if (!ws || ws.readyState !== WebSocket.OPEN) {
				throw new Error('WebSocket is not open');
			}

			const payload = serializer.serialize(message);

			return new Promise<Message>((resolve, reject) => {
				const pending: PendingRequest = { resolve, reject, serializer };
				pendingRequests.push(pending);
				try {
					ws.send(payload);
				} catch (err) {
					pendingRequests.pop();
					if (err instanceof Error) {
						reject(err);
					} else {
						reject(new Error('Failed to send message over WebSocket'));
					}
				}
			});
		};

		let client = new Client(async (m: Message, s: Serializer) => {
			const maybeOverrideAuthHeader = async (
				newAuthHeader: Record<string, object> | undefined,
				next: () => Promise<Message>
			) => {
				if (newAuthHeader !== undefined) {
					m.headers['@auth_'] = newAuthHeader;
				}

				return next();
			};

			const finish = () => sendOverSocket(m, s);

			const fn = m.getBodyTarget();

			if (fn.endsWith('_') || window.overrideAuthHeader === undefined) {
				return maybeOverrideAuthHeader(undefined, finish);
			} else {
				return window.overrideAuthHeader(schemaSource, (a) => maybeOverrideAuthHeader(a, finish));
			}
		}, new ClientOptions());

		result = {
			schemaSource: 'ws',
			schemaProtocol: 'ws',
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
			return s.deserialize(res.bytes);
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
