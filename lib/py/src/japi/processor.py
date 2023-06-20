from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass


class JapiParseError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass
class Options:
    on_error: Callable[[Exception], None] = lambda e: None
    serializer: Serializer = DefaultSerializer()

    def set_on_error(self, on_error: Callable[[Exception], None]) -> 'Options':
        self.on_error = on_error
        return self

    def set_serializer(self, serializer: Serializer) -> 'Options':
        self.serializer = serializer
        return self


class Processor:
    def __init__(self, handler: Handler, api_description_json: str, options: Optional[Options] = None) -> None:
        options = options or Options()
        description = InternalParse.new_japi(api_description_json)
        self.api_description = description.parsed()
        self.original_api_description = description.original()
        self.serializer = options.serializer

        internal_description = InternalParse.new_japi(InternalJapi.JSON)

        self.api_description.update(internal_description.parsed())
        self.original_api_description.update(internal_description.original())

        self.handler = handler
        self.internal_handler = InternalJapi.build(
            self.original_api_description)
        self.on_error = options.on_error

        self.binary_encoder = InternalBinaryEncoderBuilder.build(
            self.api_description)

    def process(self, input_japi_message_payload: bytes) -> bytes:
        return InternalProcess.process(
            input_japi_message_payload,
            self.serializer,
            self.on_error,
            self.binary_encoder,
            self.api_description,
            self.internal_handler,
            self.handler
        )
