from typing import Any

from cases import get_values
from cases import additional_union_cases, additional_fn_cases, additional_integer_cases, additional_p2Union_cases, additional_p2Str_cases, additional_struct_cases


def generate_mock_cases(given_field: str, the_type, correct_values, additional_incorrect_values = []):
    for field, _, incorrect_values, base_path in get_values(given_field, the_type, correct_values, additional_incorrect_values):
        for incorrect_value, reason, path in incorrect_values:
            if 'RequiredStructFieldMissing' in reason:
                continue

            yield [[{}, {'fn._createStub': {'stub': {'fn.test': {'value': {field: incorrect_value}}, '->': {'Ok': {}}}}}], [{}, {'_ErrorInvalidRequestBody': {'cases': [{'path': ['fn._createStub', 'stub', 'fn.test', 'value'] + base_path + path, 'reason': reason}]}}]]
            yield [[{}, {'fn._createStub': {'stub': {'fn.test': {}, '->': {'Ok': {'value': {field: incorrect_value}}}}}}], [{}, {'_ErrorInvalidRequestBody': {'cases': [{'path': ['fn._createStub', 'stub', '->', 'Ok', 'value'] + base_path + path, 'reason': reason}]}}]]


cases = {
    'boolean': [v for v in generate_mock_cases('bool', bool, [False, True])],
    'integer': [v for v in generate_mock_cases('int', int, [0, -1, 1, 9223372036854775807, -9223372036854775808], additional_integer_cases)],
    'number': [v for v in generate_mock_cases('num', float, [0, -1, 1, -1.7976931348623157e+308, -2.2250738585072014e-308, 2.2250738585072014e-308, 1.7976931348623157e+308, -0.1, 0.1])],
    'string': [v for v in generate_mock_cases('str', str, ['', 'abc'])],
    'array': [v for v in generate_mock_cases('arr', list, [[], [False, 0, 0.1, '']])],
    'object': [v for v in generate_mock_cases('obj', dict, [{}, {'a': False, 'b': 0, 'c': 0.1, 'd': ''}])],
    'any': [v for v in generate_mock_cases('any', Any, [False, 0, 0.1, '', [], {}])],
    'struct': [v for v in generate_mock_cases('struct', dict, [{'required': False}, {'optional': False, 'required': False}], additional_struct_cases)],
    'union': [v for v in generate_mock_cases('union', dict, [{'One': {}}, {'Two':{'required': False}}, {'Two':{'optional': False, 'required': False}}], additional_union_cases)],
    'fn': [v for v in generate_mock_cases('fn', dict, [{'required': False}, {'optional': False, 'required': False}], additional_fn_cases)],
    'p2Str': [v for v in generate_mock_cases('p2Str', dict, [{'wrap': False, 'nest': [0]}, {'wrap': True, 'nest': [1]}], additional_p2Str_cases)],
    'p2Union': [v for v in generate_mock_cases('p2Union', dict, [{'Two': {'ewrap': False, 'enest': [0]}}, {'Two': {'ewrap': True, 'enest': [1]}}], additional_p2Union_cases)]
}
