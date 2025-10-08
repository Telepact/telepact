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
		types: any;
	}

	let { types }: Props = $props();
	let typeName;
	let nullable = false;

	function getTypeInfo(typeData: any): [string, string, any | null] {
		let cleanTypeName;
		let displayName: string;
		let generics: any | null = null;

		if (Array.isArray(typeData)) {
			typeName = "array";
			cleanTypeName = "array";
			displayName = "array";
			generics = typeData[0]
		} else if (typeof typeData === 'object' && typeData !== null) {
			typeName = "object";
			cleanTypeName = "object";
			displayName = "object";
			generics = typeData["string"];
		} else {
			typeName = typeData as string;
			nullable = typeName.endsWith('?');
			cleanTypeName = typeName.replace(/\?$/g, '');
			let displayNameSpit = cleanTypeName.split('.');
			if (displayNameSpit.length === 1) {
				displayName = displayNameSpit[0];
			} else {
				let target = displayNameSpit[1];
				displayName = target;
			}
		}

		return [cleanTypeName, displayName, generics];
	}

	let [cleanTypeName, displayName, generics] = getTypeInfo(types);


	const standardTypes = ['boolean', 'integer', 'number', 'string', 'array', 'object', 'any'];
</script>

<span class="px-0 text-stone-200"
	>{#if standardTypes.includes(cleanTypeName)}<span class="px-0 text-stone-400"
			>{displayName}</span
		>{:else}<a
			href="#{cleanTypeName}"
			class="px-0 hover:underline {cleanTypeName.startsWith('struct')
				? 'text-sky-400'
				: 'text-emerald-500'}">{displayName}</a
		>{/if}{#if generics != null}&lt;<TypeRef
				types={generics}
			/>&gt;{/if}{#if nullable}?{/if}</span
>
