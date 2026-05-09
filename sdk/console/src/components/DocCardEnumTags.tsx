//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import DocCardStructFields from './DocCardStructFields';
import { markdownHtml, type UnionTagTypeData } from '../lib/console';

export default function DocCardEnumTags(props: { tags: UnionTagTypeData[] }) {
	return (
		<ul className="space-y-2">
			{props.tags.map((tag) => (
				<li key={tag.name} className="space-y-2 py-2">
					<div className="py-2">
						<span className="radial-gradient-bg rounded-md border-4 border-sky-700 p-2 font-mono">
							{tag.name}
						</span>
					</div>
					<div className="ml-4">
						<DocCardStructFields fields={tag.data} />
					</div>
					{tag.doc ? (
						<div
							className="ml-4 prose dark:prose-invert"
							dangerouslySetInnerHTML={{ __html: markdownHtml(tag) }}
						/>
					) : null}
				</li>
			))}
		</ul>
	);
}

