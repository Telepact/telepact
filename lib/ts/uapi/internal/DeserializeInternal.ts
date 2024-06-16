import { Serialization } from 'uapi/Serialization';
import { BinaryEncoder } from 'uapi/internal/binary/BinaryEncoder';
import { Message } from 'uapi/Message';
import { InvalidMessage } from 'uapi/internal/validation/InvalidMessage';
import { InvalidMessageBody } from 'uapi/internal/validation/InvalidMessageBody';

export function deserializeInternal(
    messageBytes: Buffer,
    serializer: Serialization,
    binaryEncoder: BinaryEncoder,
): Message {
    let messageAsPseudoJson: any;
    let isMsgPack: boolean;

    try {
        if (messageBytes[0] === 0x92) {
            // MsgPack
            isMsgPack = true;
            messageAsPseudoJson = serializer.fromMsgpack(messageBytes);
        } else {
            isMsgPack = false;
            messageAsPseudoJson = serializer.fromJson(messageBytes);
        }
    } catch (e) {
        throw new InvalidMessage();
    }

    if (!Array.isArray(messageAsPseudoJson)) {
        throw new InvalidMessage();
    }

    const messageAsPseudoJsonList: any[] = messageAsPseudoJson;

    if (messageAsPseudoJsonList.length !== 2) {
        throw new InvalidMessage();
    }

    let finalMessageAsPseudoJsonList: any[];
    if (isMsgPack) {
        finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
    } else {
        finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
    }

    if (typeof finalMessageAsPseudoJsonList[0] !== 'object') {
        throw new InvalidMessage();
    }

    const headers: { [key: string]: any } = finalMessageAsPseudoJsonList[0];

    if (typeof finalMessageAsPseudoJsonList[1] !== 'object') {
        throw new InvalidMessage();
    }

    const body: { [key: string]: any } = finalMessageAsPseudoJsonList[1];

    if (Object.keys(body).length !== 1) {
        throw new InvalidMessageBody();
    }

    if (typeof Object.values(body)[0] !== 'object') {
        throw new InvalidMessageBody();
    }

    return new Message(headers, body);
}
