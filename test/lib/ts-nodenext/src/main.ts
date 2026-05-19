//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Client, ClientOptions, Message, Serializer } from 'telepact';
import { TypedClient, greet } from './gen/genTypes.js';

const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
  return serializer.deserialize(serializer.serialize(message));
};

const client = new TypedClient(new Client(adapter, new ClientOptions()));
const input = greet.Input.from({ subject: 'nodenext' });

void [client, input];
