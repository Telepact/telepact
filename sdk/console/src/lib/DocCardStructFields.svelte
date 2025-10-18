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
	import TypeRef from './TypeRef.svelte';

	interface Props {
		fields: Record<string, any>;
		field?: import('svelte').Snippet<[any]>;
	}

	let { fields, field }: Props = $props();
</script>

{#if Object.keys(fields).length === 0}
	<div class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-400">
		<span>(empty)</span>
	</div>
{:else}
	<ul
		class="divide-y rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm font-medium text-gray-900 dark:text-white"
	>
		{#each Object.entries(fields) as [k, v]}
			<li class="flex w-full items-center justify-between border-gray-200 dark:border-gray-600 px-4 py-2">
				<div>
					<span class="rounded-sm bg-gray-200 dark:bg-gray-600 px-2 py-1 font-mono">{k}</span>
					<span class="px-1">:</span>
					<span class="rounded-full py-1">
						<TypeRef types={v} />
					</span>
					{#if k.includes('!')}
						<span class="text-stone-600 dark:text-stone-300">(optional)</span>
					{/if}
				</div>
				<div>
					{@render field?.({ header: k, })}
				</div>
			</li>
		{/each}
	</ul>
{/if}
