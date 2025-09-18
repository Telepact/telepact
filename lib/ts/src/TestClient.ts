import { Client } from "./Client";
import { Message } from "./Message";
import { isSubMap } from "./internal/mock/IsSubMap";

export class TestClient {

    client: Client;

    constructor(client: Client) {
        this.client = client;
    }

    async assertRequest(requestMessage: Message, expectedPseudoJsonBody: Record<string, unknown>, expectMatch: boolean): Promise<Record<string, unknown>> {
        const result = await this.client.request(requestMessage);

        const didMatch = isSubMap(expectedPseudoJsonBody, result.body);

        if (expectMatch) {
            if (!didMatch) {
                throw new Error("Expected response body to match");
            }
            return result.body;
        } else {
            if (didMatch) {
                throw new Error("Expected response body to not match");
            }
            return expectedPseudoJsonBody;
        }
    }
}