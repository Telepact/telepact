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

import { useEffect, useMemo, useRef, useState, type FocusEvent, type FormEvent, type KeyboardEvent } from 'react';
import * as monaco from 'monaco-editor';
import 'monaco-editor/esm/vs/language/json/monaco.contribution';

import DocCard from './components/DocCard';
import MonacoEditor, { type MonacoEditorHandle } from './components/MonacoEditor';
import Tooltip from './components/Tooltip';
import MockIcon from './components/icons/MockIcon';
import TerminalIcon from './components/icons/TerminalIcon';

import {
	genExample,
	minifyJson,
	parseTelepactSchema,
	unMinifyJson,
	type TypeData
} from './lib/console';
import { createJsonSchema } from './lib/jsonSchema';
import { ensureTelepactJsonLinksRegistered, setTelepactRequestLinkHandler } from './lib/monacoLinks';
import { loadConsoleData, type ProtocolOption, type SchemaSourceKind } from './lib/loadConsoleData';
import { submitRequest } from './lib/submitRequest';
import { jsonSchema } from './lib/telepact/index.esm.js';

type View = 's' | 'd' | 't' | 'r' | 'm';

type AsyncState<T> =
	| { status: 'idle' }
	| { status: 'loading' }
	| { status: 'ready'; value: T }
	| { status: 'error'; error: unknown };

const monacoLanguagesWithJson = monaco.languages as typeof monaco.languages & {
	json: {
		jsonDefaults: {
			setDiagnosticsOptions: (options: unknown) => void;
		};
	};
};

function inferProtocolFromUrl(value: string): ProtocolOption {
	const lowerValue = value.toLowerCase();
	if (lowerValue.startsWith('ws://') || lowerValue.startsWith('wss://')) {
		return 'ws';
	}
	return 'http';
}

function validateSourceUrl(value: string, protocol: ProtocolOption): string | null {
	const trimmed = value.trim();
	if (trimmed === '') {
		return null;
	}

	if (/%(?![0-9A-Fa-f]{2})/.test(trimmed)) {
		return 'Enter a valid URL or relative path';
	}

	const allowedProtocols = protocol === 'ws' ? ['ws:', 'wss:'] : ['http:', 'https:'];

	try {
		const absolute = new URL(trimmed);
		if (allowedProtocols.includes(absolute.protocol.toLowerCase())) {
			return null;
		}
		return protocol === 'ws'
			? 'URL must match selected scheme (ws:// or wss:// or a relative path)'
			: 'URL must match selected scheme (http:// or https:// or a relative path)';
	} catch {
		try {
			new URL(trimmed, 'http://placeholder.local');
			return null;
		} catch {
			return 'Enter a valid URL or relative path';
		}
	}
}

function getSectionClass(activeViews: string, v: View, activeViewsLength: number) {
	const width = activeViewsLength === 1 ? 'w-full' : 'w-1/2';
	if (v === 's') {
		return 'justify-start ' + width;
	}
	if (activeViews.includes('s')) {
		return 'justify-end ' + width;
	}
	if (v === 'd') {
		return 'justify-start ' + width;
	}
	if (activeViews.includes('d')) {
		return 'justify-end ' + width;
	}
	if (v === 'r') {
		return 'justify-end ' + width;
	}
	if (activeViews.includes('r')) {
		return 'justify-start ' + width;
	}
	if (v === 't' && activeViews.includes('m')) {
		return 'justify-end ' + width;
	}
	if (v === 'm' && activeViews.includes('t')) {
		return 'justify-start ' + width;
	}
	return 'justify-end ' + width;
}

