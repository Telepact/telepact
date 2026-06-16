//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import * as monaco from 'monaco-editor';

type RequestLinkHandler = (requestBody: unknown) => void;

let registered = false;
let handler: RequestLinkHandler | null = null;

export function setTelepactRequestLinkHandler(next: RequestLinkHandler | null) {
	handler = next;
}

export function ensureTelepactJsonLinksRegistered() {
	if (registered) return;
	registered = true;

	monaco.typescript.typescriptDefaults.setEagerModelSync(true);

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
