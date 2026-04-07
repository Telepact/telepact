#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING, cast

from ...Message import Message
from ...internal.mock.MockInvocation import MockInvocation
from ...internal.mock.MockStub import MockStub

if TYPE_CHECKING:
    from ...RandomGenerator import RandomGenerator
    from ...TelepactSchema import TelepactSchema


async def mock_handle(request_message: 'Message', stubs: list['MockStub'], invocations: list['MockInvocation'],
                      random: 'RandomGenerator', telepact_schema: 'TelepactSchema', enable_generated_default_stub: bool,
                      enable_optional_field_generation: bool, randomize_optional_field_generation: bool) -> 'Message':
    from ...internal.mock.IsSubMap import is_sub_map
    from ...internal.mock.Verify import verify
    from ...internal.mock.VerifyNoMoreInteractions import verify_no_more_interactions
    from ...TelepactError import TelepactError
    from ..types.TUnion import TUnion
    from ...internal.generation.GenerateContext import GenerateContext

    header: dict[str, object] = request_message.headers

    enable_generation_stub = header.get("@gen_", False)
    function_name = request_message.get_body_target()
    argument = request_message.get_body_payload()

    if function_name == "fn.createStub_":
        given_stub = cast(dict[str, object], argument.get("stub"))

        stub_call = next((e for e in given_stub.items()
                         if e[0].startswith("fn.")))
        stub_function_name, stub_arg = cast(
            tuple[str, dict[str, object]], stub_call)
        stub_result = cast(dict[str, object], given_stub.get("->"))
        allow_argument_partial_match = not argument.get("strictMatch!", False)
        stub_count = cast(int, argument.get("count!", -1))

        stub = MockStub(stub_function_name, stub_arg,
                        stub_result, allow_argument_partial_match, stub_count)

        stubs.insert(0, stub)
        return Message({}, {"Ok_": {}})
    elif function_name == "fn.verify_":
        given_call = cast(dict[str, object], argument.get("call"))

        call = next((e for e in given_call.items()
                    if e[0].startswith("fn.")), None)
        call_function_name, call_arg = cast(
            tuple[str, dict[str, object]], call)
        verify_times = cast(dict[str, object], argument.get(
            "count!", {"AtLeast": {"times": 1}}))
        strict_match = cast(bool, argument.get("strictMatch!", False))

        verification_result = verify(
            call_function_name, call_arg, strict_match, verify_times, invocations)
        return Message({}, verification_result)
    elif function_name == "fn.verifyNoMoreInteractions_":
        verification_result = verify_no_more_interactions(
            invocations)
        return Message({}, verification_result)
    elif function_name == "fn.clearCalls_":
        invocations.clear()
        return Message({}, {"Ok_": {}})
    elif function_name == "fn.clearStubs_":
        stubs.clear()
        return Message({}, {"Ok_": {}})
    elif function_name == "fn.setRandomSeed_":
        given_seed = cast(int, argument.get("seed"))

        random.set_seed(given_seed)
        return Message({}, {"Ok_": {}})
    else:
        invocations.append(MockInvocation(function_name, dict(argument)))

        definition = cast(TUnion, telepact_schema.parsed.get(function_name + '.->'))

        for stub in stubs:
            if stub.count == 0:
                continue
            if stub.when_function == function_name:
                if stub.allow_argument_partial_match:
                    if is_sub_map(stub.when_argument, argument):
                        use_blueprint_value = True
                        include_optional_fields = False
                        always_include_required_fields = True
                        result_init = definition.generate_random_value(stub.then_result, use_blueprint_value, [],
                                                                              GenerateContext(
                                                                              include_optional_fields,
                                                                              randomize_optional_field_generation,
                                                                              always_include_required_fields,
                                                                              function_name, random))
                        result = cast(dict[str, object], result_init)
                        if stub.count > 0:
                            stub.count -= 1
                        return Message({}, result)
                else:
                    if stub.when_argument == argument:
                        use_blueprint_value = True
                        include_optional_fields = False
                        always_include_required_fields = True
                        result_init = definition.generate_random_value(stub.then_result, use_blueprint_value, [],
                                                                              GenerateContext(
                                                                              include_optional_fields,
                                                                              randomize_optional_field_generation,
                                                                              always_include_required_fields,
                                                                              function_name, random))
                        result = cast(dict[str, object], result_init)
                        if stub.count > 0:
                            stub.count -= 1
                        return Message({}, result)

        if not enable_generated_default_stub and not enable_generation_stub:
            return Message({}, {"ErrorNoMatchingStub_": {}})

        if definition is not None:
            result_union = definition
            ok_struct_ref = result_union.tags["Ok_"]
            use_blueprint_value = True
            include_optional_fields = True
            always_include_required_fields = True
            random_ok_struct_init = ok_struct_ref.generate_random_value({}, use_blueprint_value, [],
                                                                        GenerateContext(
                                                                        include_optional_fields,
                                                                        randomize_optional_field_generation,
                                                                        always_include_required_fields,
                                                                        function_name, random))
            random_ok_struct = cast(dict[str, object], random_ok_struct_init)
            return Message({}, {"Ok_": random_ok_struct})
        else:
            raise TelepactError(
                "Unexpected unknown function: {}".format(function_name))
