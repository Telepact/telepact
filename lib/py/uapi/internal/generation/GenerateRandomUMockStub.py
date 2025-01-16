from uapi.internal.generation.GenerateContext import GenerateContext
from uapi.internal.generation.GenerateRandomStruct import generate_random_struct
from uapi.internal.types.UFn import UFn
from uapi.internal.types.UType import UType


def generate_random_u_mock_stub(types: dict[str, UType], ctx: GenerateContext) -> object:
    functions = [value for key, value in types.items() if isinstance(
        value, UFn) and not key.endswith('_')]

    functions.sort(key=lambda fn: fn.name)

    print(f"randomSeed: {ctx.random_generator.seed}")
    print(f"functions: {[fn.name for fn in functions]}")

    index = ctx.random_generator.next_int_with_ceiling(len(functions))

    print(f"index: {index}")

    selected_fn = functions[index]

    print(f"selectedFn: {selected_fn.name}")

    arg_fields = selected_fn.call.cases[selected_fn.name].fields
    ok_fields = selected_fn.result.cases['Ok_'].fields

    arg = generate_random_struct(arg_fields, ctx.copy(
        always_include_required_fields=False))
    ok_result = generate_random_struct(
        ok_fields, ctx.copy(always_include_required_fields=False))

    return {
        selected_fn.name: arg,
        '->': {
            'Ok_': ok_result,
        },
    }
