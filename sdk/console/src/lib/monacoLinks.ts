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

import * as monaco from 'monaco-editor';
import 'monaco-editor/esm/vs/language/typescript/monaco.contribution';

type RequestLinkHandler = (requestBody: unknown) => void;

let registered = false;
let handler: RequestLinkHandler | null = null;
const monacoLanguagesWithTypescript = monaco.languages as typeof monaco.languages & {
	typescript: {
		typescriptDefaults: {
			setEagerModelSync: (value: boolean) => void;
		};
	};
};

export function setTelepactRequestLinkHandler(next: RequestLinkHandler | null) {
	handler = next;
}

export function ensureTelepactJsonLinksRegistered() {
	if (registered) return;
	registered = true;

	monacoLanguagesWithTypescript.typescript.typescriptDefaults.setEagerModelSync(true);

	monaco.languages.registerLinkProvider('json', {
		provideLinks: (model) => {
			const matches = model.findMatches('\\{[\\s\\n]*"fn\\..*":[\\s\\n]*\\{', false, true, false, '', false, undefined);

			const links = matches
				.map((m) => {
					// @ts-expect-error - Monaco internal API
					const end: [monaco.Range, monaco.Range] = model._bracketPairs.matchBracket(
						new monaco.Position(m.range.startLineNumber, m.range.startColumn)
					);

					if (!end) return null;

					const range = new monaco.Range(
						m.range.startLineNumber,
						m.range.startColumn,
						end[1].endLineNumber,
						end[1].endColumn
					);

					const val = model.getValueInRange(range);
					return { range, val };
				})
				.filter((e): e is { range: monaco.Range; val: string } => e !== null);

			return { links: links as any };
		},
		resolveLink: (link) => {
			const val = (link as any).val;
			if (typeof val === 'string') {
				try {
					const requestBody = JSON.parse(val);
					handler?.(requestBody);
				} catch {
					// ignore
				}
			}

			return { range: link.range };
		}
	});

	// A second provider to ensure Monaco doesn't try to navigate away.
	monaco.languages.registerLinkProvider('json', {
		provideLinks: () => ({ links: [] }),
		resolveLink: (link) => ({ range: link.range })
	});
}
