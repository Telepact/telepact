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

import prettier from 'prettier/standalone';
import markdownPlugin from 'prettier/plugins/markdown';
import estreePlugin from 'prettier/plugins/estree';
import babelPlugin from 'prettier/plugins/babel';

import telepactPlugin from './prettier-plugin-telepact/index.esm.js';
import demoSchemaPseudoJson from '../demo.telepact.json';

import {
	Client,
	ClientOptions,
	Message,
	MockServer,
	MockServerOptions,
	MockTelepactSchema,
	Serializer,
	Server,
	ServerOptions,
	TelepactSchema
} from './telepact/index.esm.js';

export type ProtocolOption = 'http' | 'ws';
export type SchemaSourceKind = 'draft' | 'http' | 'ws' | 'demo' | 'unknown';

export type LoadedConsoleData = {
	client?: Client;
	schemaSource: SchemaSourceKind;
	schemaProtocol?: ProtocolOption;
	showInternalApi: boolean;
	readonlyEditor: boolean;
	filteredSchemaPseudoJson?: any[];
	telepactSchema?: TelepactSchema;
	schemaDraft?: string;
	authManaged: boolean;
};

declare global {
	interface Window {
		overrideAuthHeader?: (
			schemaSource: string,
			next: (newAuthHeader: Record<string, object>) => Promise<Message>
		) => Promise<Message>;
		overrideDefaultSchema?: () => string;
	}
}

function inferProtocolFromUrl(value: string): ProtocolOption {
	const lowerValue = value.toLowerCase();
	if (lowerValue.startsWith('ws://') || lowerValue.startsWith('wss://')) {
		return 'ws';
	}
	return 'http';
}

