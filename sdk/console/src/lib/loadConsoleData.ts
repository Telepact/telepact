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
		schemaProtocolParam === 'http' || schemaProtocolParam === 'ws'
			? schemaProtocolParam
			: undefined;

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
		const defaultSchema =
			typeof window.overrideDefaultSchema === 'function'
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
		serverOptions.onError = (e) => console.log(e);

		const userVariables = new Map<string, Map<string, number>>();
		const userEvaluations = new Map<string, any[]>();
		const sessionTokens = new Map<string, string>();
		const usernamesByToken = new Map<string, string>();

		const getUserVariables = (username: string): Map<string, number> => {
			let variables = userVariables.get(username);
			if (!variables) {
				variables = new Map<string, number>();
				userVariables.set(username, variables);
			}
			return variables;
		};

		const getUserEvaluations = (username: string): any[] => {
			let evaluations = userEvaluations.get(username);
			if (!evaluations) {
				evaluations = [];
				userEvaluations.set(username, evaluations);
			}
			return evaluations;
		};

		const getUsername = (m: Message, requireSession = false): string | undefined => {
			const auth = m.headers['@auth_'];
			if (!auth || typeof auth !== 'object') return undefined;
			if ('Ephemeral' in auth) {
				if (requireSession) return undefined;
				return auth.Ephemeral.username as string;
			}
			if ('Session' in auth) {
				return usernamesByToken.get(auth.Session.token as string);
			}
			return undefined;
		};

		const recordEvaluation = (
			username: string,
			expression: Record<string, any>,
			result: number,
			successful: boolean
		) => {
			getUserEvaluations(username).push({
				expression,
				result,
				timestamp: Math.floor(Date.now() / 1000),
				successful
			});
		};

		const evaluateExpression = (
			expression: Record<string, any>,
			variables: Map<string, number>
		): { result: number; unknownVariables: string[]; divideByZero: boolean } => {
			const [kind, payload] = Object.entries(expression)[0] as [string, Record<string, any>];

			if (kind === 'Constant') {
				return {
					result: payload.value as number,
					unknownVariables: [],
					divideByZero: false
				};
			}

			if (kind === 'Variable') {
				const variableName = payload.name as string;
				const value = variables.get(variableName);
				if (value === undefined) {
					return { result: 0, unknownVariables: [variableName], divideByZero: false };
				}
				return { result: value, unknownVariables: [], divideByZero: false };
			}

			const left = evaluateExpression(payload.left as Record<string, any>, variables);
			const right = evaluateExpression(payload.right as Record<string, any>, variables);
			const unknownVariables = [
				...new Set([...left.unknownVariables, ...right.unknownVariables])
			];
			if (unknownVariables.length > 0) {
				return { result: 0, unknownVariables, divideByZero: false };
			}
			if (left.divideByZero || right.divideByZero) {
				return { result: 0, unknownVariables: [], divideByZero: true };
			}

			switch (kind) {
				case 'Add':
					return {
						result: left.result + right.result,
						unknownVariables: [],
						divideByZero: false
					};
				case 'Sub':
					return {
						result: left.result - right.result,
						unknownVariables: [],
						divideByZero: false
					};
				case 'Mul':
					return {
						result: left.result * right.result,
						unknownVariables: [],
						divideByZero: false
					};
				case 'Div':
					if (right.result === 0) {
						return { result: 0, unknownVariables: [], divideByZero: true };
					}
					return {
						result: left.result / right.result,
						unknownVariables: [],
						divideByZero: false
					};
				default:
					throw new Error('Invalid expression');
			}
		};

		const handler = async (m: Message) => {
			const functionName = m.getBodyTarget();
			const args = m.getBodyPayload();

			if (functionName === 'fn.add') {
				return new Message(
					{},
					{ Ok_: { result: (args.x as number) + (args.y as number) } }
				);
			}

			if (functionName === 'fn.login') {
				const username = args.username as string;
				if (sessionTokens.has(username)) {
					return new Message({}, { ErrorUsernameAlreadyInUse: {} });
				}
				const token =
					typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
						? crypto.randomUUID()
						: `${username}-${Date.now()}`;
				sessionTokens.set(username, token);
				usernamesByToken.set(token, username);
				return new Message({}, { Ok_: { token } });
			}

			if (functionName === 'fn.logout') {
				const username = getUsername(m, true);
				if (!username) {
					return new Message(
						{},
						{
							ErrorUnauthenticated_: {
								'message!': 'Valid authentication is required.'
							}
						}
					);
				}
				if (username !== (args.username as string)) {
					return new Message(
						{},
						{
							ErrorUnauthorized_: {
								'message!':
									'Session authentication must match the requested username.'
							}
						}
					);
				}
				const token = sessionTokens.get(username);
				if (token) {
					sessionTokens.delete(username);
					usernamesByToken.delete(token);
				}
				userVariables.delete(username);
				userEvaluations.delete(username);
				return new Message({}, { Ok_: {} });
			}

			const username = getUsername(m);
			if (!username) {
				return new Message(
					{},
					{ ErrorUnauthenticated_: { 'message!': 'Valid authentication is required.' } }
				);
			}

			switch (functionName) {
				case 'fn.saveVariable':
					getUserVariables(username).set(args.name as string, args.value as number);
					return new Message({}, { Ok_: {} });
				case 'fn.saveVariables':
					for (const [name, value] of Object.entries(
						args.variables as Record<string, number>
					)) {
						getUserVariables(username).set(name, value);
					}
					return new Message({}, { Ok_: {} });
				case 'fn.getVariable': {
					const variableName = args.name as string;
					const value = getUserVariables(username).get(variableName);
					return new Message(
						{},
						value === undefined
							? { Ok_: {} }
							: { Ok_: { 'variable!': { name: variableName, value } } }
					);
				}
				case 'fn.getVariables':
					return new Message(
						{},
						{
							Ok_: {
								variables: [...getUserVariables(username).entries()]
									.sort(([left], [right]) => left.localeCompare(right))
									.map(([name, value]) => ({ name, value }))
							}
						}
					);
				case 'fn.deleteVariable':
					getUserVariables(username).delete(args.name as string);
					return new Message({}, { Ok_: {} });
				case 'fn.deleteVariables':
					for (const name of args.names as string[]) {
						getUserVariables(username).delete(name);
					}
					return new Message({}, { Ok_: {} });
				case 'fn.evaluate': {
					const expression = args.expression as Record<string, any>;
					const evaluation = evaluateExpression(expression, getUserVariables(username));
					if (evaluation.unknownVariables.length > 0) {
						recordEvaluation(username, expression, 0, false);
						return new Message(
							{},
							{
								ErrorUnknownVariables: {
									unknownVariables: evaluation.unknownVariables
								}
							}
						);
					}
					if (evaluation.divideByZero) {
						recordEvaluation(username, expression, 0, false);
						return new Message({}, { ErrorCannotDivideByZero: {} });
					}
					recordEvaluation(username, expression, evaluation.result, true);
					return new Message(
						{},
						{
							Ok_: {
								result: evaluation.result,
								saveResult: {
									'fn.saveVariable': { name: 'result', value: evaluation.result }
								}
							}
						}
					);
				}
				case 'fn.getPaperTape': {
					const limit = args['limit!'] as number | undefined;
					const tape = [...getUserEvaluations(username)].reverse();
					return new Message(
						{},
						{ Ok_: { tape: limit === undefined ? tape : tape.slice(0, limit) } }
					);
				}
				default:
					throw new Error('Not implemented');
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

			return window.overrideAuthHeader(schemaSource, (a) =>
				maybeOverrideAuthHeader(a, finish)
			);
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
					console.warn(
						'Received unexpected WebSocket message with no pending Telepact request.'
					);
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
					const error = new Error(
						`WebSocket closed before ready (code ${event.code}${reason})`
					);
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
					reject(
						err instanceof Error
							? err
							: new Error('Failed to send message over WebSocket')
					);
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

			return window.overrideAuthHeader(schemaSource, (a) =>
				maybeOverrideAuthHeader(a, finish)
			);
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

	const apiRequest = showInternalApi ? { 'includeInternal!': true } : {};
	const schemaResponse = await client.request(new Message({}, { 'fn.api_': apiRequest }));
	const schemaPseudoJson = schemaResponse?.body?.Ok_?.api;

	if (!Array.isArray(schemaPseudoJson)) {
		throw new Error('Failed to get schema from server.');
	}

	const telepactSchema = TelepactSchema.fromJson(JSON.stringify(schemaPseudoJson, null, 2));

	const filteredSchemaPseudoJson = schemaPseudoJson.filter((item) => {
		if (showInternalApi) return true;
		if (
			typeof item === 'object' &&
			Object.keys(item).find((i) => i.endsWith('_')) !== undefined
		) {
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
		schemaProtocol:
			schemaSourceKind === 'http' || schemaSourceKind === 'ws' ? schemaSourceKind : undefined,
		showInternalApi,
		readonlyEditor,
		filteredSchemaPseudoJson,
		telepactSchema,
		schemaDraft,
		authManaged
	};
}
