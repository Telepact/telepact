from typing import cast, TYPE_CHECKING

from ..Message import Message
from ..internal.validation.InvalidMessage import InvalidMessage
from ..internal.validation.InvalidMessageBody import InvalidMessageBody

if TYPE_CHECKING:
    from ..Serialization import Serialization
    from ..internal.binary.BinaryEncoder import BinaryEncoder


def deserialize_internal(message_bytes: bytes, serializer: 'Serialization',
                         binary_encoder: 'BinaryEncoder') -> 'Message':
    message_as_pseudo_json: object
    is_msg_pack: bool

    try:
        if message_bytes[0] == 0x92:  # MsgPack
            is_msg_pack = True
            message_as_pseudo_json = serializer.from_msgpack(message_bytes)
        else:
            is_msg_pack = False
            message_as_pseudo_json = serializer.from_json(message_bytes)
    except Exception as e:
        raise InvalidMessage() from e

    if not isinstance(message_as_pseudo_json, list):
        raise InvalidMessage()

    message_as_pseudo_json_list = cast(list[object], message_as_pseudo_json)

    if len(message_as_pseudo_json_list) != 2:
        raise InvalidMessage()

    final_message_as_pseudo_json_list: list[object]
    if is_msg_pack:
        final_message_as_pseudo_json_list = binary_encoder.decode(
            message_as_pseudo_json_list)
    else:
        final_message_as_pseudo_json_list = message_as_pseudo_json_list

    if not isinstance(final_message_as_pseudo_json_list[0], dict):
        raise InvalidMessage()

    headers = cast(dict[str, object], final_message_as_pseudo_json_list[0])

    if not isinstance(final_message_as_pseudo_json_list[1], dict):
        raise InvalidMessage()

    body = cast(dict[str, object], final_message_as_pseudo_json_list[1])

    if len(body) != 1:
        raise InvalidMessageBody()

    if not isinstance(next(iter(body.values())), dict):
        raise InvalidMessageBody()

    return Message(headers, body)
