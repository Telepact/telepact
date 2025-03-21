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

export const ssr = false;
export const prerender = true;

declare global {
	interface Window {
		getAuthHeader: () => Promise<Record<string, object>>;
	}
}

export const load: LayoutLoad = async ({ url, params, route, fetch }) => {
	console.log('layout load');
	let schemaSource = url.searchParams.get('s') ?? '';
	let showInternalApi = url.searchParams.get('i') === '1';

	const getAuthHeader = window.getAuthHeader;
	const authManaged = getAuthHeader !== undefined;

	console.log(`authManaged ${authManaged}`);

	let result: {
		client?: Client;
		showInternalApi?: boolean;
		readonlyEditor?: boolean;
		schemaSource?: string;
	} = {};
	if (schemaSource === '') {
		let schemaDraft = (url.searchParams.get('sd') as string) ?? '[{"info.Example":{}}]';

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
			if (getAuthHeader !== undefined) {
				let authHeader = await getAuthHeader();
				m.headers['auth_'] = authHeader;
			}

			let req = s.serialize(m);
			let res = await fetch(schemaSource, {
				method: 'POST',
				body: req
			});
			let buf = await res.arrayBuffer();
			let responseBytes = new Uint8Array(buf);
			return s.deserialize(responseBytes);
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
