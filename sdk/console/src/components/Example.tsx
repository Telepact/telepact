//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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

