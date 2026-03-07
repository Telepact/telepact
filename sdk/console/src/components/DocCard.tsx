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

import { useEffect, useMemo, useState } from 'react';
import DocCardEnumTags from './DocCardEnumTags';
import DocCardStructFields from './DocCardStructFields';
import Example from './Example';
import MonacoEditor from './MonacoEditor';
import TypeRef from './TypeRef';
import MockIcon from './icons/MockIcon';
import {
	generateExample,
	generateFnResultExample,
	generateHeaderExample,
	isFnTypeData,
	isHeaderData,
	isUnionTagTypeData,
	markdownHtml,
	type HeaderData,
	type TypeData
} from '../lib/console';
import type { TelepactSchema } from '../lib/telepact/index.esm.js';

export default function DocCard(props: {
	entry: TypeData;
	telepactSchema: TelepactSchema;
	navigate: (url: string) => void;
}) {
	const { entry, telepactSchema, navigate } = props;

	const schemaKey = entry.name;
	const data = entry.data;

	const description = useMemo(() => markdownHtml(entry as any), [entry]);

	const [showResultExample, setShowResultExample] = useState(false);
	const [includeErrorsInExample, setIncludeErrorsInExample] = useState(false);
	const [randomSeed, setRandomSeed] = useState(1);

	const applyFunctionToExample = () => {
		const q = new URLSearchParams(window.location.search);
		q.set('v', 'md');
		q.set('mf', schemaKey);
		navigate(`?${q.toString()}#${schemaKey}`);
	};

	const toggleHeaderForExample = (header: string) => {
		const q = new URLSearchParams(window.location.search);
		const existingHeaders = (q.get('mh') ?? '')
			.split(',')
			.map((h) => h.trim())
			.filter((h) => h !== '');
		const newHeaders = existingHeaders.includes(header)
			? existingHeaders.filter((h) => h !== header)
			: [...existingHeaders, header];
		q.set('mh', newHeaders.join(','));
		navigate(`?${q.toString()}#${schemaKey}`);
	};

	useEffect(() => {
		const id = window.location.hash?.replace('#', '');
		if (id && id === schemaKey) {
			document.getElementById(schemaKey)?.scrollIntoView();
		}
	}, [schemaKey]);

	const badgeClass = useMemo(() => {
		if (schemaKey.startsWith('fn')) return 'bg-amber-500 dark:bg-amber-700';
		if (schemaKey.startsWith('struct')) return 'bg-sky-500 dark:bg-sky-700';
		if (schemaKey.startsWith('union')) return 'bg-green-500 dark:bg-green-700';
		if (schemaKey.startsWith('errors')) return 'bg-rose-500 dark:bg-rose-800';
		if (schemaKey.startsWith('info')) return 'bg-slate-300 dark:bg-slate-600';
		return 'bg-gray-200 dark:bg-gray-700';
	}, [schemaKey]);

	return (
		<section
			id={schemaKey}
			aria-label={schemaKey}
			className="mb-2 rounded-lg border border-gray-300 bg-white p-6 shadow dark:border-gray-700 dark:bg-gray-800"
		>
			<div className="flex w-full items-center pb-4">
				<a href={`#${schemaKey}`}>
					<h5
						className={`rounded-md px-2 py-1 font-mono text-2xl font-bold tracking-tight text-gray-900 dark:text-white ${badgeClass}`}
					>
						{schemaKey}
					</h5>
				</a>
				{isFnTypeData(data) ? (
					<>
						<span className="grow" />
						<div>
							<button onClick={applyFunctionToExample} className="group flex items-center space-x-2 py-2">
								<span className="group-hover:underline">Simulate</span>
								<div className="rounded-lg p-1 group-hover:bg-sky-700 group-hover:text-cyan-300">
									<MockIcon />
								</div>
							</button>
						</div>
					</>
				) : null}
			</div>

			<div>
				{schemaKey.startsWith('struct') ? (
					<>
						<DocCardStructFields fields={entry.data as Record<string, any>} />
						{description ? (
							<div className="pt-4 prose dark:prose-invert" dangerouslySetInnerHTML={{ __html: description }} />
						) : null}
						<Example schemaKey={schemaKey} generate={() => generateExample(schemaKey, telepactSchema)} />
					</>
				) : isFnTypeData(data) ? (
					<div className="space-y-1">
						<section aria-label="Arguments">
							<DocCardStructFields fields={data.args} />
							{description ? (
								<div
									className="pt-4 prose dark:prose-invert"
									dangerouslySetInnerHTML={{ __html: description }}
								/>
							) : null}
							<Example schemaKey={schemaKey} generate={() => generateExample(schemaKey, telepactSchema)} />
						</section>

						<section aria-label="Result">
							<div>
								<span className="text-3xl text-emerald-500">→</span>
							</div>

							<DocCardEnumTags tags={data.results} />

							<div className="flex items-center justify-center space-x-2">
								<button
									onClick={() => setShowResultExample((v) => !v)}
									className="group mt-2 flex items-center rounded-lg hover:underline"
								>
									<h6
										className={`rounded-md p-2 ${showResultExample ? 'border border-slate-500 font-bold' : ''}`}
									>
										{showResultExample ? 'Hide Example' : 'Example'}
									</h6>
								</button>
								{showResultExample ? (
									<>
										<button
											onClick={() => setRandomSeed((v) => v + 1)}
											className="group mt-2 flex items-center rounded-lg hover:underline"
										>
											<h6 className="rounded-md border border-slate-500 p-2 font-bold">Regenerate</h6>
										</button>
										<label>
											<input
												type="checkbox"
												className="mr-1"
												checked={includeErrorsInExample}
												onChange={(e) => setIncludeErrorsInExample(e.target.checked)}
											/>{' '}
											Include Errors
										</label>
									</>
								) : null}
							</div>

							{showResultExample ? (
								<div className="py-2">
									<MonacoEditor
										key={randomSeed}
										id={schemaKey}
										readOnly={true}
										json={generateFnResultExample(
											schemaKey,
											telepactSchema,
											includeErrorsInExample ? null : { Ok_: {} },
											!includeErrorsInExample
										)}
										allowLinks={false}
										filename={`${schemaKey}.result.json`}
										ariaLabel={`${schemaKey}.result.example`}
										fullHeight={false}
										lineNumbers={false}
										minimap={false}
									/>
								</div>
							) : null}

							{(data.inheritedErrors?.length ?? 0) > 0 ? (
								<div className="pt-4">
									<div className="border-t border-gray-500 pt-2">
										<h6 className="font-bold tracking-tight">Also includes:</h6>
										<ul>
											{data.inheritedErrors.map((inheritedError) => (
												<ul key={inheritedError}>
													<a
														href={`#${inheritedError}`}
														className="text-md pl-4 text-sky-400 hover:underline"
													>
														{inheritedError}
													</a>
												</ul>
											))}
										</ul>
									</div>
								</div>
							) : null}
						</section>
					</div>
				) : isUnionTagTypeData(data) ? (
					<>
						{description ? (
							<div className="pb-2 prose dark:prose-invert" dangerouslySetInnerHTML={{ __html: description }} />
						) : null}
						<div className="space-y-2">
							<DocCardEnumTags tags={data} />
						</div>
						<Example schemaKey={schemaKey} generate={() => generateExample(schemaKey, telepactSchema)} />
					</>
				) : isHeaderData(data) ? (
					<div>
						{description ? (
							<div className="prose dark:prose-invert" dangerouslySetInnerHTML={{ __html: description }} />
						) : null}

						<DocCardStructFields
							fields={(data as HeaderData).requestData}
							field={({ header }) => (
								<button
									onClick={() => toggleHeaderForExample(header)}
									className="group flex items-center space-x-2"
								>
									<span className="group-hover:underline">Simulate</span>
									<div className="rounded-lg px-1 group-hover:bg-sky-700 group-hover:text-cyan-300">
										<MockIcon />
									</div>
								</button>
							)}
						/>

						{Object.keys((data as HeaderData).requestData).length > 0 ? (
							<Example
								schemaKey={`request.${schemaKey}`}
								generate={() =>
									generateHeaderExample('request', Object.keys((data as HeaderData).requestData), telepactSchema)
								}
							/>
						) : null}

						<div className="pl-4">
							<span className="text-3xl text-emerald-500">→</span>
						</div>

						<DocCardStructFields fields={(data as HeaderData).responseData} />

						{Object.keys((data as HeaderData).responseData).length > 0 ? (
							<Example
								schemaKey={`response.${schemaKey}`}
								generate={() =>
									generateHeaderExample('response', Object.keys((data as HeaderData).responseData), telepactSchema)
								}
							/>
						) : null}
					</div>
				) : description ? (
					<div className="prose dark:prose-invert" dangerouslySetInnerHTML={{ __html: description }} />
				) : null}
			</div>
		</section>
	);
}
