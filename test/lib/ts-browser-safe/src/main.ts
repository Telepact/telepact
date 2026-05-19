//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Client, ClientOptions, Message, Serializer, TelepactSchema, type FsModule, type PathModule } from 'telepact';
import { TypedClient, greet } from './gen/genTypes.js';

const schema = TelepactSchema.fromJson('[]');

const fsModule: FsModule | null = null;
const pathModule: PathModule | null = null;
const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
  return serializer.deserialize(serializer.serialize(message));
};
const typedClient = new TypedClient(new Client(adapter, new ClientOptions()));
const input = greet.Input.from({ subject: 'browser-safe' });

console.log(schema.full.length, fsModule, pathModule, typedClient, input.subject());
