<script lang="ts">
	export let types: any[];
	let generics = types.slice(1, types.length);
	let typeName = types[0];
	let nullable = typeName.endsWith('?');
	let cleanTypeName = typeName.replace(/\?$/g, '');
	let displayNameSpit = cleanTypeName.split('.');
	let displayName: string;
	if (displayNameSpit.length === 1) {
		displayName = displayNameSpit[0];
	} else {
		let target = displayNameSpit[1];
		if (isNaN(target)) {
			displayName = target;
		} else {
			displayName = `T${target}`;
		}
	}
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
		>{/if}{#if generics.length > 0}&lt;{#each generics as generic, i}<svelte:self
				types={generic}
			/>{#if i < generics.length - 1},&#20;{/if}{/each}&gt;{/if}{#if nullable}?{/if}</span
>
