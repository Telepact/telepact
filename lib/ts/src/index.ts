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

export * from './RandomGenerator';
export * from './Client';
export * from './Server';
export * from './MockServer';
export * from './Message';
export * from './Serializer';
export * from './DefaultClientBinaryStrategy';
export * from './ClientBinaryStrategy';
export * from './SerializationError';
export * from './Serialization';
export * from './TelepactSchema';
export * from './MockTelepactSchema';
export * from './TelepactSchemaParseError';
export * from './TelepactSchemaFiles';
export * from './fileSystem';
export { default as jsonSchema } from '../inc/json-schema.json';

import { GenerateContext } from './internal/generation/GenerateContext';
import { VFn } from './internal/types/VFn';

export const _internal = {
    GenerateContext,
    VFn: VFn,
};
