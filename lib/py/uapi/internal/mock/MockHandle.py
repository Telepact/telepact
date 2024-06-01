from typing import List, Dict, Any
from uapi.Message import Message
from uapi.RandomGenerator import RandomGenerator
from uapi.UApiSchema import UApiSchema
from uapi.internal.mock.IsSubMap import is_sub_map
from uapi.internal.mock.MockInvocation import MockInvocation
from uapi.internal.mock.MockStub import MockStub
from uapi.internal.mock.Verify import verify
from uapi.internal.mock.VerifyNoMoreInteractions import verify_no_more_interactions


def mock_handle(request_message: 'Message', stubs: List['MockStub'], invocations: List['MockInvocation'],
                random: 'RandomGenerator', u_api_schema: 'UApiSchema', enable_generated_default_stub: bool,
                enable_optional_field_generation: bool, randomize_optional_field_generation: bool) -> 'Message':
    header: Dict[str, Any] = request_message.header

    enable_generation_stub = header.get("_gen", False)
    function_name = request_message.get_body_target()
    argument = request_message.get_body_payload()

    if function_name == "fn.create_stub_":
        given_stub = argument.get("stub")

        stub_call = next((e for e in given_stub.items()
                         if e[0].startswith("fn.")), None)
        stub_function_name, stub_arg = stub_call
        stub_result = given_stub.get("->")
        allow_argument_partial_match = not argument.get("strictMatch!", False)
        stub_count = argument.get("count!", -1)

        stub = MockStub(stub_function_name, dict(stub_arg),
                        stub_result, allow_argument_partial_match, stub_count)

        stubs.insert(0, stub)
        return Message({}, {"Ok_": {}})
    elif function_name == "fn.verify_":
        given_call = argument.get("call")

        call = next((e for e in given_call.items()
                    if e[0].startswith("fn.")), None)
        call_function_name, call_arg = call
        verify_times = argument.get("count!", {"AtLeast": {"times": 1}})
        strict_match = argument.get("strictMatch!", False)

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
        given_seed = argument.get("seed")

        random.set_seed(given_seed)
        return Message({}, {"Ok_": {}})
    else:
        invocations.append(MockInvocation(function_name, dict(argument)))

        definition = u_api_schema.parsed.get(function_name)

        for stub in stubs:
            if stub.count == 0:
                continue
            if stub.when_function == function_name:
                if stub.allow_argument_partial_match:
                    if is_sub_map(stub.when_argument, argument):
                        use_blueprint_value = True
                        include_optional_fields = False
                        result = definition.result.generate_random_value(stub.then_result, use_blueprint_value,
                                                                         include_optional_fields,
                                                                         randomize_optional_field_generation,
                                                                         [], [], random)
                        if stub.count > 0:
                            stub.count -= 1
                        return Message({}, result)
                else:
                    if stub.when_argument == argument:
                        use_blueprint_value = True
                        include_optional_fields = False
                        result = definition.result.generate_random_value(stub.then_result, use_blueprint_value,
                                                                         include_optional_fields,
                                                                         randomize_optional_field_generation,
                                                                         [], [], random)
                        if stub.count > 0:
                            stub.count -= 1
                        return Message({}, result)

        if not enable_generated_default_stub and not enable_generation_stub:
            return Message({}, {"ErrorNoMatchingStub__": {}})

        if definition is not None:
            result_union = definition.result
            ok_struct_ref = result_union.cases.get("Ok_")
            use_blueprint_value = True
            include_optional_fields = True
            random_ok_struct = ok_struct_ref.generate_random_value({}, use_blueprint_value,
                                                                   include_optional_fields,
                                                                   randomize_optional_field_generation,
                                                                   [], [], random)
            return Message({}, {"Ok_": random_ok_struct})
        else:
            raise UApiError(
                "Unexpected unknown function: {}".format(function_name))
