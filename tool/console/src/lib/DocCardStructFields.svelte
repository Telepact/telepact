<script lang="ts">
	import TypeRef from './TypeRef.svelte';

	export let fields: Record<string, any>;
</script>

{#if Object.keys(fields).length === 0}
	<div class="rounded-lg border border-gray-600 px-4 py-2 text-sm font-medium text-gray-400">
		<span>(empty)</span>
	</div>
{:else}
	<ul
		class="divide-y rounded-lg border border-gray-600 bg-gray-700 text-sm font-medium text-white"
	>
		{#each Object.entries(fields) as [k, v]}
			<li class="flex w-full items-center justify-between border-gray-600 px-4 py-2">
				<div>
					<span class="rounded-sm bg-gray-600 px-2 py-1 font-mono">{k}</span>
					<span class="px-1">:</span>
					<span class="rounded-full py-1">
						<TypeRef types={v} />
					</span>
					{#if k.includes('!')}
						<span class="text-stone-300">(optional)</span>
					{/if}
				</div>
				<div>
					<slot name="field" header={k} />
				</div>
			</li>
		{/each}
	</ul>
{/if}
