from typing import List, Dict, Any
from uapi import Message, Serialization
from uapi.internal.binary import BinaryEncoder
from uapi.internal.validation import InvalidMessage, InvalidMessageBody


def deserialize_internal(message_bytes: bytes, serializer: Serialization,
                         binary_encoder: BinaryEncoder) -> Message:
    message_as_pseudo_json: Any
    is_msg_pack: bool

    try:
        if message_bytes[0] == 0x92:  # MsgPack
            is_msg_pack = True
            message_as_pseudo_json = serializer.from_msg_pack(message_bytes)
        else:
            is_msg_pack = False
            message_as_pseudo_json = serializer.from_json(message_bytes)
    except Exception as e:
        raise InvalidMessage(str(e))

    if not isinstance(message_as_pseudo_json, list):
        raise InvalidMessage()

    message_as_pseudo_json_list = cast(List[Any], message_as_pseudo_json)

    if len(message_as_pseudo_json_list) != 2:
        raise InvalidMessage()

    final_message_as_pseudo_json_list: List[Any]
    if is_msg_pack:
        final_message_as_pseudo_json_list = binary_encoder.decode(
            message_as_pseudo_json_list)
    else:
        final_message_as_pseudo_json_list = message_as_pseudo_json_list

    if not isinstance(final_message_as_pseudo_json_list[0], dict):
        raise InvalidMessage()

    headers = cast(Dict[str, Any], final_message_as_pseudo_json_list[0])

    if not isinstance(final_message_as_pseudo_json_list[1], dict):
        raise InvalidMessage()

    body = cast(Dict[str, Any], final_message_as_pseudo_json_list[1])

    if len(body) != 1:
        raise InvalidMessageBody()

    if not isinstance(next(iter(body.values())), dict):
        raise InvalidMessageBody()

    return Message(headers, body)
