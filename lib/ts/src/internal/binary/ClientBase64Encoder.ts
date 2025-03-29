import { Base64Encoder } from "../../internal/binary/Base64Encoder";
import { clientBase64Decode } from "../../internal/binary/ClientBase64Decode";
import { clientBase64Encode } from "../../internal/binary/ClientBase64Encode";

export class ClientBase64Encoder extends Base64Encoder {
    decode(message: object[]): object[] {
        clientBase64Decode(message);
        return message;
    }

    encode(message: object[]): object[] {
        clientBase64Encode(message);
        return message;
    }
}