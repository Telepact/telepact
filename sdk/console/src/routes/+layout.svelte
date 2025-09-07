<!--|                                                                            |-->
<!--|  Copyright The Telepact Authors                                            |-->
<!--|                                                                            |-->
<!--|  Licensed under the Apache License, Version 2.0 (the "License");           |-->
<!--|  you may not use this file except in compliance with the License.          |-->
<!--|  You may obtain a copy of the License at                                   |-->
<!--|                                                                            |-->
<!--|  https://www.apache.org/licenses/LICENSE-2.0                               |-->
<!--|                                                                            |-->
<!--|  Unless required by applicable law or agreed to in writing, software       |-->
<!--|  distributed under the License is distributed on an "AS IS" BASIS,         |-->
<!--|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  |-->
<!--|  See the License for the specific language governing permissions and       |-->
<!--|  limitations under the License.                                            |-->
<!--|                                                                            |-->

<script lang="ts">
	import { preventDefault } from 'svelte/legacy';

	import '../app.css';

	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { beforeNavigate } from '$app/navigation';
	import { TelepactSchema, Message, jsonSchema } from '$lib/telepact/index.esm';

	import {
		genExample,
		handleRequest,
		handleSubmitRequest,
		minifyJson,
		parseTelepactSchema,
		unMinifyJson
	} from '$lib';

	import MonacoEditor from '$lib/MonacoEditor.svelte';
	import DocCard from '$lib/DocCard.svelte';
	import TerminalIcon from '$lib/TerminalIcon.svelte';
	import MockIcon from '$lib/MockIcon.svelte';
	import { responseStore } from '$lib';
	import { onMount } from 'svelte';
	import { createJsonSchema } from '$lib/jsonSchema';
	import * as monaco from 'monaco-editor';
	import Tooltip from '$lib/Tooltip.svelte';
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();

	let requestEditor: MonacoEditor;
	let schemaEditor: MonacoEditor;

	let sourceUrl: string = $derived($page.url.searchParams.get('s') ?? '');

	let schemaSource: string = $derived($page.data.schemaSource);

	let submitString: string = $derived(
		schemaSource === 'draft' ? 'Submit (mock)' : 'Submit (live)'
	);

	let schemaSourceReadOnly: boolean = $derived($page.data.readonlyEditor);

	let request: string | null = $derived($page.url.searchParams.get('r'));

	let response: Promise<string> | null = $derived($responseStore);

	let showInternalApi: boolean = $derived($page.data.showInternalApi);

	let telepactSchemaPromise: Promise<TelepactSchema> = $derived($page.data.fullTelepactSchemaRef);

	let schemaDraftPromise: Promise<string> = $derived($page.data.schemaDraft);

	let filteredSchemaPseudoJsonPromise: Promise<any[]> = $derived(
		$page.data.filteredSchemaPseudoJson
	);

	let authManaged: boolean = $derived($page.data.authManaged);

	console.log(`page.data`, $page.data);

	let selectedViews = $derived($page.url.searchParams.get('v') ?? 'd');

	let activeViews: string = $derived(selectedViews.substring(0, 2));

	let sortDocCardsAZ: boolean = $derived($page.url.searchParams.get('az') === '1');

	let exampleFn: string = $derived($page.url.searchParams.get('mf') ?? 'fn.ping_');

	let exampleHeaders: Array<string> = $derived(
		($page.url.searchParams.get('mh') ?? '').split(',')
	);

	beforeNavigate(({ type }) => {
		if (type === 'popstate') {
			$responseStore = null;
		}
	});

	$effect(() => {
		if (telepactSchemaPromise) {
			telepactSchemaPromise.then((e) => {
				console.log('Reloading request json schema');
				const requestJsonSchema = createJsonSchema(e);
				monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
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
			});
		}
	});

	type view = 's' | 'd' | 't' | 'r' | 'm';

	let randomSeed = $state(1);

	function handleSourceGet(e: Event) {
		console.log(`e`, e);
		const formData = new FormData(e.target as HTMLFormElement);
		const sourceUrl = formData.get('url') as string;

		let q = new URLSearchParams($page.url.searchParams.toString());

		const existingS = q.get('s');

		if (existingS !== sourceUrl) {
			q.delete('mf');
			q.delete('mh');
			q.delete('r');
			q.set('v', 'd');
		}

		q.set('s', sourceUrl ?? '');
		goto(`?${q.toString()}`);
	}

	function thisHandleRequest() {
		if (
			schemaSource === 'http' &&
			!sessionStorage.getItem('telepact-console:live-request-acknowledge')
		) {
			if (!confirm('You are about to submit a request to a live server.')) {
				return;
			} else {
				sessionStorage.setItem('telepact-console:live-request-acknowledge', 'true');
			}
		}

		let request = requestEditor.getContent();
		handleRequest(request, 'tr');
		handleSubmitRequest($page.data.client, request);
	}

	function handleSchema() {
		let schema = schemaEditor.getContent();
		let minifiedSchema = minifyJson(schema);
		let q = new URLSearchParams($page.url.searchParams.toString());
		q.set('s', '');
		q.set('sd', minifiedSchema!);
		q.set('v', 'sd');
		goto(`?${q.toString()}`);
	}

	function toggleView(v: view) {
		let newViews: string;
		if (selectedViews.substring(0, 2).includes(v)) {
			newViews = selectedViews.replace(v, '');
		} else {
			if (selectedViews.includes(v)) {
				let temp = selectedViews.replace(v, '');
				newViews = v + temp;
			} else {
				newViews = v + selectedViews;
			}
		}
		let q = new URLSearchParams($page.url.searchParams.toString());
		q.set('v', newViews);
		goto(`?${q.toString()}`);
	}

	function toggleTerminal() {
		toggleView('t');
	}

	function toggleResults() {
		toggleView('r');
	}

	function toggleShowSchemaCode() {
		toggleView('s');
	}

	function toggleShowDocUi() {
		toggleView('d');
	}

	function toggleShowExample() {
		toggleView('m');
	}

	function toggleShowInternalApi() {
		let q = new URLSearchParams($page.url.searchParams.toString());
		if (showInternalApi) {
			q.delete('i');
		} else {
			q.set('i', '1');
		}
		goto(`?${q.toString()}`);
	}

	function toggleSortDocCardsAZ() {
		let q = new URLSearchParams($page.url.searchParams.toString());
		if (sortDocCardsAZ) {
			q.delete('az');
		} else {
			q.set('az', '1');
		}
		goto(`?${q.toString()}`);
	}

	function incrementRandomSeed() {
		randomSeed += 1;
	}

	function getSectionClass(v: view, activeViewsLength: number) {
		let width = activeViewsLength === 1 ? 'w-full' : 'w-1/2';
		if (v === 's') {
			return 'justify-start ' + width;
		} else if (activeViews.includes('s')) {
			return 'justify-end ' + width;
		} else if (v === 'd') {
			return 'justify-start ' + width;
		} else if (activeViews.includes('d')) {
			return 'justify-end ' + width;
		} else if (v === 'r') {
			return 'justify-end ' + width;
		} else if (activeViews.includes('r')) {
			return 'justify-start ' + width;
		} else if (v === 't' && activeViews.includes('m')) {
			return 'justify-end ' + width;
		} else if (v === 'm' && activeViews.includes('t')) {
			return 'justify-start ' + width;
		} else {
			return 'justify-end ' + width;
		}
	}

	let showDropdown = false;

	function toggleDropdown() {
		showDropdown = !showDropdown;
	}

	function closeDropdown() {
		showDropdown = false;
	}
