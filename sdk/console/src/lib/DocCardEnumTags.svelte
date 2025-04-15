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
	import DocCardStructFields from './DocCardStructFields.svelte';
	import { markdownHtml, type UnionTagTypeData } from '$lib';

	interface Props {
		tags: UnionTagTypeData[];
	}

	let { tags }: Props = $props();
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
				<div class="ml-4 prose prose-invert">
					{@html markdownHtml(thisTag)}
				</div>
			{/if}
		</li>
	{/each}
</ul>
