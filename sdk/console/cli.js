#!/usr/bin/env node

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

import express from 'express';
import http from 'http';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { Command } from 'commander';
import { createProxyMiddleware } from 'http-proxy-middleware';

const program = new Command();

program
	.description(
		'The Telepact Console is a web-based interface for inspecting and testing Telepact APIs.'
	)
	.option('-p, --port <number>', 'port number', process.env.PORT || '4173')
	.option('-d, --debug', 'enable additional logging', false)
	.parse(process.argv);

const options = program.opts();
const port = parseInt(options.port, 10);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PORT = port;
const BUILD_DIR = resolve(__dirname, 'build');
const PROXY_HTTP_PATH = '/__telepact_proxy/http';
const PROXY_WS_PATH = '/__telepact_proxy/ws';
const proxyTargetSymbol = Symbol('telepactProxyTarget');

const app = express();

function parseTargetUrl(rawValue, protocols) {
	if (typeof rawValue !== 'string') {
		return null;
	}

	const value = rawValue.trim();
	if (value === '') {
		return null;
	}

	try {
		const targetUrl = new URL(value);
		if (!protocols.includes(targetUrl.protocol)) {
			return null;
		}
		return targetUrl;
	} catch {
		return null;
	}
}

function getTargetUrl(req, protocols) {
	return parseTargetUrl(req.query.target, protocols);
}

function getProxyPath(req) {
	const targetUrl = req[proxyTargetSymbol];
	const path = `${targetUrl.pathname}${targetUrl.search}`;
	return path === '' ? '/' : path;
}

function setProxyTarget(req, res, next, protocols) {
	const targetUrl = getTargetUrl(req, protocols);

	if (!targetUrl) {
		res.status(400).send('Invalid target URL');
		return;
	}

	req[proxyTargetSymbol] = targetUrl;

	if (options.debug) {
		console.log(`Proxying ${req.method} ${req.originalUrl} -> ${targetUrl.toString()}`);
	}

	next();
}

function writeUpgradeError(socket, statusCode, message) {
	socket.write(
		`HTTP/1.1 ${statusCode} ${message}\r\n` +
			'Connection: close\r\n' +
			'Content-Type: text/plain\r\n' +
			`\r\n${message}`
	);
	socket.destroy();
}

const httpProxy = createProxyMiddleware({
	target: 'http://127.0.0.1',
	changeOrigin: true,
	router: (req) => req[proxyTargetSymbol].origin,
	pathRewrite: (_, req) => getProxyPath(req),
	on: {
		error(err, req, res) {
			if (options.debug) {
				console.error('HTTP proxy failed:', err);
			}
			if (!res.headersSent) {
				res.writeHead(502, { 'Content-Type': 'text/plain' });
			}
			res.end(`Proxy request failed: ${err.message}`);
		}
	}
});

const wsProxy = createProxyMiddleware({
	target: 'ws://127.0.0.1',
	changeOrigin: true,
	ws: true,
	router: (req) => req[proxyTargetSymbol].origin,
	pathRewrite: (_, req) => getProxyPath(req),
	on: {
		error(err) {
			if (options.debug) {
				console.error('WebSocket proxy failed:', err);
			}
		}
	}
});

app.get('/override.js', (_req, res) => {
	res.type('application/javascript');
	res.setHeader('Cache-Control', 'no-store');
	res.send(
		`window.telepactConsoleProxy = ${JSON.stringify({
			httpPath: PROXY_HTTP_PATH,
			wsPath: PROXY_WS_PATH
		})};\n`
	);
});

app.use(PROXY_HTTP_PATH, (req, res, next) => setProxyTarget(req, res, next, ['http:', 'https:']));
app.use(PROXY_HTTP_PATH, httpProxy);

app.use(
	'/',
	express.static(BUILD_DIR, {
		fallthrough: false
	})
);

app.use((err, req, res, next) => {
	if (err.code === 'ENOENT') {
		if (options.debug) {
			console.error(`File not found: ${req.path}`);
		}
		res.status(404).send('Not Found');
	} else {
		next(err);
	}
});

const server = http.createServer(app);

server.on('upgrade', (req, socket, head) => {
	const requestUrl = req.url ?? '';
	if (!requestUrl.startsWith(PROXY_WS_PATH)) {
		return;
	}

	const host = req.headers.host ?? `localhost:${PORT}`;
	const parsedUrl = new URL(requestUrl, `http://${host}`);
	const targetUrl = parseTargetUrl(parsedUrl.searchParams.get('target'), ['ws:', 'wss:']);

	if (!targetUrl) {
		writeUpgradeError(socket, 400, 'Invalid target URL');
		return;
	}

	req[proxyTargetSymbol] = targetUrl;

	if (options.debug) {
		console.log(`Proxying WS ${requestUrl} -> ${targetUrl.toString()}`);
	}

	wsProxy.upgrade(req, socket, head);
});

server.listen(PORT, () => {
	console.log(`Server running. Access at http://localhost:${PORT}`);
});
