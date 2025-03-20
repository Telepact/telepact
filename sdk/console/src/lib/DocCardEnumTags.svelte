<script lang="ts">
	import { doc } from 'prettier';
	import TypeRef from './TypeRef.svelte';
	import DocCardStructFields from './DocCardStructFields.svelte';
	import type { UnionTagTypeData } from '$lib';

	export let tags: UnionTagTypeData[];
</script>

<ul class="space-y-2">
	{#each tags as thisTag}
		<li class="space-y-2 py-2">
			<div class="py-2">
				<span class="radial-gradient-bg rounded-md border-4 border-sky-700 p-2 font-mono"
					>{thisTag.name}</span
				>
			</div>
			<div class="ml-4">
				<DocCardStructFields fields={thisTag.data} />
			</div>
			{#if thisTag.doc}
				<div class="docstring ml-4 font-normal text-gray-700 dark:text-gray-400">
					{@html thisTag.doc}
				</div>
			{/if}
		</li>
	{/each}
</ul>
