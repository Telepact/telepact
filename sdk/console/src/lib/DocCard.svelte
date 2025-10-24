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
	import DocCardEnumTags from './DocCardEnumTags.svelte';
	import DocCardStructFields from './DocCardStructFields.svelte';
	import TerminalIcon from './TerminalIcon.svelte';
	import { goto } from '$app/navigation';
	import {
		generateExample,
		generateFnResultExample,
		generateHeaderExample,
		isFnTypeData,
		isHeaderData,
		isUnionTagTypeData,
		markdownHtml,
		type TypeData
	} from '$lib';
	import { page } from '$app/stores';
	import { TelepactSchema } from './telepact/index.esm';
	import { onMount } from 'svelte';
	import MonacoEditor from './MonacoEditor.svelte';
	import TypeRef from './TypeRef.svelte';
	import Example from './Example.svelte';
	import MockIcon from './MockIcon.svelte';

	interface Props {
		entry: TypeData;
		telepactSchema: TelepactSchema;
	}

	let { entry, telepactSchema }: Props = $props();

	let argumentExampleMonaco: MonacoEditor;

	let showExample: boolean = $state(false);
	let includeErrorsInExample: boolean = $state(false);
	let randomSeed = $state(1);

	let data = entry.data;
	let schemaKey = entry.name;

	let description: string = markdownHtml(entry);
	let nameParts = schemaKey.split('.');

	function applyFunctionToExample() {
		let q = new URLSearchParams($page.url.searchParams.toString());
		q.set('v', 'md');
		q.set('mf', schemaKey);
		goto(`?${q.toString()}#${schemaKey}`);
	}

	function toggleHeaderForExample(header: string, schemaKey: string) {
		let q = new URLSearchParams($page.url.searchParams.toString());
		let existingHeaders = (q.get('mh') ?? '').split(',').filter((h) => h !== '');
		let newHeaders = existingHeaders.includes(header)
			? existingHeaders.filter((h) => h !== header)
			: [...existingHeaders, header];
		q.set('mh', newHeaders.join(','));
		goto(`?${q.toString()}#${schemaKey}`);
	}

	function toggleShowExample() {
		showExample = !showExample;
	}

	function incrementRandomSeed() {
		randomSeed += 1;
	}

	onMount(() => {
		const hash = $page.url.hash;
		const id = hash?.replace('#', '');
		if (id) {
			if (id == schemaKey) {
				// scroll into view
				document.getElementById(schemaKey)?.scrollIntoView();
			}
		}
	});
</script>

<section
	id={schemaKey}
	aria-label={schemaKey}
	class="mb-2 rounded-lg border p-6 shadow border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