export default function App() {
	const [url, setUrl] = useState(() => new URL(window.location.href));

	const navigate = (relative: string) => {
		const nextUrl = new URL(relative, window.location.href);
		window.history.pushState({}, '', nextUrl);
		setUrl(nextUrl);
		if (nextUrl.hash) {
			const id = nextUrl.hash.replace('#', '');
			setTimeout(() => {
				document.getElementById(id)?.scrollIntoView();
			}, 0);
		}
	};

	const [responsePromise, setResponsePromise] = useState<Promise<string> | null>(null);
	const [responseState, setResponseState] = useState<AsyncState<string>>({ status: 'idle' });

	useEffect(() => {
		const onPopState = () => {
			setUrl(new URL(window.location.href));
			setResponsePromise(null);
		};
		const onHashChange = () => setUrl(new URL(window.location.href));
		window.addEventListener('popstate', onPopState);
		window.addEventListener('hashchange', onHashChange);
		return () => {
			window.removeEventListener('popstate', onPopState);
			window.removeEventListener('hashchange', onHashChange);
		};
	}, []);

	useEffect(() => {
		if (!responsePromise) {
			setResponseState({ status: 'idle' });
			return;
		}

		let cancelled = false;
		setResponseState({ status: 'loading' });

		responsePromise.then(
			(value) => {
				if (cancelled) return;
				setResponseState({ status: 'ready', value });
			},
			(error) => {
				if (cancelled) return;
				setResponseState({ status: 'error', error });
			}
		);

		return () => {
			cancelled = true;
		};
	}, [responsePromise]);

	const schemaSourceParam = (url.searchParams.get('s') ?? '').trim();
	const schemaProtocolParam = url.searchParams.get('p') ?? '';
	const showInternalApiParam = url.searchParams.get('i') ?? '';
	const schemaDraftParam = url.searchParams.get('sd') ?? '';

	const loadKey = `${schemaSourceParam}|${schemaProtocolParam}|${showInternalApiParam}|${schemaDraftParam}`;

	const [loadState, setLoadState] = useState<AsyncState<Awaited<ReturnType<typeof loadConsoleData>>>>({
		status: 'loading'
	});

	useEffect(() => {
		let cancelled = false;
		setLoadState({ status: 'loading' });
		loadConsoleData(url)
			.then((data) => {
				if (cancelled) return;
				setLoadState({ status: 'ready', value: data });
			})
			.catch((error) => {
				if (cancelled) return;
				setLoadState({ status: 'error', error });
			});
		return () => {
			cancelled = true;
		};
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [loadKey]);

	const data = loadState.status === 'ready' ? loadState.value : null;
	const telepactSchema = data?.telepactSchema;
	const filteredSchemaPseudoJson = data?.filteredSchemaPseudoJson ?? [];
	const schemaDraft = data?.schemaDraft ?? '';
	const authManaged = data?.authManaged ?? false;
	const readonlyEditor = data?.readonlyEditor ?? true;
	const schemaSourceKind: SchemaSourceKind = data?.schemaSource ?? 'unknown';

	useEffect(() => {
		ensureTelepactJsonLinksRegistered();

		setTelepactRequestLinkHandler((requestBody) => {
			const requestJson = JSON.stringify([{}, requestBody], null, 2);
			const q = new URLSearchParams(url.searchParams.toString());
			q.set('r', minifyJson(requestJson, true));
			navigate(`?${q.toString()}`);
			setResponsePromise(null);
		});

		return () => setTelepactRequestLinkHandler(null);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [url.search]);

	useEffect(() => {
		if (!telepactSchema) return;

		const requestJsonSchema = createJsonSchema(telepactSchema);
		monacoLanguagesWithJson.json.jsonDefaults.setDiagnosticsOptions({
			schemas: [
				{
					uri: 'internal://server/jsonschema-telepact.json',
					fileMatch: ['schema.telepact.json'],
					schema: jsonSchema
				},
				{
					uri: 'internal://server/jsonschema-request.json',
					fileMatch: ['request.json'],
					schema: requestJsonSchema
				}
			]
		});
	}, [telepactSchema]);

	const selectedViews = url.searchParams.get('v') ?? 'd';
	const activeViews = selectedViews.substring(0, 2);
	const sortDocCardsAZ = url.searchParams.get('az') === '1';
	const exampleFn = url.searchParams.get('mf') ?? 'fn.ping_';
	const exampleHeaders = (url.searchParams.get('mh') ?? '')
		.split(',')
		.map((h) => h.trim())
		.filter((h) => h !== '');
	const requestParam = url.searchParams.get('r');

	const [sourceUrlInput, setSourceUrlInput] = useState(schemaSourceParam);
	useEffect(() => {
		setSourceUrlInput(schemaSourceParam);
	}, [schemaSourceParam]);

	const [sourceUrlProtocol, setSourceUrlProtocol] = useState<ProtocolOption>(() => {
		if (schemaProtocolParam === 'http' || schemaProtocolParam === 'ws') {
			return schemaProtocolParam;
		}
		return inferProtocolFromUrl(schemaSourceParam);
	});

	const urlError = useMemo(
		() => validateSourceUrl(sourceUrlInput, sourceUrlProtocol),
		[sourceUrlInput, sourceUrlProtocol]
	);

	const submitString = schemaSourceKind === 'draft' ? 'Submit (mock)' : 'Submit (live)';

	const [showDropdown, setShowDropdown] = useState(false);
	const [liveUrlActive, setLiveUrlActive] = useState(false);

	const handleSourceGet = (e: FormEvent) => {
		e.preventDefault();
		const trimmed = sourceUrlInput.trim();
		setSourceUrlInput(trimmed);
		const validationError = validateSourceUrl(trimmed, sourceUrlProtocol);
		if (validationError !== null) return;

		const q = new URLSearchParams(url.searchParams.toString());
		const existingS = q.get('s');

		if (existingS !== trimmed) {
			q.delete('mf');
			q.delete('mh');
			q.delete('r');
			q.set('v', 'd');
		}

		if (trimmed === '') {
			q.delete('s');
			q.delete('p');
		} else {
			q.set('s', trimmed);
			q.set('p', sourceUrlProtocol);
		}

		setShowDropdown(false);
		navigate(`?${q.toString()}`);
	};

	const toggleView = (v: View) => {
		let newViews: string;
		if (selectedViews.substring(0, 2).includes(v)) {
			newViews = selectedViews.replace(v, '');
		} else if (selectedViews.includes(v)) {
			const temp = selectedViews.replace(v, '');
			newViews = v + temp;
		} else {
			newViews = v + selectedViews;
		}

		const q = new URLSearchParams(url.searchParams.toString());
		q.set('v', newViews);
		navigate(`?${q.toString()}`);
	};

	const toggleShowInternalApi = () => {
		const q = new URLSearchParams(url.searchParams.toString());
		if (q.get('i') === '1') {
			q.delete('i');
		} else {
			q.set('i', '1');
		}
		navigate(`?${q.toString()}`);
	};

	const schemaEditor = useRef<MonacoEditorHandle | null>(null);
	const requestEditor = useRef<MonacoEditorHandle | null>(null);

	const handleSchemaSave = () => {
		const schemaText = schemaEditor.current?.getContent();
		if (!schemaText) return;
		const minifiedSchema = minifyJson(schemaText);
		const q = new URLSearchParams(url.searchParams.toString());
		q.set('s', '');
		q.set('sd', minifiedSchema);
		q.set('v', 'sd');
		navigate(`?${q.toString()}`);
	};

	const handleSubmit = () => {
		if ((schemaSourceKind === 'http' || schemaSourceKind === 'ws') && !sessionStorage.getItem('telepact-console:live-request-acknowledge')) {
			if (!confirm('You are about to submit a request to a live server.')) {
				return;
			}
			sessionStorage.setItem('telepact-console:live-request-acknowledge', 'true');
		}

		const requestText = requestEditor.current?.getContent();
		if (!requestText) return;

		const q = new URLSearchParams(url.searchParams.toString());
		q.set('v', 'tr');
		q.set('r', minifyJson(requestText, true));
		navigate(`?${q.toString()}`);

		if (!data?.client) return;
		setResponsePromise(submitRequest(data.client, requestText));
	};

	const [simulationSeed, setSimulationSeed] = useState(1);
	const [simulationState, setSimulationState] = useState<AsyncState<{ request: string; response: string }>>({
		status: 'idle'
	});

	useEffect(() => {
		if (!telepactSchema || !activeViews.includes('m')) {
			setSimulationState({ status: 'idle' });
			return;
		}

		let cancelled = false;
		setSimulationState({ status: 'loading' });
		genExample(exampleFn, exampleHeaders, telepactSchema).then(
			(value) => {
				if (cancelled) return;
				setSimulationState({ status: 'ready', value });
			},
			(error) => {
				if (cancelled) return;
				setSimulationState({ status: 'error', error });
			}
		);
		return () => {
			cancelled = true;
		};
	}, [telepactSchema, activeViews, exampleFn, exampleHeaders.join(','), simulationSeed]);

	const showInternalApi = data?.showInternalApi ?? false;

	const docEntries: TypeData[] = useMemo(() => {
		if (!telepactSchema) return [];
		const entries = parseTelepactSchema(filteredSchemaPseudoJson, telepactSchema, sortDocCardsAZ, showInternalApi);
		if (showInternalApi) return entries;
		return entries.filter((entry) => {
			const tokens = entry.name.split('.');
			const suffix = tokens[1] ?? '';
			return !suffix.endsWith('_');
		});
	}, [filteredSchemaPseudoJson, sortDocCardsAZ, showInternalApi, telepactSchema]);

	const simulationKey = `${simulationSeed}:${exampleFn}:${exampleHeaders.join(',')}`;

	const dropdownKeydown = (event: KeyboardEvent) => {
		if (event.key === 'Escape') {
			event.stopPropagation();
			setShowDropdown(false);
		}
	};

	const handleLiveUrlFocusOut = (event: FocusEvent) => {
		const currentTarget = event.currentTarget as HTMLElement | null;
		const relatedTarget = event.relatedTarget as Node | null;

		if (!currentTarget || !relatedTarget || !currentTarget.contains(relatedTarget)) {
			setLiveUrlActive(false);
			setShowDropdown(false);
		}
	};

	return (
		<div className="text-gray-800 dark:text-gray-200">
			<nav className="fixed top-0 z-10 h-16 w-full border-y border-slate-300 bg-slate-100 dark:border-slate-600 dark:bg-slate-800">
				<div className="flex h-full items-center px-4">
					<div className={`flex items-center ${liveUrlActive ? 'shrink-0 pr-4' : 'flex-1 min-w-0'}`}>
						<div className="flex items-center rounded-md py-2">
							<div className="text-sky-400">
								<img src="/favicon.svg" alt="Telepact logo" className="h-8 w-8" />
							</div>
							<h1 className="px-2 text-lg font-semibold text-gray-900 dark:text-gray-100">Telepact</h1>
						</div>
					</div>

					<div
						id="view-select"
						className={`flex shrink-0 content-center space-x-2 ${liveUrlActive ? 'ml-4 mr-auto justify-start' : 'mx-auto justify-center'}`}
					>
						<div className="inline-flex rounded-md">
							<Tooltip text="Schema">
								<button
									aria-label="Toggle Schema"
									aria-pressed={activeViews.includes('s')}
									onClick={() => toggleView('s')}
									className={`rounded-s-md p-2 ${activeViews.includes('s') ? 'bg-sky-700 text-cyan-300' : 'bg-slate-200 text-gray-800 dark:bg-slate-700 dark:text-gray-200'}`}
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										strokeWidth="1"
										stroke="currentColor"
										className="h-6 w-6"
									>
										<path d="M 2 22 L 5 16 L 19 2 L 22 5 L 8 19 L 2 22 M 5 16 L 8 19 M 19 8 L 16 5 M 17 4 L 20 7" />
									</svg>
								</button>
							</Tooltip>
							<Tooltip text="Documentation">
								<button
									aria-label="Toggle Documentation"
									aria-pressed={activeViews.includes('d')}
									onClick={() => toggleView('d')}
									className={`p-2 ${activeViews.includes('d') ? 'bg-sky-700 text-cyan-300' : 'bg-slate-200 text-gray-800 dark:bg-slate-700 dark:text-gray-200'}`}
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										strokeWidth="1.5"
										stroke="currentColor"
										className="h-6 w-6"
									>
										<path d="M 20 19 L 20 5 M 20 5 L 14 5 L 12 6 L 10 5 L 4 5 L 4 19 L 10 19 L 12 20 L 14 19 L 20 19 M 20 7 L 22 7 L 22 21 L 14 21 L 12 22 L 10 21 L 2 21 L 2 7 L 4 7 M 12 6 L 12 20 M 7 9 L 9 9 M 7 12 L 9 12 M 7 15 L 9 15 M 15 9 L 17 9 M 15 12 L 17 12 M 15 15 L 17 15" />
									</svg>
								</button>
							</Tooltip>
							<Tooltip text="Example">
								<button
									aria-label="Toggle Simulation"
									aria-pressed={activeViews.includes('m')}
									onClick={() => toggleView('m')}
									className={`rounded-e-md p-2 ${activeViews.includes('m') ? 'bg-sky-700 text-cyan-300' : 'bg-slate-200 text-gray-800 dark:bg-slate-700 dark:text-gray-200'}`}
								>
									<MockIcon />
								</button>
							</Tooltip>
						</div>

						<div className="inline-flex rounded-md">
							<Tooltip text="Terminal">
								<button
									aria-label="Toggle Terminal"
									aria-pressed={activeViews.includes('t')}
									onClick={() => toggleView('t')}
									className={`rounded-s-md p-2 ${activeViews.includes('t') ? 'bg-emerald-900 text-green-300' : 'bg-slate-200 text-gray-800 dark:bg-slate-700 dark:text-gray-200'}`}
								>
									<TerminalIcon />
								</button>
							</Tooltip>
							<Tooltip text="Results">
								<button
									aria-label="Toggle Results"
									aria-pressed={activeViews.includes('r')}
									onClick={() => toggleView('r')}
									className={`rounded-e-md p-2 ${activeViews.includes('r') ? 'bg-emerald-900 text-green-300' : 'bg-slate-200 text-gray-800 dark:bg-slate-700 dark:text-gray-200'}`}
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										strokeWidth="1.5"
										stroke="currentColor"
										className="h-6 w-6"
									>
										<path d="M 22 15 L 22 6 M 22 6 L 2 6 L 2 15 M 5 12 L 19 12 M 17 12 L 17 22 L 7 22 L 7 12 M 2 15 L 7 15 M 17 15 L 22 15 M 7 6 L 7 2 L 17 2 L 17 6 M 20 8 L 19 8 L 19 9 L 20 9 M 10 15 L 14 15 M 10 18 L 14 18 Z" />
									</svg>
								</button>
							</Tooltip>
						</div>
					</div>

					<div className="flex flex-1 min-w-0 items-center justify-end">
						<form
							className={`flex items-center space-x-2 ml-4 ${liveUrlActive ? 'w-full' : ''}`}
							onSubmit={handleSourceGet}
						>
							<div
								className={`flex items-stretch rounded-md border focus-within:ring-1 focus-within:ring-inset ${
									urlError
										? 'border-red-500 focus-within:ring-red-500 ring-1 ring-inset ring-red-500 dark:border-red-400 dark:focus-within:ring-red-400'
										: 'border-gray-300 focus-within:ring-gray-500 dark:border-gray-500 dark:focus-within:ring-gray-400'
								} ${liveUrlActive ? 'flex-1 min-w-0' : 'w-80'}`}
							>
								<label
									htmlFor="url"
									className={`content-center rounded-l-md px-2 py-2 text-sm font-medium whitespace-nowrap ${
										urlError
											? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
											: 'bg-zinc-200 text-gray-700 dark:bg-zinc-600 dark:text-gray-200'
									}`}
								>
									Live URL
								</label>

								<div className="relative flex content-center">
									<button
										type="button"
										className={`content-center border-l border-gray-300 dark:border-gray-500 flex items-center gap-1 px-2 py-2 text-sm font-medium lowercase focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-sky-500 ${
											urlError
												? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
												: 'bg-zinc-200 text-gray-700 dark:bg-zinc-600 dark:text-gray-200'
										}`}
										aria-haspopup="listbox"
										aria-label="Select protocol"
										aria-expanded={showDropdown ? 'true' : 'false'}
										onClick={() => setShowDropdown((v) => !v)}
										onKeyDown={dropdownKeydown}
									>
										<span>{sourceUrlProtocol}</span>
										<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
											<path
												fillRule="evenodd"
												d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 10.94l3.71-3.71a.75.75 0 1 1 1.06 1.06l-4.24 4.24a.75.75 0 0 1-1.06 0L5.21 8.29a.75.75 0 0 1 .02-1.08z"
												clipRule="evenodd"
											/>
										</svg>
									</button>

									{showDropdown ? (
										<div
											className="absolute left-0 top-full z-20 mt-1 w-28 overflow-hidden rounded-md border border-gray-200 bg-white shadow-lg dark:border-zinc-600 dark:bg-zinc-700"
											role="listbox"
											aria-label="Select protocol"
											onKeyDown={dropdownKeydown}
											tabIndex={-1}
										>
											<button
												type="button"
												onClick={() => {
													setSourceUrlProtocol('http');
													setShowDropdown(false);
												}}
												className={`block w-full px-3 py-2 text-left text-sm lowercase ${
													sourceUrlProtocol === 'http'
														? 'bg-sky-600 text-white'
														: 'text-gray-700 hover:bg-sky-100 dark:text-gray-100 dark:hover:bg-zinc-600'
												}`}
												role="option"
												aria-selected={sourceUrlProtocol === 'http' ? 'true' : 'false'}
											>
												http
											</button>
											<button
												type="button"
												onClick={() => {
													setSourceUrlProtocol('ws');
													setShowDropdown(false);
												}}
												className={`block w-full px-3 py-2 text-left text-sm lowercase ${
													sourceUrlProtocol === 'ws'
														? 'bg-sky-600 text-white'
														: 'text-gray-700 hover:bg-sky-100 dark:text-gray-100 dark:hover:bg-zinc-600'
												}`}
												role="option"
												aria-selected={sourceUrlProtocol === 'ws' ? 'true' : 'false'}
											>
												ws
											</button>
										</div>
									) : null}
								</div>

								<div
									className={`${liveUrlActive ? 'flex-1 min-w-0' : ''}`}
									onFocus={() => setLiveUrlActive(true)}
									onBlur={handleLiveUrlFocusOut}
								>
									<Tooltip text={urlError ?? ''}>
										<input
											type="text"
											name="url"
											id="url"
											placeholder="None  (draft mode)"
											value={sourceUrlInput}
											onChange={(e) => setSourceUrlInput(e.target.value)}
											className={`w-full rounded-r-md border-0 pl-2 py-2 placeholder:text-gray-400 focus:ring-1 focus:ring-inset ${
												urlError
													? 'bg-red-50 text-red-800 focus:ring-red-500 dark:bg-red-900/30 dark:text-red-200 dark:focus:ring-red-400'
													: 'bg-zinc-100 focus:ring-gray-500 dark:bg-zinc-700 dark:focus:ring-gray-400'
											}`}
											aria-invalid={urlError ? 'true' : 'false'}
											aria-describedby={urlError ? 'live-url-error' : undefined}
										/>
									</Tooltip>
									{urlError ? (
										<p id="live-url-error" className="sr-only">
											{urlError}
										</p>
									) : null}
								</div>
							</div>

							<button
								type="submit"
								className="shrink-0 rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white active:bg-sky-800"
							>
								Load
							</button>
						</form>
					</div>
				</div>
			</nav>

			<main className="mt-16 flex h-[calc(100vh-4em)] bg-zinc-50 dark:bg-zinc-800">
				{loadState.status === 'loading' ? <span>loading schema</span> : null}
				{loadState.status === 'error' ? <span>failed to get schema</span> : null}

				{loadState.status === 'ready' ? (
					<>
						{activeViews.includes('s') ? (
							<div className={`flex h-[calc(100vh-4em)] ${getSectionClass(activeViews, 's', activeViews.length)}`}>
								<div className="flex w-full flex-col p-6">
									<div className="flex justify-between">
										<h1 className="pb-4 text-xl font-semibold text-gray-900 dark:text-gray-100">Schema (JSON)</h1>
										{!readonlyEditor ? (
											<div className="flex space-x-2">
												<a href="https://github.com/Telepact/telepact/blob/main/doc/02-design-apis/01-schema-guide.md">
													<button className="flex items-center rounded-md bg-gray-200 px-3 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-300 hover:underline dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600">
														<span>Writing Guide</span>
														<svg
															xmlns="http://www.w3.org/2000/svg"
															fill="none"
															viewBox="0 0 24 24"
															strokeWidth="3"
															stroke="currentColor"
															className="ml-2 h-4 w-4"
														>
															<path d="M 14 2 L 4 2 A 4 4 0 0 0 0 6 L 0 20 A 4 4 0 0 0 4 24 L 18 24 A 4 4 0 0 0 22 20 L 22 10 M 11 13 L 24 0 L 18 0 M 24 0 L 24 6" />
														</svg>
													</button>
												</a>
												<div>
													<button
														onClick={handleSchemaSave}
														className="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-600 active:bg-sky-700"
													>
														<span>Save</span>
													</button>
												</div>
											</div>
										) : null}
									</div>

									<div className="grow border border-zinc-300 dark:border-zinc-600">
										<MonacoEditor
											key={schemaDraft}
											id="schema"
											readOnly={readonlyEditor}
											json={schemaDraft}
											ctrlEnter={handleSchemaSave}
											filename="schema.telepact.json"
											ariaLabel="schema"
											ref={schemaEditor}
										/>
									</div>
								</div>
							</div>
						) : null}

						{activeViews.includes('d') ? (
							<div className={`flex overflow-scroll ${getSectionClass(activeViews, 'd', activeViews.length)}`}>
								<div className="flex w-full flex-col p-6">
									<div>
										<h1 className="pb-4 text-xl font-semibold text-gray-900 dark:text-gray-100">Schema</h1>
									</div>

									{docEntries.map((entry) => (
										<DocCard key={entry.name} entry={entry} telepactSchema={telepactSchema!} navigate={navigate} />
									))}

									<div className="flex justify-center pb-4">
										<button
											onClick={toggleShowInternalApi}
											className="mt-4 rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-600"
										>
											{showInternalApi ? 'Hide Internal API' : 'Show Internal API'}
										</button>
									</div>
								</div>
							</div>
						) : null}

						{activeViews.includes('m') ? (
							<div className={`flex overflow-scroll ${getSectionClass(activeViews, 'm', activeViews.length)}`}>
								<div className="flex w-full flex-col p-6">
									<div className="flex items-start justify-between">
										<h1 className="pb-4 text-xl font-semibold text-gray-900 dark:text-gray-100">Mocked Example</h1>
										<button
											onClick={() => setSimulationSeed((v) => v + 1)}
											className="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-600"
										>
											Regenerate
										</button>
									</div>

									{simulationState.status === 'loading' ? (
										<div className="mb-4">
											<span>
												Loading...<span> </span>
											</span>
										</div>
									) : null}

									{simulationState.status === 'ready' ? (
										<div className="flex h-full flex-col space-y-2">
											<div className="h-1/2 grow border border-zinc-300 dark:border-zinc-600">
												<MonacoEditor
													key={`${simulationKey}:request`}
													id="requestExample"
													readOnly={true}
													json={simulationState.value.request}
													allowLinks={false}
													filename="requestExample.json"
													ariaLabel="requestExample"
													minimap={false}
												/>
											</div>

											<div className="ml-4 shrink">
												<span className="text-3xl text-emerald-500">→</span>
											</div>

											<div className="h-1/2 grow border border-zinc-300 dark:border-zinc-600">
												<MonacoEditor
													key={`${simulationKey}:response`}
													id="responseExample"
													readOnly={true}
													json={simulationState.value.response}
													allowLinks={false}
													filename="responseExample.json"
													ariaLabel="responseExample"
													lineNumbers={false}
													minimap={false}
												/>
											</div>
										</div>
									) : null}
								</div>
							</div>
						) : null}

						{activeViews.includes('t') ? (
							<div className={`flex h-[calc(100vh-4em)] ${getSectionClass(activeViews, 't', activeViews.length)}`}>
								<div className="flex w-full flex-col bg-zinc-100 p-6 dark:bg-zinc-700">
									<div className="flex justify-between">
										<h1 className="pb-4 text-xl font-semibold text-gray-900 dark:text-gray-100">Request</h1>
										<div>
											<button
												onClick={handleSubmit}
												disabled={responseState.status === 'loading'}
												className={`rounded-md px-3 py-2 text-sm font-semibold ${
													responseState.status === 'loading'
														? 'cursor-not-allowed bg-sky-600/40 text-gray-500 dark:text-gray-300'
														: 'bg-sky-700 text-white active:bg-sky-800'
												}`}
											>
												{submitString}
											</button>
										</div>
									</div>

									<div className="grow border border-zinc-300 dark:border-zinc-600">
										<MonacoEditor
											key={requestParam ?? ''}
											id="request"
											readOnly={false}
											json={unMinifyJson(requestParam, authManaged)}
											ctrlEnter={handleSubmit}
											filename="request.json"
											ariaLabel="request"
											ref={requestEditor}
										/>
									</div>
								</div>
							</div>
						) : null}

						{activeViews.includes('r') ? (
							<div className={`flex h-[calc(100vh-4em)] ${getSectionClass(activeViews, 'r', activeViews.length)}`}>
								{responsePromise ? (
									<div className="flex w-full flex-col bg-zinc-100 p-6 dark:bg-zinc-700">
										<h1 className="mb-4 text-xl font-semibold text-gray-900 dark:text-gray-100">Response</h1>

										{responseState.status === 'loading' ? (
											<div className="grid h-full w-full place-content-center">
												<div>
													<span>
														Loading...<span> </span>
													</span>
												</div>
											</div>
										) : null}

										{responseState.status === 'ready' ? (
											<div className="grow border border-zinc-300 dark:border-zinc-600">
												<MonacoEditor
													key={responseState.value}
													id="response"
													readOnly={true}
													json={responseState.value}
													allowLinks={true}
													filename="response.json"
													ariaLabel="response"
												/>
											</div>
										) : null}

										{responseState.status === 'error' ? (
											<div className="h-full rounded-md border border-red-300 bg-red-100 p-4 text-red-700 dark:border-red-700 dark:bg-red-500/20 dark:text-red-500">
												<div className="overflow-scroll">
													<span>{String(responseState.error)}</span>
												</div>
											</div>
										) : null}
									</div>
								) : (
									<div className="grid h-full w-full place-content-center">
										<div>
											<span>Click "Submit" on Request pane to fetch response.</span>
										</div>
									</div>
								)}
							</div>
						) : null}
					</>
				) : null}
			</main>
		</div>
	);
}
