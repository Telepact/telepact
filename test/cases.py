from typing import Any

default_values = [False, 0, 0.1, '', [], {}]

def get_type(the_type) -> str:
    if the_type == bool:
        return 'Boolean'
    elif the_type == int:
        return 'Integer'
    elif the_type == float:
        return 'Number'
    elif the_type == str:
        return 'String'
    elif the_type == list:
        return 'Array'
    elif the_type == dict:
        return 'Object'
    elif the_type == type(None):
        return 'Null'
    elif the_type == Any:
        return 'Any'


def type_unexp(incorrect_value, the_type):
    return {'TypeUnexpected': {'actual': {get_type(type(incorrect_value)): {}}, 'expected': {get_type(the_type): {}}}}

def cap(s: str):
    return s[:1].upper() + s[1:]


def get_values(given_field: str, the_type, given_correct_values, additional_incorrect_values):
    default_incorrect_values = list(filter(lambda n: type(n) not in (int, float) if the_type == float else False if the_type == Any else type(n) != the_type, default_values))
    given_incorrect_values = [(v, type_unexp(v, the_type), '') for v in default_incorrect_values] + additional_incorrect_values
    given_incorrect_values_w_null = [(v, type_unexp(v, the_type), '') for v in [None] + default_incorrect_values] + additional_incorrect_values
    abc = 'abcdefghijklmnopqrstuvwxyz'

    field = given_field
    correct_values = given_correct_values
    incorrect_values = [(v, r, p) for v, r, p in given_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, field
    
    field = 'null{}'.format(cap(given_field))
    correct_values = [None] + given_correct_values
    incorrect_values = [(v, r, p) for v, r, p in given_incorrect_values]
    yield field, correct_values, incorrect_values, field

    field = 'arr{}'.format(cap(given_field))
    correct_values = [[]] + [[v] for v in given_correct_values] + [given_correct_values]
    incorrect_values = [([given_correct_values[0], v], r, p) for v, r, p in given_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, '{}[1]'.format(field)

    field = 'arrNull{}'.format(cap(given_field))
    correct_values = [[]] + [[v] for v in [None] + given_correct_values] + [[None] + given_correct_values]
    incorrect_values = [([given_correct_values[0], v], r, p) for v, r, p in given_incorrect_values]
    yield field, correct_values, incorrect_values, '{}[1]'.format(field)

    field = 'obj{}'.format(cap(given_field))
    correct_values = [{}] + [{'a': v} for v in given_correct_values] + [{abc[i]: v for i,v in enumerate(given_correct_values)}]
    incorrect_values = [({'a': given_correct_values[0], 'b': v}, r, p) for v, r, p in given_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, '{}{{b}}'.format(field)

    field = 'objNull{}'.format(cap(given_field))
    correct_values = [{}] + [{'a': v} for v in [None] + given_correct_values] + [{abc[i]: v for i,v in enumerate([None] + given_correct_values)}]
    incorrect_values = [({'a': given_correct_values[0], 'b': v}, r, p) for v, r, p in given_incorrect_values]
    yield field, correct_values, incorrect_values, '{}{{b}}'.format(field)

    field = 'pStr{}'.format(cap(given_field))
    correct_values = [{'wrap': v} for v in given_correct_values]
    incorrect_values = [({'wrap': v}, r, p) for v, r, p in given_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, '{}.wrap'.format(field)

    field = 'pStrNull{}'.format(cap(given_field))
    correct_values = [{'wrap': v} for v in [None] + given_correct_values]
    incorrect_values = [({'wrap': v}, r, p) for v, r, p in given_incorrect_values]
    yield field, correct_values, incorrect_values, '{}.wrap'.format(field)

    field = 'pEnum{}'.format(cap(given_field))
    correct_values = [{'one': {}}] + [{'two': {'ewrap': v}} for v in given_correct_values]
    incorrect_values = [({'two': {'ewrap': v}}, r, p) for v, r, p in given_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, '{}.two.ewrap'.format(field)

    field = 'pEnumNull{}'.format(cap(given_field))
    correct_values = [{'one': {}}] + [{'two': {'ewrap': v}} for v in [None] + given_correct_values]
    incorrect_values = [({'two': {'ewrap': v}}, r, p) for v, r, p in given_incorrect_values]
    yield field, correct_values, incorrect_values, '{}.two.ewrap'.format(field)


def is_iter(v):
    try:
        i = iter(v)
        return True
    except TypeError:
        return False



def generate_basic_cases(given_field: str, the_type, correct_values, additional_incorrect_values = []):
    for field, correct_values, incorrect_values, base_path in get_values(given_field, the_type, correct_values, additional_incorrect_values):
        for correct_value in correct_values:
            case = [[{'ok': {'value': {field: correct_value}}}, {'fn.test': {'value': {field: correct_value}}}], [{}, {'ok': {'value': {field: correct_value}}}]]
            if is_iter(correct_value) and len(correct_value) > 3:
                case.append(False)
            yield case

        for incorrect_value, reason, path in incorrect_values:
            yield [[{}, {'fn.test': {'value': {field: incorrect_value}}}], [{}, {'_errorInvalidRequestBody': {'cases': [{'path': 'fn.test.value.{}{}'.format(base_path, path), 'reason': reason}]}}]]

        for incorrect_value, reason, path in incorrect_values:
            yield [[{'ok': {'value': {field: incorrect_value}}}, {'fn.test': {}}], [{}, {'_errorInvalidResponseBody': {'cases': [{'path': 'ok.value.{}{}'.format(base_path, path), 'reason': reason}]}}]]


additional_integer_cases = [
    (9223372036854775808, {'NumberOutOfRange': {}}, ''), 
    (-9223372036854775809, {'NumberOutOfRange': {}}, '')
]
additional_struct_cases = [
    ({}, {'RequiredStructFieldMissing': {}}, '.required'),
    ({'required': False, 'a': False}, {'StructFieldUnknown': {}}, '.a')
]
additional_enum_cases = [
    ({}, {'ZeroOrManyEnumFieldsDisallowed': {}}, ''),
    ({'one': {}, 'two': {'optional': False, 'required': False}}, {'ZeroOrManyEnumFieldsDisallowed': {}}, ''),
    ({'a': {}}, {'EnumFieldUnknown': {}}, '.a'),
    ({'two': {}}, {'RequiredStructFieldMissing': {}}, '.two.required'),
    ({'one': False}, {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}, '.one'),
    ({'one': 0}, {'TypeUnexpected': {'actual': {'Integer': {}}, 'expected': {'Object': {}}}}, '.one'),
    ({'one': 0.1}, {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}, '.one'),
    ({'one': ''}, {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}, '.one'),
    ({'one': []}, {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}, '.one'),
]
additional_fn_cases = [
    ({}, {'RequiredStructFieldMissing': {}}, '.required'),
    ({'required': False, 'a': False}, {'StructFieldUnknown': {}}, '.a')
]
additional_p2Str_cases = [
    ({'wrap': 0, 'nest': [0]}, {'TypeUnexpected': {'actual': {'Integer': {}}, 'expected': {'Boolean': {}}}}, '.wrap'),
    ({'wrap': 0.1, 'nest': [0]}, {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}, '.wrap'),
    ({'wrap': '', 'nest': [0]}, {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}, '.wrap'),
    ({'wrap': [], 'nest': [0]}, {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}, '.wrap'),
    ({'wrap': {}, 'nest': [0]}, {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}, '.wrap'),
    ({'wrap': False, 'nest': [0, False]}, {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}, '.nest[1]'),
    ({'wrap': False, 'nest': [0, 0.1]}, {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}, '.nest[1]'),
    ({'wrap': False, 'nest': [0, '']}, {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}, '.nest[1]'),
    ({'wrap': False, 'nest': [0, []]}, {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}, '.nest[1]'),
    ({'wrap': False, 'nest': [0, {}]}, {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}, '.nest[1]'),
]
additional_p2Enum_cases = [
    ({'two': {'ewrap': 0, 'enest': [0]}}, {'TypeUnexpected': {'actual': {'Integer': {}}, 'expected': {'Boolean': {}}}}, '.two.ewrap'),
    ({'two': {'ewrap': 0.1, 'enest': [0]}}, {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}, '.two.ewrap'),
    ({'two': {'ewrap': '', 'enest': [0]}}, {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}, '.two.ewrap'),
    ({'two': {'ewrap': [], 'enest': [0]}}, {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}, '.two.ewrap'),
    ({'two': {'ewrap': {}, 'enest': [0]}}, {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}, '.two.ewrap'),
    ({'two': {'ewrap': False, 'enest': [0, False]}}, {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}, '.two.enest[1]'),
    ({'two': {'ewrap': False, 'enest': [0, 0.1]}}, {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}, '.two.enest[1]'),
    ({'two': {'ewrap': False, 'enest': [0, '']}}, {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}, '.two.enest[1]'),
    ({'two': {'ewrap': False, 'enest': [0, []]}}, {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}, '.two.enest[1]'),
    ({'two': {'ewrap': False, 'enest': [0, {}]}}, {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}, '.two.enest[1]'),
]

cases = {
    'boolean': [v for v in generate_basic_cases('bool', bool, [False, True])],
    'integer': [v for v in generate_basic_cases('int', int, [0, -1, 1, 9223372036854775807, -9223372036854775808], additional_integer_cases)],
    'number': [v for v in generate_basic_cases('num', float, [0, -1, 1, -1.7976931348623157e+308, -2.2250738585072014e-308, 2.2250738585072014e-308, 1.7976931348623157e+308, -0.1, 0.1])],
    'string': [v for v in generate_basic_cases('str', str, ['', 'abc'])],
    'array': [v for v in generate_basic_cases('arr', list, [[], [False, 0, 0.1, '']])],
    'object': [v for v in generate_basic_cases('obj', dict, [{}, {'a': False, 'b': 0, 'c': 0.1, 'd': ''}])],
    'any': [v for v in generate_basic_cases('any', Any, [False, 0, 0.1, '', [], {}])],
    'struct': [v for v in generate_basic_cases('struct', dict, [{'required': False}, {'optional': False, 'required': False}], additional_struct_cases)],
    'enum': [v for v in generate_basic_cases('enum', dict, [{'one': {}}, {'two':{'required': False}}, {'two':{'optional': False, 'required': False}}], additional_enum_cases)],
    'fn': [v for v in generate_basic_cases('fn', dict, [{'required': False}, {'optional': False, 'required': False}], additional_fn_cases)],
    'p2Str': [v for v in generate_basic_cases('p2Str', dict, [{'wrap': False, 'nest': [0]}, {'wrap': True, 'nest': [1]}], additional_p2Str_cases)],
    'p2Enum': [v for v in generate_basic_cases('p2Enum', dict, [{'two': {'ewrap': False, 'enest': [0]}}, {'two': {'ewrap': True, 'enest': [1]}}], additional_p2Enum_cases)],
    'testPdStr': [
        [[{'ok': {'value': {'pdStr': {'dwrap': {'wrap': False}}}}}, {'fn.test': {'value': {'pdStr': {'dwrap': {'wrap': False}}}}}], [{}, {'ok': {'value': {'pdStr': {'dwrap': {'wrap': False}}}}}]],
    ],
    'testPing': [
        [[{}, {'fn._ping': {}}], [{}, {'ok': {}}]],
    ],
    'testCallId': [
        [[{'_id': 'abcd'}, {'fn._ping': {}}], [{'_id': 'abcd'}, {'ok': {}}]],
        [[{'_id': 1234}, {'fn._ping': {}}], [{'_id': 1234}, {'ok': {}}]],
    ],
    'testUnknownFunction': [
        [[{}, {'fn.notFound': {}}], [{}, {'_errorInvalidRequestBody': {'cases': [{'path': 'fn.notFound', 'reason': {'FunctionUnknown': {}}}]}}], True],
    ],
    'testErrors': [
        [[{'result': {'errorExample': {'property': 'a'}}}, {'fn.test': {}}], [{}, {'errorExample': {'property': 'a'}}]],
        [[{'result': {'errorExample': {'wrong': 'a'}}}, {'fn.test': {}}], [{}, {'_errorInvalidResponseBody': {'cases': [{'path': 'errorExample.property', 'reason': {'RequiredStructFieldMissing': {}}}, {'path': 'errorExample.wrong', 'reason': {'StructFieldUnknown': {}}}]}}]],
        [[{'result': {'errorUnknown': {'property': 'a'}}}, {'fn.test': {}}], [{}, {'_errorInvalidResponseBody': {'cases': [{'path': 'errorUnknown', 'reason': {'EnumFieldUnknown': {}}}]}}]],
    ],
    'testSelectFields': [
        [[{'_sel': {'struct.ExStruct': ['optional']}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'struct': {'optional': False}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional']}, 'ok': {'value': {'struct': {'required': False}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'struct': {}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional', 'required']}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'struct': {'optional': False, 'required': False}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional', 'required']}, 'ok': {'value': {'struct': {'required': False}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'struct': {'required': False}}}}]],
        [[{'_sel': {'struct.ExStruct': []}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'struct': {}}}}]],
        [[{'_sel': {'struct.ExStruct': []}, 'ok': {'value': {'struct': {'required': False}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'struct': {}}}}]],
        [[{'_sel': {'->.ok': []}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'ok': {}}]],
        [[{'_sel': {'fn.example': ['optional']}, 'ok': {'value': {'fn': {'required': True, 'optional': True}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'fn': {'optional': True}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional']}, 'ok': {'value': {'arrStruct': [{'required': False}, {'optional': False, 'required': False}]}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'arrStruct': [{}, {'optional': False}]}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional']}, 'ok': {'value': {'objStruct': {'a': {'required': False}, 'b': {'optional': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'objStruct': {'a': {}, 'b': {'optional': False}}}}}]],
        [[{'_sel': False, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}', 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': 0, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}', 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': '', 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}', 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': [], 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}', 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': {'': []}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{}', 'reason': {'SelectHeaderKeyMustBeStructReference': {}}}]}}]],
        [[{'_sel': {'notStruct': []}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{notStruct}', 'reason': {'SelectHeaderKeyMustBeStructReference': {}}}]}}]],
        [[{'_sel': {'struct.Unknown': []}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.Unknown}', 'reason': {'StructNameUnknown': {}}}]}}]],
        [[{'_sel': {'struct.ExStruct': False}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}', 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': 0}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}', 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': ''}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}', 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': {}}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}', 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [False]}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}[0]', 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [0]}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}[0]', 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [[]]}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}[0]', 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [{}]}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}[0]', 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': ['unknownField']}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}[0]', 'reason': {'StructFieldUnknown': {}}}]}}]],
        [[{'_sel': {'struct.ExStruct': ['']}, 'ok': {'value': {'struct': {'optional': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_sel}{struct.ExStruct}[0]', 'reason': {'StructFieldUnknown': {}}}]}}]],
    ],
    'testUnsafe': [
        [[{'_unsafe': True, 'result': {'ok': {'value': {'bool': 0}}}}, {'fn.test': {}}], [{}, {'ok': {'value': {'bool': 0}}}]],
        [[{'_unsafe': True, 'result': {'errorExample': {'wrong': 'a'}}}, {'fn.test': {}}], [{}, {'errorExample': {'wrong': 'a'}}]],
    ],
    'testApplicationFailure': [
        [[{'throw': True}, {'fn.test': {}}], [{}, {'_errorUnknown': {}}]],
    ],
    'api': [
        [[{}, {'fn._api': {}}], [{},{'ok':{'api':[{'///':[' This is the example schema. It is focussed on outlining type edge cases for use in tests. ','                                                                                           ',' As a reminder:                                                                            ',' - ! means optional field                                                                  ',' - ? means nullable type                                                                   '],'info.Example':{}},{'///':' A struct value demonstrating all common type permutations. ','struct.Value':{'bool!':['boolean'],'nullBool!':['boolean?'],'arrBool!':['array',['boolean']],'arrNullBool!':['array',['boolean?']],'objBool!':['object',['boolean']],'objNullBool!':['object',['boolean?']],'pStrBool!':['struct<1>.PStr',['boolean']],'pStrNullBool!':['struct<1>.PStr',['boolean?']],'pEnumBool!':['enum<1>.PEnum',['boolean']],'pEnumNullBool!':['enum<1>.PEnum',['boolean?']],'int!':['integer'],'nullInt!':['integer?'],'arrInt!':['array',['integer']],'arrNullInt!':['array',['integer?']],'objInt!':['object',['integer']],'objNullInt!':['object',['integer?']],'pStrInt!':['struct<1>.PStr',['integer']],'pStrNullInt!':['struct<1>.PStr',['integer?']],'pEnumInt!':['enum<1>.PEnum',['integer']],'pEnumNullInt!':['enum<1>.PEnum',['integer?']],'num!':['number'],'nullNum!':['number?'],'arrNum!':['array',['number']],'arrNullNum!':['array',['number?']],'objNum!':['object',['number']],'objNullNum!':['object',['number?']],'pStrNum!':['struct<1>.PStr',['number']],'pStrNullNum!':['struct<1>.PStr',['number?']],'pEnumNum!':['enum<1>.PEnum',['number']],'pEnumNullNum!':['enum<1>.PEnum',['number?']],'str!':['string'],'nullStr!':['string?'],'arrStr!':['array',['string']],'arrNullStr!':['array',['string?']],'objStr!':['object',['string']],'objNullStr!':['object',['string?']],'pStrStr!':['struct<1>.PStr',['string']],'pStrNullStr!':['struct<1>.PStr',['string?']],'pEnumStr!':['enum<1>.PEnum',['string']],'pEnumNullStr!':['enum<1>.PEnum',['string?']],'arr!':['array',['any']],'nullArr!':['array?',['any']],'arrArr!':['array',['array',['any']]],'arrNullArr!':['array',['array?',['any']]],'objArr!':['object',['array',['any']]],'objNullArr!':['object',['array?',['any']]],'pStrArr!':['struct<1>.PStr',['array',['any']]],'pStrNullArr!':['struct<1>.PStr',['array?',['any']]],'pEnumArr!':['enum<1>.PEnum',['array',['any']]],'pEnumNullArr!':['enum<1>.PEnum',['array?',['any']]],'obj!':['object',['any']],'nullObj!':['object?',['any']],'arrObj!':['array',['object',['any']]],'arrNullObj!':['array',['object?',['any']]],'objObj!':['object',['object',['any']]],'objNullObj!':['object',['object?',['any']]],'pStrObj!':['struct<1>.PStr',['object',['any']]],'pStrNullObj!':['struct<1>.PStr',['object?',['any']]],'pEnumObj!':['enum<1>.PEnum',['object',['any']]],'pEnumNullObj!':['enum<1>.PEnum',['object?',['any']]],'any!':['any'],'nullAny!':['any?'],'arrAny!':['array',['any']],'arrNullAny!':['array',['any?']],'objAny!':['object',['any']],'objNullAny!':['object',['any?']],'pStrAny!':['struct<1>.PStr',['any']],'pStrNullAny!':['struct<1>.PStr',['any?']],'pEnumAny!':['enum<1>.PEnum',['any']],'pEnumNullAny!':['enum<1>.PEnum',['any?']],'struct!':['struct.ExStruct'],'nullStruct!':['struct.ExStruct?'],'arrStruct!':['array',['struct.ExStruct']],'arrNullStruct!':['array',['struct.ExStruct?']],'objStruct!':['object',['struct.ExStruct']],'objNullStruct!':['object',['struct.ExStruct?']],'pStrStruct!':['struct<1>.PStr',['struct.ExStruct']],'pStrNullStruct!':['struct<1>.PStr',['struct.ExStruct?']],'pEnumStruct!':['enum<1>.PEnum',['struct.ExStruct']],'pEnumNullStruct!':['enum<1>.PEnum',['struct.ExStruct?']],'enum!':['enum.ExEnum'],'nullEnum!':['enum.ExEnum?'],'arrEnum!':['array',['enum.ExEnum']],'arrNullEnum!':['array',['enum.ExEnum?']],'objEnum!':['object',['enum.ExEnum']],'objNullEnum!':['object',['enum.ExEnum?']],'pStrEnum!':['struct<1>.PStr',['enum.ExEnum']],'pStrNullEnum!':['struct<1>.PStr',['enum.ExEnum?']],'pEnumEnum!':['enum<1>.PEnum',['enum.ExEnum']],'pEnumNullEnum!':['enum<1>.PEnum',['enum.ExEnum?']],'fn!':['fn.example'],'nullFn!':['fn.example?'],'arrFn!':['array',['fn.example']],'arrNullFn!':['array',['fn.example?']],'objFn!':['object',['fn.example']],'objNullFn!':['object',['fn.example?']],'pStrFn!':['struct<1>.PStr',['fn.example']],'pStrNullFn!':['struct<1>.PStr',['fn.example?']],'pEnumFn!':['enum<1>.PEnum',['fn.example']],'pEnumNullFn!':['enum<1>.PEnum',['fn.example?']],'p2Str!':['struct<2>.P2Str',['boolean'],['integer']],'nullP2Str!':['struct<2>.P2Str?',['boolean'],['integer']],'arrP2Str!':['array',['struct<2>.P2Str',['boolean'],['integer']]],'arrNullP2Str!':['array',['struct<2>.P2Str?',['boolean'],['integer']]],'objP2Str!':['object',['struct<2>.P2Str',['boolean'],['integer']]],'objNullP2Str!':['object',['struct<2>.P2Str?',['boolean'],['integer']]],'pStrP2Str!':['struct<1>.PStr',['struct<2>.P2Str',['boolean'],['integer']]],'pStrNullP2Str!':['struct<1>.PStr',['struct<2>.P2Str?',['boolean'],['integer']]],'pEnumP2Str!':['enum<1>.PEnum',['struct<2>.P2Str',['boolean'],['integer']]],'pEnumNullP2Str!':['enum<1>.PEnum',['struct<2>.P2Str?',['boolean'],['integer']]],'p2Enum!':['enum<2>.P2Enum',['boolean'],['integer']],'nullP2Enum!':['enum<2>.P2Enum?',['boolean'],['integer']],'arrP2Enum!':['array',['enum<2>.P2Enum',['boolean'],['integer']]],'arrNullP2Enum!':['array',['enum<2>.P2Enum?',['boolean'],['integer']]],'objP2Enum!':['object',['enum<2>.P2Enum',['boolean'],['integer']]],'objNullP2Enum!':['object',['enum<2>.P2Enum?',['boolean'],['integer']]],'pStrP2Enum!':['struct<1>.PStr',['enum<2>.P2Enum',['boolean'],['integer']]],'pStrNullP2Enum!':['struct<1>.PStr',['enum<2>.P2Enum?',['boolean'],['integer']]],'pEnumP2Enum!':['enum<1>.PEnum',['enum<2>.P2Enum',['boolean'],['integer']]],'pEnumNullP2Enum!':['enum<1>.PEnum',['enum<2>.P2Enum?',['boolean'],['integer']]],'pdStr!':['struct<1>.PdStr',['struct<1>.PStr',['boolean']]]}},{'///':[' The main struct example.                                                                ','                                                                                         ',' The [required] field must be supplied. The optional field does not need to be supplied. '],'struct.ExStruct':{'required':['boolean'],'optional!':['boolean']}},{'enum.ExEnum':{'one':{},'two':{'required':['boolean'],'optional!':['boolean']}}},{'struct<1>.PStr':{'wrap':['T.0']}},{'struct<1>.PdStr':{'dwrap':['struct<1>.PStr',['boolean']]}},{'struct<2>.P2Str':{'wrap':['T.0'],'nest':['array',['T.1']]}},{'enum<1>.PEnum':{'one':{},'two':{'ewrap':['T.0']}}},{'enum<2>.P2Enum':{'one':{},'two':{'ewrap':['T.0'],'enest':['array',['T.1']]}}},{'///':'An example function.','fn.example':{'required':['boolean'],'optional!':['boolean']},'->':{'ok':{}}},{'fn.test':{'value!':['struct.Value']},'->':{'ok':{'value!':['struct.Value']},'errorExample':{'property':['string']}}},{'///':' Ping the server. ','fn._ping':{},'->':{'ok':{}}},{'///':' Get the jAPI `schema` of this server. ','fn._api':{},'->':{'ok':{'api':['array',['object',['any']]]}}},{'///':' A placeholder function when the requested function is unknown. ','fn._unknown':{},'->':{'ok':{}}},{'///':' A type. ','enum._Type':{'Boolean':{},'Integer':{},'Number':{},'String':{},'Array':{},'Object':{},'Unknown':{}}},{'///':' A reason for the validation failure in the body. ','enum._BodyValidationFailureReason':{'TypeUnexpected':{'expected':['enum._Type'],'actual':['enum._Type']},'NullDisallowed':{},'StructFieldUnknown':{},'RequiredStructFieldMissing':{},'NumberOutOfRange':{},'ZeroOrManyEnumFieldsDisallowed':{},'EnumFieldUnknown':{},'ExtensionValidationFailure':{'message':['string']},'FunctionUnknown':{}}},{'///':' A reason for the validation failure in the header. ','enum._HeaderValidationFailureReason':{'TypeUnexpected':{'expected':['enum._Type'],'actual':['enum._Type']},'SelectHeaderKeyMustBeStructReference':{},'StructNameUnknown':{},'StructFieldUnknown':{}}},{'///':' A validation failure located at a `path` explained by a `reason`. ','struct._BodyValidationFailure':{'path':['string'],'reason':['enum._BodyValidationFailureReason']}},{'///':' A validation failure located at a `path` explained by a `reason`. ','struct._HeaderValidationFailure':{'path':['string'],'reason':['enum._HeaderValidationFailureReason']}},{'///':[' All functions may return a validation error:                                                             ',' - `_errorInvalidRequestHeaders`: The Headers on the Request is invalid as outlined by a list of `cases`. ',' - `_errorInvalidRequestBody`: The Body on the Request is invalid as outlined by a list of `cases`.       ',' - `_errorInvalidResponseBody`: The Body that the Server attempted to put on the Response is invalid as   ','     outlined by a list of `cases.                                                                        ',' - `_errorParseFailure`: The Request could not be parsed as a jAPI Message.                               '],'trait._Validated':{'fn._?*':{},'->':{'_errorUnknown':{},'_errorInvalidRequestHeaders':{'cases':['array',['struct._HeaderValidationFailure']]},'_errorInvalidRequestBody':{'cases':['array',['struct._BodyValidationFailure']]},'_errorInvalidResponseBody':{'cases':['array',['struct._BodyValidationFailure']]},'_errorParseFailure':{'reasons':['array',['string']]}}}}]}}]],
    ],
}
