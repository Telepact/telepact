//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import TypeRef from './TypeRef';
import type { ReactNode } from 'react';

export default function DocCardStructFields(props: {
	fields: Record<string, any>;
	field?: (args: { header: string }) => ReactNode;
}) {
	if (Object.keys(props.fields).length === 0) {
		return (
			<div className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 dark:border-gray-600 dark:text-gray-400">
				<span>(empty)</span>
			</div>
		);
	}

	return (
		<ul className="divide-y rounded-lg border border-gray-300 bg-gray-50 text-sm font-medium text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-white">
			{Object.entries(props.fields).map(([k, v]) => (
				<li
					key={k}
					className="flex w-full items-center justify-between border-gray-200 px-4 py-2 dark:border-gray-600"
				>
					<div>
						<span className="rounded-sm bg-gray-200 px-2 py-1 font-mono dark:bg-gray-600">
							{k}
						</span>
						<span className="px-1">:</span>
						<span className="rounded-full py-1">
							<TypeRef types={v} />
						</span>
						{k.includes('!') ? (
							<span className="text-stone-600 dark:text-stone-300">(optional)</span>
						) : null}
					</div>
					<div>{props.field ? props.field({ header: k }) : null}</div>
				</li>
			))}
		</ul>
	);
}
