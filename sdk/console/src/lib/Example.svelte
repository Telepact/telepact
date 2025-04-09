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
	import MonacoEditor from './MonacoEditor.svelte';

	interface Props {
		schemaKey: string;
		generate: () => string;
	}

	let { schemaKey, generate }: Props = $props();

	let showExample: boolean = $state(false);
	let randomSeed: number = $state(1);

	function incrementRandomSeed() {
		randomSeed += 1;
	}

	function toggleShowExample() {
		showExample = !showExample;
	}
</script>

<div class="flex items-center justify-center space-x-2">
	<button
		onclick={toggleShowExample}
		class="group mt-2 flex items-center rounded-lg hover:underline"
	>
		<h6 class="rounded-md p-2 {showExample ? 'border border-slate-500 font-bold' : ''}">
			{showExample ? 'Hide Example' : 'Example'}
		</h6>
	</button>
	{#if showExample}
		<button
			onclick={incrementRandomSeed}
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