>
	<div class="flex w-full items-center pb-4">
		<a href="#{schemaKey}">
			<h5
				class="rounded-md px-2 py-1 font-mono text-2xl font-bold tracking-tight text-gray-900 dark:text-white {schemaKey.startsWith(
					'fn'
				)
					? 'bg-amber-500 dark:bg-amber-700'
					: schemaKey.startsWith('struct')
						? 'bg-sky-500 dark:bg-sky-700'
						: schemaKey.startsWith('union')
							? 'bg-green-500 dark:bg-green-700'
							: schemaKey.startsWith('errors')
								? 'bg-rose-500 dark:bg-rose-800'
								: schemaKey.startsWith('info')
									? 'bg-slate-300 dark:bg-slate-600'
									: 'bg-gray-200 dark:bg-gray-700'}"
			>
				{schemaKey}
			</h5>
		</a>
		{#if isFnTypeData(data)}
			<span class="grow"></span>
			<div>
				<button
					onclick={applyFunctionToExample}
					class="group flex items-center space-x-2 py-2"
				>
					<span class="group-hover:underline">Simulate</span>
					<div class="rounded-lg p-1 group-hover:bg-sky-700 group-hover:text-cyan-300">
						<MockIcon />
					</div>
				</button>
			</div>
		{/if}
	</div>
	<div>
		{#if schemaKey.startsWith('struct')}
			<DocCardStructFields fields={entry.data} />
			{#if description}
				<div class="pt-4 prose dark:prose-invert">
					{@html description}
				</div>
			{/if}

			<Example {schemaKey} generate={() => generateExample(schemaKey, telepactSchema)} />
		{:else if isFnTypeData(data)}
			<div class="space-y-1">
				<section aria-label="Arguments">
				<DocCardStructFields fields={data.args} />
				{#if description}
					<div class="pt-4 prose dark:prose-invert">
						{@html description}
					</div>
				{/if}

				<Example {schemaKey} generate={() => generateExample(schemaKey, telepactSchema)} />
				</section>

				<section aria-label="Result">
					<div>
						<span class="text-3xl text-emerald-500">→</span>
					</div>

					<DocCardEnumTags tags={data.results} />

					<div class="flex items-center justify-center space-x-2">
						<button
							onclick={toggleShowExample}
							class="group mt-2 flex items-center rounded-lg hover:underline"
						>
							<h6
								class="rounded-md p-2 {showExample
									? 'border border-slate-500 font-bold'
									: ''}"
							>
								{showExample ? 'Hide Example' : 'Example'}
							</h6>
						</button>
						{#if showExample}
							<button
								onclick={incrementRandomSeed}
								class="group mt-2 flex items-center rounded-lg hover:underline"
							>
								<h6 class="rounded-md border border-slate-500 p-2 font-bold">
									Regenerate
								</h6>
							</button>
							<label>
								<input
									type="checkbox"
									class="mr-1"
									bind:checked={includeErrorsInExample}
								/> Include Errors
							</label>
						{/if}
					</div>
					{#if showExample}
						<div class="py-2">
							{#key randomSeed}
								<MonacoEditor
									id={schemaKey}
									readOnly={true}
									json={generateFnResultExample(
										schemaKey,
										telepactSchema,
										includeErrorsInExample
											? null
											: {
													Ok_: {}
												},
										!includeErrorsInExample
									)}
									allowLinks={false}
									filename={schemaKey + '.result.json'}
									ariaLabel={schemaKey + '.result.example'}
									fullHeight={false}
									lineNumbers={false}
									minimap={false}
								/>
							{/key}
						</div>
					{/if}

					{#if data.inheritedErrors?.length ?? 0 > 0}
						<div class="pt-4">
							<div class="border-t border-gray-500 pt-2">
								<h6 class="font-bold tracking-tight">Also includes:</h6>
								<ul>
									{#each data.inheritedErrors as inheritedError}
										<ul>
											<a
												href={`#${inheritedError}`}
												class="text-md pl-4 text-sky-400 hover:underline"
												>{inheritedError}</a
											>
										</ul>
									{/each}
								</ul>
							</div>
						</div>
					{/if}
				</section>
			</div>
		{:else if isUnionTagTypeData(data)}
			{#if description}
				<div class="pb-2 prose dark:prose-invert">
					{@html description}
				</div>
			{/if}

			<div class="space-y-2">
				<DocCardEnumTags tags={data} />
			</div>

			<Example {schemaKey} generate={() => generateExample(schemaKey, telepactSchema)} />
		{:else if isHeaderData(data)}
			<div>
				{#if description}
					<div class="prose dark:prose-invert">
						{@html description}
					</div>
				{/if}

				<DocCardStructFields fields={data.requestData}>
					{#snippet field({ header })}
																<div  >
							<button
								onclick={() => toggleHeaderForExample(header, schemaKey)}
								class="group flex items-center space-x-2"
							>
								<span class="group-hover:underline">Simulate</span>
								<div
									class="rounded-lg px-1 group-hover:bg-sky-700 group-hover:text-cyan-300"
								>
									<MockIcon />
								</div>
							</button>
						</div>
															{/snippet}
				</DocCardStructFields>

				{#if Object.keys(data.requestData).length > 0}
					<Example
						schemaKey={'request.' + schemaKey}
						generate={() =>
							generateHeaderExample(
								'request',
								Object.keys(data.requestData),
								telepactSchema
							)}
					/>
				{/if}
				<div class="pl-4">
					<span class="text-3xl text-emerald-500">→</span>
				</div>

				<DocCardStructFields fields={data.responseData} />

				{#if Object.keys(data.responseData).length > 0}
					<Example
						schemaKey={'response.' + schemaKey}
						generate={() =>
							generateHeaderExample(
								'response',
								Object.keys(data.responseData),
								telepactSchema
							)}
					/>
				{/if}
			</div>
		{:else if description}
			<div class="prose dark:prose-invert">
				{@html description}
			</div>
		{/if}
	</div>
</section>
