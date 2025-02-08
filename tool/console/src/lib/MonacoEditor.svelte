<script lang="ts">
	import { onDestroy, onMount, afterUpdate, createEventDispatcher } from 'svelte';
	import * as monaco from 'monaco-editor';
	import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
	import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker';

	let editor: monaco.editor.IStandaloneCodeEditor;
	let editorElement: HTMLDivElement;

	export let id: string;
	export let json: string;
	export let readOnly: boolean;
	export let allowLinks: boolean = false;
	export let filename: string;
	export let ctrlEnter = () => {};
	export let fullHeight: boolean = true;
	export let lineNumbers: boolean = true;
	export let minimap: boolean = true;

	export const getContent = () => {
		return editor.getValue();
	};

	const calculateEditorHeight = (content: string) => {
		const lineHeight = 20;
		const numberOfLines = content.split('\n').length;
		return numberOfLines * lineHeight + 40; // Add some padding
	};

	const updateEditorHeight = () => {
		const content = editor.getValue();
		const height = calculateEditorHeight(content);
		editorElement.style.height = `${height}px`;
		editor.layout();
	};

	onMount(async () => {
		self.MonacoEnvironment = {
			getWorker: function (_: any, label: string) {
				if (label === 'json') {
					return new jsonWorker();
				}
				return new editorWorker();
			}
		};

		editor = monaco.editor.create(
			editorElement,
			{
				automaticLayout: true,
				theme: 'vs-dark',
				scrollbar: {
					alwaysConsumeMouseWheel: false
				},
				scrollBeyondLastLine: false,
				readOnly: readOnly,
				padding: {
					top: 20,
					bottom: 20
				},
				links: allowLinks,
				glyphMargin: true,
				lineNumbers: lineNumbers ? 'on' : 'off',
				minimap: {
					enabled: minimap
				}
			},
			{
				textModelService: null
			}
		);

		const model = monaco.editor.createModel(
			json,
			'json',
			monaco.Uri.parse(`internal://server/${filename}`)
		);
		editor.setModel(model);

		if (!readOnly) {
			editor.addAction({
				id: id,
				label: 'Enter',
				keybindings: [
					monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
					monaco.KeyMod.WinCtrl | monaco.KeyCode.Enter
				],
				run: () => ctrlEnter()
			});
		}

		if (!fullHeight) {
			updateEditorHeight();
		}
	});

	onDestroy(() => {
		editor.getModel()?.dispose();
		editor?.dispose();
	});

	afterUpdate(() => {
		if (!fullHeight) {
			updateEditorHeight();
		}
	});
</script>

<div class="z-1 relative w-full {fullHeight ? 'h-full' : ''}">
	<div class={fullHeight ? 'h-full' : ''} bind:this={editorElement} />
	<div class="absolute right-0 top-0">
		<slot />
	</div>
</div>
