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
	export let ariaLabel: string;

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

		const prefersDark = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
		const initialTheme = prefersDark ? 'vs-dark' : (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'vs' : 'vs-dark');

		editor = monaco.editor.create(
			editorElement,
			{
				automaticLayout: true,
				theme: initialTheme,
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
				},
				ariaLabel: ariaLabel,
				ariaRequired: true
			},
			{
				textModelService: null
			}
		);

		// React to OS theme changes
		if (typeof window !== 'undefined' && window.matchMedia) {
			const mql = window.matchMedia('(prefers-color-scheme: dark)');
			const applyTheme = (isDark: boolean) => {
				monaco.editor.setTheme(isDark ? 'vs-dark' : 'vs');
			};
			applyTheme(mql.matches);
			mql.addEventListener('change', (e) => applyTheme(e.matches));
		}

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
	<div class={fullHeight ? 'h-full' : ''} bind:this={editorElement}></div>
	<div class="absolute right-0 top-0">
		<slot />
	</div>
</div>
