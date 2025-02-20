from typing import Dict, List, Union

from ...internal.generation.GenerateContext import GenerateContext


def generate_random_select(possible_selects: dict[str, object], ctx: 'GenerateContext') -> object:
    possible_select = possible_selects[ctx.fn_scope]
    return sub_select(possible_select, ctx)


def sub_select(possible_select_section: object, ctx: 'GenerateContext') -> object:
    if isinstance(possible_select_section, list):
        selected_field_names = []

        for field_name in possible_select_section:
            if ctx.random_generator.next_boolean():
                selected_field_names.append(field_name)

        return selected_field_names
    elif isinstance(possible_select_section, dict):
        selected_section: dict[str, object] = {}

        for key, value in possible_select_section.items():
            if ctx.random_generator.next_boolean():
                result = sub_select(value, ctx)
                if isinstance(result, dict) and not result:
                    continue
                selected_section[key] = result

        return selected_section
    else:
        raise ValueError('Invalid possible_select_section')
