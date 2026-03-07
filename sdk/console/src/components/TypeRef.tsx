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

const standardTypes = ['boolean', 'integer', 'number', 'string', 'array', 'object', 'any'];

function getTypeInfo(typeData: unknown): { cleanTypeName: string; displayName: string; generics: any | null; nullable: boolean } {
	if (Array.isArray(typeData)) {
		return { cleanTypeName: 'array', displayName: 'array', generics: typeData[0], nullable: false };
	}
	if (typeof typeData === 'object' && typeData !== null) {
		const asRecord = typeData as Record<string, any>;
		return { cleanTypeName: 'object', displayName: 'object', generics: asRecord['string'], nullable: false };
	}

	const typeName = String(typeData);
	const nullable = typeName.endsWith('?');
	const cleanTypeName = typeName.replace(/\?$/g, '');
	const displayTokens = cleanTypeName.split('.');
	const displayName = displayTokens.length === 1 ? displayTokens[0] : displayTokens[1] ?? cleanTypeName;

	return { cleanTypeName, displayName, generics: null, nullable };
}

export default function TypeRef(props: { types: any }) {
	const { cleanTypeName, displayName, generics, nullable } = getTypeInfo(props.types);
	const isStandard = standardTypes.includes(cleanTypeName);

	return (
		<span className="px-0 text-stone-200">
			{isStandard ? (
				<span className="px-0 text-stone-400">{displayName}</span>
			) : (
				<a
					href={`#${cleanTypeName}`}
					className={`px-0 hover:underline ${cleanTypeName.startsWith('struct') ? 'text-sky-400' : 'text-emerald-500'}`}
				>
					{displayName}
				</a>
			)}
			{generics != null ? (
				<>
					&lt;<TypeRef types={generics} />&gt;
				</>
			) : null}
			{nullable ? '?' : null}
		</span>
	);
}

