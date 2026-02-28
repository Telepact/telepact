//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import * as monaco from 'monaco-editor';
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker';

export type MonacoEditorHandle = {
	getContent: () => string;
};

export type MonacoEditorProps = {
	id: string;
	json: string;
	readOnly: boolean;
	allowLinks?: boolean;
	filename: string;
	ctrlEnter?: () => void;
	fullHeight?: boolean;
	lineNumbers?: boolean;
	minimap?: boolean;
	ariaLabel: string;
};

const MonacoEditor = forwardRef<MonacoEditorHandle, MonacoEditorProps>(function MonacoEditor(props, ref) {
	const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
	const editorElementRef = useRef<HTMLDivElement | null>(null);

	useImperativeHandle(
		ref,
		() => ({
			getContent: () => editorRef.current?.getValue() ?? ''
		}),
		[]
	);

	const calculateEditorHeight = (content: string) => {
		const lineHeight = 20;
		const numberOfLines = content.split('\n').length;
		return numberOfLines * lineHeight + 40;
	};

	const updateEditorHeight = () => {
		const editor = editorRef.current;
		const editorElement = editorElementRef.current;
		if (!editor || !editorElement) return;
		const content = editor.getValue();
		const height = calculateEditorHeight(content);
		editorElement.style.height = `${height}px`;
		editor.layout();
	};

	useEffect(() => {
		const editorElement = editorElementRef.current;
		if (!editorElement) return;

		(self as any).MonacoEnvironment = {
			getWorker: function (_: any, label: string) {
				if (label === 'json') {
					return new jsonWorker();
				}
				return new editorWorker();
			}
		};

		const prefersDark =
			typeof window !== 'undefined' &&
			!!window.matchMedia &&
			window.matchMedia('(prefers-color-scheme: dark)').matches;
		const prefersLight =
			typeof window !== 'undefined' &&
			!!window.matchMedia &&
			window.matchMedia('(prefers-color-scheme: light)').matches;
		const initialTheme = prefersDark ? 'vs-dark' : prefersLight ? 'vs' : 'vs-dark';

		const editor = monaco.editor.create(
			editorElement,
			{
				automaticLayout: true,
				theme: initialTheme,
				scrollbar: {
					alwaysConsumeMouseWheel: false
				},
				scrollBeyondLastLine: false,
				readOnly: props.readOnly,
				padding: {
					top: 20,
					bottom: 20
				},
				links: props.allowLinks ?? false,
				glyphMargin: true,
				lineNumbers: (props.lineNumbers ?? true) ? 'on' : 'off',
				minimap: {
					enabled: props.minimap ?? true
				},
				ariaLabel: props.ariaLabel,
				ariaRequired: true
			},
			{
				textModelService: null
			}
		);
		editorRef.current = editor;

		let themeListener: ((e: MediaQueryListEvent) => void) | null = null;
		let mql: MediaQueryList | null = null;

		if (typeof window !== 'undefined' && window.matchMedia) {
			mql = window.matchMedia('(prefers-color-scheme: dark)');
			const applyTheme = (isDark: boolean) => {
				monaco.editor.setTheme(isDark ? 'vs-dark' : 'vs');
			};
			applyTheme(mql.matches);
			themeListener = (e) => applyTheme(e.matches);
			mql.addEventListener('change', themeListener);
		}

		const model = monaco.editor.createModel(
			props.json,
			'json',
			monaco.Uri.parse(`internal://server/${props.filename}`)
		);
		editor.setModel(model);

		if (!props.readOnly) {
			editor.addAction({
				id: props.id,
				label: 'Enter',
				keybindings: [
					monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
					monaco.KeyMod.WinCtrl | monaco.KeyCode.Enter
				],
				run: () => props.ctrlEnter?.()
			});
		}

		let heightSubscription: monaco.IDisposable | null = null;
		if (!(props.fullHeight ?? true)) {
			updateEditorHeight();
			heightSubscription = editor.onDidChangeModelContent(() => {
				updateEditorHeight();
			});
		}

		return () => {
			heightSubscription?.dispose();
			if (mql && themeListener) {
				mql.removeEventListener('change', themeListener);
			}
			editor.getModel()?.dispose();
			editor.dispose();
			editorRef.current = null;
		};
		// Intentionally mount-only. Parent components should use `key=...` to reset.
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	return (
		<div className={`z-1 relative w-full ${(props.fullHeight ?? true) ? 'h-full' : ''}`}>
			<div ref={editorElementRef} className={(props.fullHeight ?? true) ? 'h-full' : ''} />
		</div>
	);
});

export default MonacoEditor;
