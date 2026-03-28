import { Client, ClientOptions, Message, Serializer } from 'telepact';

const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
  return serializer.deserialize(serializer.serialize(message));
};

void new Client(adapter, new ClientOptions());
