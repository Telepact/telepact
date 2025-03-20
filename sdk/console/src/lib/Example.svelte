<script lang="ts">
	import MonacoEditor from './MonacoEditor.svelte';

	export let schemaKey: string;
	export let generate: () => string;

	let showExample: boolean = false;
	let randomSeed: number = 1;

	function incrementRandomSeed() {
		randomSeed += 1;
	}

	function toggleShowExample() {
		showExample = !showExample;
	}
</script>

<div class="flex items-center justify-center space-x-2">
	<button
		on:click={toggleShowExample}
		class="group mt-2 flex items-center rounded-lg hover:underline"
	>
		<h6 class="rounded-md p-2 {showExample ? 'border border-slate-500 font-bold' : ''}">
			{showExample ? 'Hide Example' : 'Example'}
		</h6>
	</button>
	{#if showExample}
		<button
			on:click={incrementRandomSeed}
			class="group mt-2 flex items-center rounded-lg hover:underline"
		>
			<h6 class="rounded-md border border-slate-500 p-2 font-bold">Regenerate</h6>
		</button>
	{/if}
</div>
{#if showExample}
	<div class="py-2">
		{#key randomSeed}
			<MonacoEditor
				id={schemaKey}
				readOnly={true}
				json={generate()}
				allowLinks={false}
				filename={schemaKey + '.json'}
				ariaLabel={schemaKey + '.example'}
				fullHeight={false}
				lineNumbers={false}
				minimap={false}
			/>
		{/key}
	</div>
{/if}
