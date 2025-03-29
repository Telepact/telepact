import { Base64Encoder } from "./Base64Encoder";
import { serverBase64Encode } from "./ServerBase64Encode";

export class ServerBase64Encoder extends Base64Encoder {
    decode(message: object[]): object[] {
        // Server manually runs its decode logic after validation
        return message;
    }

    encode(message: object[]): object[] {
        serverBase64Encode(message);
        return message;
    }
}