import keyword
from typing import Awaitable, Callable, TypeVar, Union, Literal, Generic, NoReturn, Never
from dataclasses import dataclass
from typing import cast, ForwardRef
import telepact.Message
import telepact.Client
import telepact.TypedMessage
from typing import Tuple, NamedTuple
from enum import Enum

T = TypeVar('T')
U = TypeVar('U')


def util_let(value: T, f: Callable[[T], U]) -> U:
    return f(value)


class Undefined(Enum):
    Inst = "undefined"

class TaggedValue_(Generic[T, U]):
    tag: T
    value: U

    def __init__(self, tag: T, value: U) -> None:
        self.tag = tag
        self.value = value

class UntypedTaggedValue_:
    tag: str
    value: dict[str, object]

    def __init__(self, tag: str, value: dict[str, object]) -> None:
        self.tag = tag
        self.value = value


class add:
    class Input:
        
        pseudo_json: dict[str, object]

        def __init__(self, pseudo_json: dict[str, object]) -> None:
            self.pseudo_json = pseudo_json

        @staticmethod
        def from_(
            x: 'int',
            y: 'int',
        ) -> 'add.Input':
            input: dict[str, object] = {}
            input["x"] = x
            input["y"] = y

            return add.Input({'fn.add': input})
        
        def x(self) -> 'int':
            return cast(int, self.pseudo_json["fn.add"]["x"])
        
        def y(self) -> 'int':
            return cast(int, self.pseudo_json["fn.add"]["y"])
        
    class Output:
        
        pseudo_json: dict[str, object]

        def __init__(self, pseudo_json: dict[str, object]) -> None:
            self.pseudo_json = pseudo_json
        
        @staticmethod
        def from_Ok_(
            result: 'int',
        ) -> 'add.Output':
            return add.Output({
                "Ok_": add.Output.Ok_.from_(
                            result=result,
                ).pseudo_json
            })
        
        def get_tagged_value(self) -> Union[
                TaggedValue_[Literal["Ok_"], 'add.Output.Ok_'],
                TaggedValue_[Literal["NoMatch_"], UntypedTaggedValue_]]:
            
            tag = next(iter(self.pseudo_json.keys()))
            if tag == "Ok_":
                return TaggedValue_(cast(Literal["Ok_"], "Ok_"), add.Output.Ok_(cast(dict[str, object], self.pseudo_json["Ok_"])))
            else:
                return TaggedValue_(cast(Literal["NoMatch_"], "NoMatch_"), UntypedTaggedValue_(tag, cast(dict[str, object], self.pseudo_json[tag])))

        class Ok_:
            
            pseudo_json: dict[str, object]

            def __init__(self, pseudo_json: dict[str, object]) -> None:
                self.pseudo_json = pseudo_json

            @staticmethod
            def from_(
                result: 'int',
            ) -> 'add.Output.Ok_':
                input: dict[str, object] = {}
                input["result"] = result

                return add.Output.Ok_(input)
            
            def result(self) -> 'int':
                return cast(int, self.pseudo_json["result"])
            

    class Select_:
        pseudo_json: dict[str, object]

        def ok_result(self) -> 'add.Select_':
            result_union = cast(dict[str, object], self.pseudo_json.get("->", {}))

            these_fields = cast(list[object], result_union.get("Ok_", []))
            if 'result' not in these_fields:
                these_fields.append('result')

            result_union["Ok_"] = these_fields

            self.pseudo_json["->"] = result_union
            return self


class Select_:
    pseudo_json: dict[str, object] = {}

    def __init__(self, pseudo_json: dict[str, object]) -> None:
        self.pseudo_json = pseudo_json

    @staticmethod
    def add(self, select: 'add.Select_') -> 'Select_':
        return Select_(select.pseudo_json)

class TypedClient:

    client: telepact.Client

    def __init__(self, client: telepact.Client):
        self.client = client
    
    async def add(self, headers: dict[str, object], input: add.Input) -> telepact.TypedMessage[add.Output]:
        message = await self.client.request(telepact.Message(headers, input.pseudo_json))
        return telepact.TypedMessage(message.headers, add.Output(message.body))
    

class TypedServerHandler:
    async def add(self, headers: dict[str, object], input: add.Input) -> telepact.TypedMessage[add.Output]:
        raise NotImplementedError()
    

    def function_routes(self) -> dict[str, Callable[[str, telepact.Message], Awaitable[telepact.Message]]]:
        return {
            
            "fn.add": self._add_route,
        }
    async def _add_route(self, function_name: str, request_message: telepact.Message) -> telepact.Message:
        argument = request_message.body[function_name]
        response_headers, add_output = await self.add(request_message.headers, add.Input({"fn.add": argument}))
        return telepact.Message(response_headers, add_output.pseudo_json)
    

    async def handler(self, message: telepact.Message) -> telepact.Message:
        function_name = next(iter(message.body.keys()))
        function_route = self.function_routes().get(function_name)
        if function_route is None:
            raise Exception("Unknown function: " + function_name)
        return await function_route(function_name, message)