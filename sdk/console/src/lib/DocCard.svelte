<script lang="ts">
	import { parse } from 'marked';
	import DocCardEnumTags from './DocCardEnumTags.svelte';
	import DocCardStructFields from './DocCardStructFields.svelte';
	import TerminalIcon from './TerminalIcon.svelte';
	import DOMPurify from 'dompurify';
	import { goto } from '$app/navigation';
	import {
		generateExample,
		generateFnResultExample,
		generateHeaderExample,
		isFnTypeData,
		isHeaderData,
		isUnionTagTypeData,
		type TypeData
	} from '$lib';
	import { page } from '$app/stores';
	import { MsgPactSchema } from './msgpact/index.esm';
	import { onMount } from 'svelte';
	import MonacoEditor from './MonacoEditor.svelte';
	import TypeRef from './TypeRef.svelte';
	import Example from './Example.svelte';
	import MockIcon from './MockIcon.svelte';

	export let entry: TypeData;
	export let msgpactSchema: MsgPactSchema;

	let argumentExampleMonaco: MonacoEditor;

	let showExample: boolean = false;
	let includeErrorsInExample: boolean = false;
	let randomSeed = 1;

	let data = entry.data;
	let schemaKey = entry.name;

	let descriptionDef = entry.doc;
	let descriptionStr = Array.isArray(descriptionDef)
		? descriptionDef.map((l) => l.trim()).join('\n')
		: descriptionDef;
	let markdownHtml = typeof descriptionStr == 'string' ? (parse(descriptionStr) as string) : '';
	let description: string = DOMPurify.sanitize(markdownHtml);
	let nameParts = schemaKey.split('.');

	function applyFunctionToExample() {
		let q = new URLSearchParams($page.url.searchParams.toString());
		q.set('v', 'md');
		q.set('mf', schemaKey);
		goto(`?${q.toString()}#${schemaKey}`);
	}

	function toggleHeaderForExample(header: string, schemaKey: string) {
		console.log(`toggleHeaderForExample`, header, schemaKey);
		let q = new URLSearchParams($page.url.searchParams.toString());
		let existingHeaders = (q.get('mh') ?? '').split(',').filter((h) => h !== '');
		console.log(`existingHeaders`, existingHeaders);
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
	class="mb-2 rounded-lg border border-gray-200 bg-white p-6 shadow dark:border-gray-700 dark:bg-gray-800"
>
	<div class="flex w-full items-center pb-4">
		<a href="#{schemaKey}">
			<h5
				class="rounded-md px-2 py-1 font-mono text-2xl font-bold tracking-tight text-white {schemaKey.startsWith(
					'fn'
				)
					? 'bg-amber-700'
					: schemaKey.startsWith('struct')
						? 'bg-sky-700'
						: schemaKey.startsWith('union')
							? 'bg-green-700'
							: schemaKey.startsWith('errors')
								? 'bg-rose-800'
								: schemaKey.startsWith('info')
									? 'bg-slate-600'
									: 'bg-gray-700'}"
			>
				{schemaKey}
			</h5>
		</a>
		{#if isFnTypeData(data)}
			<span class="grow" />
			<div>
				<button
					on:click={applyFunctionToExample}
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
				<div class="docstring font-normal text-gray-700 dark:text-gray-400">
					{@html description}
				</div>
			{/if}

			<Example {schemaKey} generate={() => generateExample(schemaKey, msgpactSchema)} />
		{:else if isFnTypeData(data)}
			<div class="space-y-1">
				<section aria-label="Arguments">
				<DocCardStructFields fields={data.args} />
				{#if description}
					<div class="docstring font-normal text-gray-700 dark:text-gray-400">
						{@html description}
					</div>
				{/if}

				<Example {schemaKey} generate={() => generateExample(schemaKey, msgpactSchema)} />
				</section>

				<section aria-label="Result">
					<div>
						<span class="text-3xl text-emerald-500">→</span>
					</div>

					<DocCardEnumTags tags={data.results} />

					<div class="flex items-center justify-center space-x-2">
						<button
							on:click={toggleShowExample}
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
								on:click={incrementRandomSeed}
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
										msgpactSchema,
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
				<div class="docstring font-normal text-gray-700 dark:text-gray-400">
					{@html description}
				</div>
			{/if}

			<div class="space-y-2">
				<DocCardEnumTags tags={data} />
			</div>

			<Example {schemaKey} generate={() => generateExample(schemaKey, msgpactSchema)} />
		{:else if isHeaderData(data)}
			<div>
				{#if description}
					<div class="docstring font-normal text-gray-700 dark:text-gray-400">
						{@html description}
					</div>
				{/if}

				<DocCardStructFields fields={data.requestData}>
					<div slot="field" let:header>
						<button
							on:click={() => toggleHeaderForExample(header, schemaKey)}
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
				</DocCardStructFields>

				{#if Object.keys(data.requestData).length > 0}
					<Example
						schemaKey={'request.' + schemaKey}
						generate={() =>
							generateHeaderExample(
								'request',
								Object.keys(data.requestData),
								msgpactSchema
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
								msgpactSchema
							)}
					/>
				{/if}
			</div>
		{:else if description}
			<div class="docstring font-normal text-gray-700 dark:text-gray-400">
				{@html description}
			</div>
		{/if}
	</div>
</section>