</script>

<div class="text-gray-200">
	<nav class="fixed top-0 z-10 h-16 w-full border-y border-slate-600 bg-slate-800">
		<div class="flex h-full items-center px-4">
			<div class="flex basis-1/3">
				<div class="flex items-center rounded-md py-2">
					<div class="text-sky-400">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1"
							stroke="currentColor"
							class="h-8 w-8"
						>
							<!-- <path
								d="M 12 16 A 1 1 0 0 0 12 8 A 1 1 0 0 0 12 16 M 8 16 L 5 19 M 3 20 A 1 1 0 0 0 3 22 A 1 1 0 0 0 3 20 M 16 8 L 19 5 M 21 4 A 1 1 0 0 0 21 2 A 1 1 0 0 0 21 4 M 7 12 L 5 12 M 4 12 A 1 1 0 0 0 2 12 A 1 1 0 0 0 4 12 M 17 12 L 19 12 M 20 12 A 1 1 0 0 0 22 12 A 1 1 0 0 0 20 12 M 12 7 L 12 4 M 12 17 L 12 20 M 10 22 L 14 22 M 10 2 L 14 2"
							/> -->
							<path
								d="M 2.093 6.908 C 0.414 4.35 1.447 0.938 3 1 C 3.67 1.171 3.799 1.352 4.057 1.946 C 4.833 4.117 4 11 2 23 L 16 23 M 18 2 A 1 1 0 0 0 17 1 L 3 1 M 10 17 C 14.007 12.249 17 9 21 7 M 10.965 15.376 C 10.939 14.498 10.965 13.671 11.224 12.947 L 11.991 13.619 L 11.663 12.172 C 13.369 10.104 14.842 8.347 16.514 7.494 L 17.366 8.993 L 17.788 6.9 C 22.879 4.652 24.403 5.763 21.251 8.787 L 20.726 8.037 L 20.829 9.123 C 18.201 11.371 15.022 14.369 11.301 15.712 M 18 2 L 18 5 M 16 23 C 16.619 20.297 16.959 17.314 17.185 15.578"
							/>
						</svg>
					</div>
					<h1 class="px-2 text-lg font-semibold text-gray-100">Telepact</h1>
				</div>
			</div>
			<div id="view-select" class="flex basis-1/3 content-center justify-center space-x-2">
				<div class="inline-flex rounded-md">
					<Tooltip text="Schema">
						<button
							aria-label="Toggle Schema"
							aria-pressed={activeViews.includes('s')}
							onclick={toggleShowSchemaCode}
							class="rounded-s-md p-2 {activeViews.includes('s')
								? 'bg-sky-700 text-cyan-300'
								: 'bg-slate-700 text-gray-200'}"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								stroke-width="1"
								stroke="currentColor"
								class="h-6 w-6"
							>
								<path
									d="M 2 22 L 5 16 L 19 2 L 22 5 L 8 19 L 2 22 M 5 16 L 8 19 M 19 8 L 16 5 M 17 4 L 20 7"
								/>
							</svg>
						</button>
					</Tooltip>
					<Tooltip text="Documentation">
						<button
							aria-label="Toggle Documentation"
							aria-pressed={activeViews.includes('d')}
							onclick={toggleShowDocUi}
							class="p-2 {activeViews.includes('d')
								? 'bg-sky-700 text-cyan-300'
								: 'bg-slate-700 text-gray-200'}"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
								class="h-6 w-6"
							>
								<path
									d="M 20 19 L 20 5 M 20 5 L 14 5 L 12 6 L 10 5 L 4 5 L 4 19 L 10 19 L 12 20 L 14 19 L 20 19 M 20 7 L 22 7 L 22 21 L 14 21 L 12 22 L 10 21 L 2 21 L 2 7 L 4 7 M 12 6 L 12 20 M 7 9 L 9 9 M 7 12 L 9 12 M 7 15 L 9 15 M 15 9 L 17 9 M 15 12 L 17 12 M 15 15 L 17 15"
								/>
							</svg>
						</button>
					</Tooltip>
					<Tooltip text="Example">
						<button
							aria-label="Toggle Simulation"
							aria-pressed={activeViews.includes('m')}
							onclick={toggleShowExample}
							class="rounded-e-md p-2 {activeViews.includes('m')
								? 'bg-sky-700 text-cyan-300'
								: 'bg-slate-700 text-gray-200'}"
						>
							<MockIcon />
						</button>
					</Tooltip>
				</div>
				<div class="inline-flex rounded-md">
					<Tooltip text="Terminal">
						<button
							aria-label="Toggle Terminal"
							aria-pressed={activeViews.includes('t')}
							onclick={toggleTerminal}
							class="rounded-s-md p-2 {activeViews.includes('t')
								? 'bg-emerald-900 text-green-300'
								: 'bg-slate-700 text-gray-200'}"
						>
							<TerminalIcon />
						</button>
					</Tooltip>
					<Tooltip text="Results">
						<button
							aria-label="Toggle Results"
							aria-pressed={activeViews.includes('r')}
							onclick={toggleResults}
							class="rounded-e-md p-2 {activeViews.includes('r')
								? 'bg-emerald-900 text-green-300'
								: 'bg-slate-700 text-gray-200'}"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
								class="h-6 w-6"
							>
								<path
									d="M 22 15 L 22 6 M 22 6 L 2 6 L 2 15 M 5 12 L 19 12 M 17 12 L 17 22 L 7 22 L 7 12 M 2 15 L 7 15 M 17 15 L 22 15 M 7 6 L 7 2 L 17 2 L 17 6 M 20 8 L 19 8 L 19 9 L 20 9 M 10 15 L 14 15 M 10 18 L 14 18 Z"
								/>
							</svg>
						</button>
					</Tooltip>
				</div>
			</div>
			<div class="flex basis-1/3 justify-end">
				<form class="flex space-x-2" onsubmit={preventDefault(handleSourceGet)}>
					<div class="flex rounded-md border border-gray-500">
						<label
							for="url"
							class="content-center rounded-l-md bg-zinc-600 px-2 py-2 text-sm font-medium text-gray-200 whitespace-nowrap"
							>Live URL</label
						>
						<div>
							<input
								type="text"
								name="url"
								id="url"
								placeholder="None  (draft mode)"
								value={sourceUrl}
								class="rounded-r-md border-0 bg-zinc-700 py-2 placeholder:text-gray-400 focus:border-gray-500 focus:ring-1 focus:ring-inset focus:ring-gray-500"
							/>
						</div>
					</div>
					<button
						type="submit"
						class="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white active:bg-sky-800"
						>Load</button
					>
				</form>
			</div>
		</div>
	</nav>

	<main class="mt-16 flex h-[calc(100vh-4em)] bg-zinc-800">
		{#await Promise.all( [telepactSchemaPromise, filteredSchemaPseudoJsonPromise, schemaDraftPromise] )}
			<span>loading schema</span>
		{:then [telepactSchema, filteredSchemaPseudoJson, schemaDraft]}
			{#if activeViews.includes('s')}
				<div class="flex h-[calc(100vh-4em)] {getSectionClass('s', activeViews.length)}">
					<div class="flex w-full flex-col p-6">
						<div class="flex justify-between">
							<h1 class="pb-4 text-xl font-semibold text-gray-100">Schema (JSON)</h1>
							{#if !schemaSourceReadOnly}
								<div class="flex space-x-2">
									<a
										href="https://github.com/Telepact/telepact/blob/main/doc/schema-guide.md"
									>
										<button
											onclick={handleSchema}
											class="flex items-center rounded-md bg-gray-700 px-3 py-2 text-sm font-semibold text-white hover:bg-gray-600 hover:underline"
										>
											<span>Writing Guide</span>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="3"
												stroke="currentColor"
												class="ml-2 h-4 w-4"
											>
												<path
													d="M 14 2 L 4 2 A 4 4 0 0 0 0 6 L 0 20 A 4 4 0 0 0 4 24 L 18 24 A 4 4 0 0 0 22 20 L 22 10 M 11 13 L 24 0 L 18 0 M 24 0 L 24 6"
												/>
											</svg>
										</button>
									</a>
									<div>
										<button
											onclick={handleSchema}
											class="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-600 active:bg-sky-700"
											><span>Save</span></button
										>
									</div>
								</div>
							{/if}
						</div>
						<div class="grow border border-zinc-600">
							<MonacoEditor
								id="schema"
								readOnly={schemaSourceReadOnly}
								json={schemaDraft}
								ctrlEnter={handleSchema}
								filename="schema.telepact.json"
								ariaLabel="schema"
								bind:this={schemaEditor}
							/>
						</div>
					</div>
				</div>
			{/if}
			{#if activeViews.includes('d')}
				<div class="flex overflow-scroll {getSectionClass('d', activeViews.length)}">
					<div class="flex w-full flex-col p-6">
						<div>
							<h1 class="pb-4 text-xl font-semibold text-gray-100">Schema</h1>
						</div>
						{#key sortDocCardsAZ}
							{#each parseTelepactSchema(filteredSchemaPseudoJson, telepactSchema, sortDocCardsAZ, showInternalApi) as entry}
								{#if showInternalApi || !(Object.keys(entry)[0].split('.')[1] ?? '').endsWith('_')}
									<DocCard {entry} {telepactSchema} />
								{/if}
							{/each}
						{/key}
						<div class="flex justify-center pb-4">
							<button
								onclick={toggleShowInternalApi}
								class="mt-4 rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-600"
								>{showInternalApi
									? 'Hide Internal Api'
									: 'Show Internal Api'}</button
							>
						</div>
					</div>
				</div>
			{/if}
			{#if activeViews.includes('m')}
				<div class="flex overflow-scroll {getSectionClass('m', activeViews.length)}">
					<div class="flex w-full flex-col p-6">
						<div class="flex items-start justify-between">
							<h1 class="pb-4 text-xl font-semibold text-gray-100">Mocked Example</h1>
							<button
								onclick={incrementRandomSeed}
								class="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-600"
							>
								Regenerate
							</button>
						</div>
						{#key randomSeed + exampleFn}
							{#await genExample(exampleFn, exampleHeaders, telepactSchema)}
								<div class="mb-4">
									<span>Loading...<span> </span></span>
								</div>
							{:then example}
								<div class="flex h-full flex-col space-y-2">
									<div class="h-1/2 grow border border-zinc-600">
										<MonacoEditor
											id={'requestExample'}
											readOnly={true}
											json={example.request}
											allowLinks={false}
											filename={'requestExample.json'}
											ariaLabel="requestExample"
											minimap={false}
										/>
									</div>
									<div class="ml-4 shrink">
										<span class="text-3xl text-emerald-500">→</span>
									</div>
									<div class="h-1/2 grow border border-zinc-600">
										<MonacoEditor
											id={'responseExample'}
											readOnly={true}
											json={example.response}
											allowLinks={false}
											filename={'responseExample.json'}
											ariaLabel="responseExample"
											lineNumbers={false}
											minimap={false}
										/>
									</div>
								</div>
							{/await}
						{/key}
					</div>
				</div>
			{/if}
		{:catch error}
			<span>failed to get schema</span>
		{/await}
		{#if activeViews.includes('t')}
			<div class="flex h-[calc(100vh-4em)] {getSectionClass('t', activeViews.length)}">
				<div class="flex w-full flex-col bg-zinc-700 p-6">
					<div class="flex justify-between">
						<h1 class="pb-4 text-xl font-semibold text-gray-100">Request</h1>
						<div>
							{#if response}
								{#await response}
									<button
										disabled
										class="cursor-not-allowed rounded-md bg-sky-600/40 px-3 py-2 text-sm font-semibold text-gray-300"
										>{submitString}</button
									>
								{:then}
									<button
										onclick={thisHandleRequest}
										class="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white active:bg-sky-800"
										>{submitString}</button
									>
								{:catch error}
									<button
										onclick={thisHandleRequest}
										class="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white active:bg-sky-800"
										>{submitString}</button
									>
								{/await}
							{:else}
								<button
									onclick={thisHandleRequest}
									class="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white active:bg-sky-800"
									>{submitString}</button
								>
							{/if}
						</div>
					</div>
					{#key request}
						<div class="grow border border-zinc-600">
							<MonacoEditor
								id="request"
								readOnly={false}
								json={unMinifyJson(request, authManaged)}
								ctrlEnter={() => thisHandleRequest()}
								filename="request.json"
								ariaLabel="request"
								bind:this={requestEditor}
							/>
						</div>
					{/key}
				</div>
			</div>
		{/if}
		{#if activeViews.includes('r')}
			<div class="flex h-[calc(100vh-4em)] {getSectionClass('r', activeViews.length)}">
				{#if response}
					<div class="flex w-full flex-col bg-zinc-700 p-6">
						<h1 class="mb-4 text-xl font-semibold text-gray-100">Response</h1>
						{#await response}
							<div class="grid h-full w-full place-content-center">
								<div>
									<span>Loading...<span> </span></span>
								</div>
							</div>
						{:then d}
							{#key d}
								<div class="grow border border-zinc-600">
									<MonacoEditor
										id="response"
										readOnly={true}
										json={d}
										allowLinks={true}
										filename="response.json"
										ariaLabel="response"
									/>
								</div>
							{/key}
						{:catch error}
							<div
								class="h-full rounded-md border border-red-700 bg-red-500/20 p-4 text-red-500"
							>
								<div class="overflow-scroll">
									<span>{error}</span>
									{#if error.stack}
										<div class="text-sm text-gray-400">
											{error.stack}
										</div>
									{/if}
								</div>
							</div>
						{/await}
					</div>
				{:else}
					<div class="grid h-full w-full place-content-center">
						<div>
							<span>Click "Submit" on Request pane to fetch response.</span>
						</div>
					</div>
				{/if}
			</div>
		{/if}
		{@render children?.()}
	</main>
</div>
