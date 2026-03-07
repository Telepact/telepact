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

import { useState } from 'react';
import MonacoEditor from './MonacoEditor';

export default function Example(props: { schemaKey: string; generate: () => string }) {
	const [showExample, setShowExample] = useState(false);
	const [randomSeed, setRandomSeed] = useState(1);

	const toggleShowExample = () => setShowExample((v) => !v);
	const incrementRandomSeed = () => setRandomSeed((v) => v + 1);

	return (
		<>
			<div className="flex items-center justify-center space-x-2">
				<button onClick={toggleShowExample} className="group mt-2 flex items-center rounded-lg hover:underline">
					<h6 className={`rounded-md p-2 ${showExample ? 'border border-slate-500 font-bold' : ''}`}>
						{showExample ? 'Hide Example' : 'Example'}
					</h6>
				</button>
				{showExample ? (
					<button
						onClick={incrementRandomSeed}
						className="group mt-2 flex items-center rounded-lg hover:underline"
					>
						<h6 className="rounded-md border border-slate-500 p-2 font-bold">Regenerate</h6>
					</button>
				) : null}
			</div>
			{showExample ? (
				<div className="py-2">
					<MonacoEditor
						key={randomSeed}
						id={props.schemaKey}
						readOnly={true}
						json={props.generate()}
						allowLinks={false}
						filename={`${props.schemaKey}.json`}
						ariaLabel={`${props.schemaKey}.example`}
						fullHeight={false}
						lineNumbers={false}
						minimap={false}
					/>
				</div>
			) : null}
		</>
	);
}

