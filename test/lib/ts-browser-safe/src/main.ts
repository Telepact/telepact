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

import { Client, ClientOptions, Message, Serializer, TelepactSchema, type FsModule, type PathModule } from 'telepact';
import { TypedClient, greet } from '../../../../example/ts-codegen/gen/genTypes.js';

const schema = TelepactSchema.fromJson('[]');

const fsModule: FsModule | null = null;
const pathModule: PathModule | null = null;
const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
  return serializer.deserialize(serializer.serialize(message));
};
const typedClient = new TypedClient(new Client(adapter, new ClientOptions()));
const input = greet.Input.from({ subject: 'browser-safe' });

console.log(schema.full.length, fsModule, pathModule, typedClient, input.subject());
