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