export async function loadConsoleData(url: URL): Promise<LoadedConsoleData> {
	let schemaSource = (url.searchParams.get('s') ?? '').trim();
	const showInternalApi = url.searchParams.get('i') === '1';

	const schemaProtocolParam = url.searchParams.get('p');
	const normalizedProtocol =
		schemaProtocolParam === 'http' || schemaProtocolParam === 'ws' ? schemaProtocolParam : undefined;

	const lowerSchemaSource = schemaSource.toLowerCase();
	const inferredProtocol =
		lowerSchemaSource.startsWith('ws://') || lowerSchemaSource.startsWith('wss://')
			? 'ws'
			: lowerSchemaSource.startsWith('http://') || lowerSchemaSource.startsWith('https://')
				? 'http'
				: undefined;

	const schemaProtocol = normalizedProtocol ?? inferredProtocol;

	const authManaged = typeof window.overrideAuthHeader === 'function';

	let client: Client | undefined;
	let schemaSourceKind: SchemaSourceKind = 'unknown';
	let readonlyEditor = true;

	if (schemaSource === '') {
		const defaultSchema = typeof window.overrideDefaultSchema === 'function'
			? window.overrideDefaultSchema()
			: '[{"///": "No schema loaded.\\n\\nTry [editing the schema](/?v=ds), or loading a schema from a live running Telepact server by entering a URL in the `Live URL` text box.", "info.Example":{}}]';

		const schemaDraft = url.searchParams.get('sd') ?? defaultSchema;

		const telepactSchema = MockTelepactSchema.fromJson(schemaDraft);

		const mockServerOptions = new MockServerOptions();
		mockServerOptions.generatedCollectionLengthMin = 2;
		mockServerOptions.randomizeOptionalFieldGeneration = false;
		mockServerOptions.onError = (e) => console.log(e);
		const mockServer = new MockServer(telepactSchema, mockServerOptions);

		client = new Client(async (m: Message, s: Serializer) => {
			const req = s.serialize(m);
			const res = await mockServer.process(req);
			return s.deserialize(res.bytes);
		}, new ClientOptions());

		schemaSourceKind = 'draft';
		readonlyEditor = false;
	} else if (schemaSource === 'demo') {
		const telepactSchema = TelepactSchema.fromJson(JSON.stringify(demoSchemaPseudoJson));

		const serverOptions = new ServerOptions();
		serverOptions.authRequired = false;
		serverOptions.onError = (e) => console.log(e);

		const handler = async (m: Message) => {
			if (m.getBodyTarget() !== 'fn.compute') {
				throw new Error('Not implemented');
			}

			const args = m.getBodyPayload();
			const x = args['x']['Constant']['value'];
			const y = args['y']['Constant']['value'];
			const op = args['op'];
			const opKey = Object.keys(op)[0];

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
		};

		const server = new Server(telepactSchema, handler, serverOptions);

		client = new Client(async (m: Message, s: Serializer) => {
			const req = s.serialize(m);
			const res = await server.process(req);
			return s.deserialize(res.bytes);
		}, new ClientOptions());

		schemaSourceKind = 'demo';
	} else if (schemaProtocol === 'http') {
		client = new Client(async (m: Message, s: Serializer) => {
			const maybeOverrideAuthHeader = async (
				newAuthHeader: Record<string, object> | undefined,
				next: () => Promise<Message>
			) => {
				if (newAuthHeader !== undefined) {
					m.headers['@auth_'] = newAuthHeader;
				}

				return next();
			};

			const finish = async () => {
				const req = s.serialize(m);
				const res = await fetch(schemaSource, { method: 'POST', body: req });
				const buf = await res.arrayBuffer();
				const responseBytes = new Uint8Array(buf);
				return s.deserialize(responseBytes);
			};

			const fn = m.getBodyTarget();

			if (fn.endsWith('_') || window.overrideAuthHeader === undefined) {
				return maybeOverrideAuthHeader(undefined, finish);
			}

			return window.overrideAuthHeader(schemaSource, (a) => maybeOverrideAuthHeader(a, finish));
		}, new ClientOptions());

		schemaSourceKind = 'http';
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
			if (data instanceof ArrayBuffer) return new Uint8Array(data);
			if (data instanceof Blob) return new Uint8Array(await data.arrayBuffer());
			if (typeof data === 'string') return new TextEncoder().encode(data);
			if (ArrayBuffer.isView(data)) {
				const view = data as ArrayBufferView;
				return new Uint8Array(view.buffer, view.byteOffset, view.byteLength);
			}
			throw new Error('Unsupported WebSocket payload type');
		};

		const ensureSocket = async () => {
			if (socket && socket.readyState === WebSocket.OPEN) return;
			if (connecting) return connecting;

			const ws = new WebSocket(schemaSource);
			ws.binaryType = 'arraybuffer';
			socket = ws;
			let ready = false;

			const handleMessage = async (event: MessageEvent) => {
				if (ws !== socket) return;
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
				if (ws !== socket) return;
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

			const handleError = () => {
				if (ws !== socket) return;
				const error = new Error('WebSocket error');
				failPending(error);
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
					cleanup();
					ready = true;
					resolve();
				};

				const handleConnectError = () => {
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
					reject(err instanceof Error ? err : new Error('Failed to send message over WebSocket'));
				}
			});
		};

		client = new Client(async (m: Message, s: Serializer) => {
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
			}

			return window.overrideAuthHeader(schemaSource, (a) => maybeOverrideAuthHeader(a, finish));
		}, new ClientOptions());

		schemaSourceKind = 'ws';
	} else {
		return {
			schemaSource: 'unknown',
			showInternalApi,
			readonlyEditor: true,
			authManaged
		};
	}

	if (!client) {
		return { schemaSource: 'unknown', showInternalApi, readonlyEditor: true, authManaged };
	}

	const schemaResponse = await client.request(new Message({}, { 'fn.api_': {} }));
	const schemaPseudoJson = schemaResponse?.body?.Ok_?.api;

	if (!Array.isArray(schemaPseudoJson)) {
		throw new Error('Failed to get schema from server.');
	}

	const telepactSchema = TelepactSchema.fromJson(JSON.stringify(schemaPseudoJson, null, 2));

	const filteredSchemaPseudoJson = schemaPseudoJson.filter((item) => {
		if (showInternalApi) return true;
		if (typeof item === 'object' && Object.keys(item).find((i) => i.endsWith('_')) !== undefined) {
			return false;
		}
		return true;
	});

	const filteredJson = JSON.stringify(filteredSchemaPseudoJson, null, 2);
	const schemaDraft = (
		await prettier.format(filteredJson, {
			parser: 'telepact-parse',
			printWidth: 78,
			proseWrap: 'always',
			plugins: [babelPlugin, estreePlugin, markdownPlugin, telepactPlugin]
		})
	).trimEnd();

	return {
		client,
		schemaSource: schemaSourceKind,
		schemaProtocol: schemaSourceKind === 'http' || schemaSourceKind === 'ws' ? schemaSourceKind : undefined,
		showInternalApi,
		readonlyEditor,
		filteredSchemaPseudoJson,
		telepactSchema,
		schemaDraft,
		authManaged
	};
}
