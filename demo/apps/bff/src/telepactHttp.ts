import { Client, ClientOptions, Message } from "telepact";

export interface TelepactRequester {
  request: (body: Record<string, unknown>, headers?: Record<string, unknown>) => Promise<Message>;
}

export function createTelepactRequester(baseUrl: string): TelepactRequester {
  const options = new ClientOptions();
  options.alwaysSendJson = true;

  const client = new Client(async (message, serializer) => {
    const response = await fetch(baseUrl, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: serializer.serialize(message),
    });
    const bytes = new Uint8Array(await response.arrayBuffer());
    return serializer.deserialize(bytes);
  }, options);

  return {
    request: async (body, headers = {}) => client.request(new Message(headers, body)),
  };
}
