from typing import Any

default_values = [False, 0, 0.1, '', [], {}]

def get_type(the_type, use_int=True) -> str:
    if the_type == bool:
        return 'Boolean'
    elif use_int and the_type == int:
        return 'Integer'
    elif the_type in (int, float):
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
    return {'TypeUnexpected': {'actual': {get_type(type(incorrect_value), use_int=False): {}}, 'expected': {get_type(the_type): {}}}}

def cap(s: str):
    return s[:1].upper() + s[1:]


def get_values(given_field: str, the_type, given_correct_values, additional_incorrect_values):
    default_incorrect_values = list(filter(lambda n: type(n) not in (int, float) if the_type == float else False if the_type == Any else type(n) != the_type, default_values))
    given_incorrect_values = [(v, [(type_unexp(v, the_type), [])]) for v in default_incorrect_values] + additional_incorrect_values
    given_incorrect_values_w_null = [(v, [(type_unexp(v, the_type), [])]) for v in [None] + default_incorrect_values] + additional_incorrect_values
    abc = 'abcdefghijklmnopqrstuvwxyz'

    field = given_field
    correct_values = given_correct_values
    incorrect_values = [(v, e) for v, e in given_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, [field]
    
    field = 'null{}'.format(cap(given_field))
    correct_values = [None] + given_correct_values
    incorrect_values = [(v, e) for v, e in given_incorrect_values]
    yield field, correct_values, incorrect_values, [field]

    field = 'arr{}'.format(cap(given_field))
    correct_values = [[]] + [[v] for v in given_correct_values] + [given_correct_values]
    incorrect_values = [([given_correct_values[0], v], [(r, [1] + p)]) for v, [(r, p)] in given_incorrect_values_w_null]
    if incorrect_values:
        incorrect_values += [([v for v, e in given_incorrect_values_w_null], [(r, [i] + p) for i, (v, [(r, p)]) in enumerate(given_incorrect_values_w_null)])]
    yield field, correct_values, incorrect_values, [field]

    field = 'arrNull{}'.format(cap(given_field))
    correct_values = [[]] + [[v] for v in [None] + given_correct_values] + [[None] + given_correct_values]
    incorrect_values = [([given_correct_values[0], v], [(r, [1] + p)]) for v, [(r, p)] in given_incorrect_values]
    if incorrect_values:
        incorrect_values += [([v for v, e in given_incorrect_values], [(r, [i] + p) for i, (v, [(r, p)]) in enumerate(given_incorrect_values)])]
    yield field, correct_values, incorrect_values, [field]

    field = 'obj{}'.format(cap(given_field))
    correct_values = [{}] + [{'a': v} for v in given_correct_values] + [{abc[i]: v for i,v in enumerate(given_correct_values)}]
    incorrect_values = [({'a': given_correct_values[0], 'b': v}, [(r, ['b'] + p)]) for v, [(r, p)] in given_incorrect_values_w_null]
    if incorrect_values:
        incorrect_values += [({abc[i]: v for i, (v, e) in enumerate(given_incorrect_values_w_null)}, [(r, [abc[i]] + p) for i, (v, [(r, p)]) in enumerate(given_incorrect_values_w_null)])]
    yield field, correct_values, incorrect_values, [field]

    field = 'objNull{}'.format(cap(given_field))
    correct_values = [{}] + [{'a': v} for v in [None] + given_correct_values] + [{abc[i]: v for i,v in enumerate([None] + given_correct_values)}]
    incorrect_values = [({'a': given_correct_values[0], 'b': v}, [(r, ['b'] + p)]) for v, [(r, p)] in given_incorrect_values]
    if incorrect_values:
        incorrect_values += [({abc[i]: v for i, (v, e) in enumerate(given_incorrect_values)}, [(r, [abc[i]] + p) for i, (v, [(r, p)]) in enumerate(given_incorrect_values)])]
    yield field, correct_values, incorrect_values, [field]


def is_iter(v):
    try:
        i = iter(v)
        return True
    except TypeError:
        return False
    

def has_too_many_keys(v):
    if type(v) == list:
        return any([has_too_many_keys(e) for e in v])
    elif type(v) == dict:
        if len(v) > 2:
            return True
        else:
            return any([has_too_many_keys(e) for e in v.values()])
    else:
        return False


def generate_basic_cases(given_field: str, the_type, correct_values, additional_incorrect_values = []):
    for field, correct_values, incorrect_values, base_path in get_values(given_field, the_type, correct_values, additional_incorrect_values):
        for correct_value in correct_values:
            expected_response_header = {}
            if has_too_many_keys(correct_value):
                expected_response_header['_assert'] = {'skipFieldIdCheck': True}
            
            case = [[{'good_': True, 'Ok_': {'value!': {field: correct_value}}}, {'fn.test': {'value!': {field: correct_value}}}], [expected_response_header, {'Ok_': {'value!': {field: correct_value}}}]]

            yield case

        for incorrect_value, errors in incorrect_values:
            expected_response_header = {}
            cases = [{'path': ['fn.test', 'value!'] + base_path + path, 'reason': reason} for reason, path in errors]
            if len(cases) > 1:
                expected_response_header.setdefault('_assert', {})['setCompare'] = True
            if has_too_many_keys(incorrect_value):
                expected_response_header.setdefault('_assert', {})['skipFieldIdCheck'] = True

            yield [[{}, {'fn.test': {'value!': {field: incorrect_value}}}], [expected_response_header, {'ErrorInvalidRequestBody_': {'cases': cases}}]]

        for incorrect_value, errors in incorrect_values:
            expected_response_header = {}
            cases = [{'path': ['Ok_', 'value!'] + base_path + path, 'reason': reason} for reason, path in errors]
            if len(cases) > 1:
                expected_response_header.setdefault('_assert', {})['setCompare'] = True
            if has_too_many_keys(incorrect_value):
                expected_response_header.setdefault('_assert', {})['skipFieldIdCheck'] = True

            yield [[{'Ok_': {'value!': {field: incorrect_value}}}, {'fn.test': {}}], [expected_response_header, {'ErrorInvalidResponseBody_': {'cases': cases}}]]


additional_integer_cases = [
    (9223372036854775808, [({'NumberOutOfRange': {}}, [])]), 
    (-9223372036854775809, [({'NumberOutOfRange': {}}, [])])
]
additional_number_cases = [
    (9223372036854775808, [({'NumberOutOfRange': {}}, [])]),
    (-9223372036854775809, [({'NumberOutOfRange': {}}, [])])
]
additional_struct_cases = [
    ({}, [({'RequiredObjectKeyMissing': {'key': 'required'}}, [])]),
    ({'required': False, 'a': False}, [({'ObjectKeyDisallowed': {}}, ['a'])])
]
additional_union_cases = [
    ({}, [({'ObjectSizeUnexpected': {'actual': 0, 'expected': 1}}, [])]),
    ({'One': {}, 'Two': {'optional!': False, 'required': False}}, [({'ObjectSizeUnexpected': {'actual': 2, 'expected': 1}}, [])]),
    ({'a': {}}, [({'ObjectKeyDisallowed': {}}, ['a'])]),
    ({'Two': {}}, [({'RequiredObjectKeyMissing': {'key': 'required'}}, ['Two'])]),
    ({'One': False}, [({'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}, ['One'])]),
    ({'One': 0}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}, ['One'])]),
    ({'One': 0.1}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}, ['One'])]),
    ({'One': ''}, [({'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}, ['One'])]),
    ({'One': []}, [({'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}, ['One'])]),
]
additional_fn_cases = [
    ({}, [({'ObjectSizeUnexpected': {'actual': 0, 'expected': 1}}, [])]),
    ({'a': {}}, [({'ObjectKeyDisallowed': {}}, ['a'])]),
    ({'fn.example': {}}, [({'RequiredObjectKeyMissing': {'key': 'required'}}, ['fn.example'])]),
    ({'fn.example': {'required': False, 'a': False}}, [({'ObjectKeyDisallowed': {}}, ['fn.example', 'a'])]),
    ({'fn.example': False}, [({'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}, ['fn.example'])]),
    ({'fn.example': 0}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}, ['fn.example'])]),
    ({'fn.example': 0.1}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}, ['fn.example'])]),
    ({'fn.example': ''}, [({'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}, ['fn.example'])]),
    ({'fn.example': []}, [({'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}, ['fn.example'])]),
]
additional_p2Str_cases = [
    ({'wrap': 0, 'nest': [0]}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}, ['wrap'])]),
    ({'wrap': 0.1, 'nest': [0]}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}, ['wrap'])]),
    ({'wrap': '', 'nest': [0]}, [({'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}, ['wrap'])]),
    ({'wrap': [], 'nest': [0]}, [({'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}, ['wrap'])]),
    ({'wrap': {}, 'nest': [0]}, [({'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}, ['wrap'])]),
    ({'wrap': False, 'nest': [0, False]}, [({'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}, ['nest', 1])]),
    ({'wrap': False, 'nest': [0, 0.1]}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}, ['nest', 1])]),
    ({'wrap': False, 'nest': [0, '']}, [({'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}, ['nest', 1])]),
    ({'wrap': False, 'nest': [0, []]}, [({'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}, ['nest', 1])]),
    ({'wrap': False, 'nest': [0, {}]}, [({'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}, ['nest', 1])]),
]
additional_p2Union_cases = [
    ({'Two': {'ewrap': 0, 'enest': [0]}}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}, ['Two', 'ewrap'])]),
    ({'Two': {'ewrap': 0.1, 'enest': [0]}}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}, ['Two', 'ewrap'])]),
    ({'Two': {'ewrap': '', 'enest': [0]}}, [({'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}, ['Two', 'ewrap'])]),
    ({'Two': {'ewrap': [], 'enest': [0]}}, [({'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}, ['Two', 'ewrap'])]),
    ({'Two': {'ewrap': {}, 'enest': [0]}}, [({'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}, ['Two', 'ewrap'])]),
    ({'Two': {'ewrap': False, 'enest': [0, False]}}, [({'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}, ['Two', 'enest', 1])]),
    ({'Two': {'ewrap': False, 'enest': [0, 0.1]}}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}, ['Two', 'enest', 1])]),
    ({'Two': {'ewrap': False, 'enest': [0, '']}}, [({'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}, ['Two', 'enest', 1])]),
    ({'Two': {'ewrap': False, 'enest': [0, []]}}, [({'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}, ['Two', 'enest', 1])]),
    ({'Two': {'ewrap': False, 'enest': [0, {}]}}, [({'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}, ['Two', 'enest', 1])]),
]

cases = {
    'boolean': [v for v in generate_basic_cases('bool!', bool, [False, True])],
    'integer': [v for v in generate_basic_cases('int!', int, [0, -1, 1, 9223372036854775807, -9223372036854775808], additional_integer_cases)],
    'number': [v for v in generate_basic_cases('num!', float, [0, -1, 1, -1.7976931348623157e+308, -2.2250738585072014e-308, 2.2250738585072014e-308, 1.7976931348623157e+308, -0.1, 0.1], additional_number_cases)],
    'string': [v for v in generate_basic_cases('str!', str, ['', 'abc'])],
    'array': [v for v in generate_basic_cases('arr!', list, [[], [False, 0, 0.1, '']])],
    'object': [v for v in generate_basic_cases('obj!', dict, [{}, {'a': False, 'b': 0, 'c': 0.1, 'd': ''}])],
    'any': [v for v in generate_basic_cases('any!', Any, [False, 0, 0.1, '', [], {}])],
    'struct' : [v for v in generate_basic_cases('struct!', dict, [{'required': True}, {'optional!': False, 'required': True}, {'optional2!': 0, 'required': True}, {'optional!': False, 'optional2!': 0, 'required': True}], additional_struct_cases)],
    'union' : [v for v in generate_basic_cases('union!', dict, [{'One': {}}, {'Two':{'required': True}}, {'Two':{'optional!': False, 'required': True}}], additional_union_cases)],
    'fn' : [v for v in generate_basic_cases('fn!', dict, [{'fn.example':{'required': True}}, {'fn.example':{'optional!': False, 'required': True}}], additional_fn_cases)],
    'testPing': [
        [[{}, {'fn.ping_': {}}], [{}, {'Ok_': {}}]],
    ],
    'testCallId': [
        [[{'id_': 'abcd'}, {'fn.ping_': {}}], [{'id_': 'abcd'}, {'Ok_': {}}]],
        [[{'id_': 1234}, {'fn.ping_': {}}], [{'id_': 1234}, {'Ok_': {}}]],
    ],
    'testUnknownFunction': [
        [[{}, {'fn.notFound': {}}], [{'_assert': {'skipFieldIdCheck': True}}, {'ErrorInvalidRequestBody_': {'cases': [{'path': ['fn.notFound'], 'reason': {'FunctionUnknown': {}}}]}}]],
    ],
    'testErrors': [
        [[{'result': {'ErrorExample': {'property': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorExample': {'property': 'a'}}]],
        [[{'result': {'ErrorExample': {'wrong': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorInvalidResponseBody_': {'cases': [{'path': ['ErrorExample'], 'reason': {'RequiredObjectKeyMissing': {'key': 'property'}}}, {'path': ['ErrorExample', 'wrong'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'result': {'errorUnknown': {'property': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorInvalidResponseBody_': {'cases': [{'path': ['errorUnknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
    ],
    'testSelectFields': [
        [[{'select_': {'struct.ExStruct': ['optional!']}, 'Ok_': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'optional!': False}}}}]],
        [[{'select_': {'struct.ExStruct': ['optional!']}, 'Ok_': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {}}}}]],
        [[{'select_': {'struct.ExStruct': ['optional!']}, 'Ok_': {'value!': {'struct!': {'optional!': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'optional!': False}}}}]],
        [[{'select_': {'struct.ExStruct': ['optional!', 'required']}, 'Ok_': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'optional!': False, 'required': False}}}}]],
        [[{'select_': {'struct.ExStruct': ['optional!', 'required']}, 'Ok_': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': False}}}}]],
        [[{'select_': {'struct.ExStruct': []}, 'Ok_': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {}}}}]],
        [[{'select_': {'struct.ExStruct': []}, 'Ok_': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {}}}}]],
        [[{'select_': {'union.ExUnion': {}}, 'Ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}]],
        [[{'select_': {'union.ExUnion': {'Two': ['optional!']}}, 'Ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'optional!': False}}}}}]],
        [[{'select_': {'union.ExUnion': {'Two': ['optional!']}}, 'Ok_': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'select_': {'union.ExUnion': {'Two': ['optional!']}}, 'Ok_': {'value!': {'union!': {'Two': {'optional!': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'optional!': False}}}}}]],
        [[{'select_': {'union.ExUnion': {'Two': ['optional!', 'required']}}, 'Ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}]],
        [[{'select_': {'union.ExUnion': {'Two': ['optional!', 'required']}}, 'Ok_': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'required': False}}}}}]],
        [[{'select_': {'union.ExUnion': {'Two': []}}, 'Ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'select_': {'union.ExUnion': {'Two': []}}, 'Ok_': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'select_': {'->': {'Ok_': []}}, 'Ok_': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {}}]],
        [[{'select_': {'->': {'Ok_': []}}, 'Ok_': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {}}]],
        [[{'select_': {'->': {'Ok_': ['optional!']}}, 'Ok_': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {'optional!': False}}]],
        [[{'select_': {'->': {'Ok_': ['optional!']}}, 'Ok_': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {}}]],
        [[{'select_': {'->': {'Ok_': ['optional!']}}, 'Ok_': {'optional!': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {'optional!': False}}]],
        [[{'select_': {'->': {'Ok_': ['optional!', 'required']}}, 'Ok_': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {'optional!': False, 'required': False}}]],
        [[{'select_': {'->': {'Ok_': ['optional!', 'required']}}, 'Ok_': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {'required': False}}]],
        [[{'select_': {'struct.ExStruct': ['optional!']}, 'Ok_': {'value!': {'arrStruct!': [{'required': False}, {'optional!': False, 'required': False}]}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'arrStruct!': [{}, {'optional!': False}]}}}]],
        [[{'select_': {'struct.ExStruct': ['optional!']}, 'Ok_': {'value!': {'objStruct!': {'a': {'required': False}, 'b': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'objStruct!': {'a': {}, 'b': {'optional!': False}}}}}]],
        [[{'select_': {'fn.example': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'fn.example'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'select_': None}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': False}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': 0}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': ''}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': []}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': {'': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', ''], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'select_': {'notStruct': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'notStruct'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'select_': {'struct.Unknown': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.Unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'select_': {'fn.notKnown': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'fn.notKnown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'select_': {'struct.ExStruct': None}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'struct.ExStruct': False}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'struct.ExStruct': 0}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'struct.ExStruct': ''}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'struct.ExStruct': {}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'struct.ExStruct': [None]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'struct.ExStruct': [False]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'struct.ExStruct': [0]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'struct.ExStruct': [[]]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'struct.ExStruct': [{}]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'struct.ExStruct': ['unknownField']}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'struct.ExStruct': ['']}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'union.ExUnion': None}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': False}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': 0}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': ''}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': None}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': False}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': 0}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': ''}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': {}}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'select_': {'union.ExUnion': {'Unknown': {}}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'Unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': [None]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': [False]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': [0]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': [[]]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'select_': {'union.ExUnion': {'One': [{}]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['select_', 'union.ExUnion', 'One', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
    ],
    'testUnsafe': [
        [[{'unsafe_': True, 'result': {'Ok_': {'value!': {'bool!': 0}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'bool!': 0}}}]],
        [[{'unsafe_': True, 'result': {'ErrorExample': {'wrong': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorExample': {'wrong': 'a'}}]],
    ],
    'testApplicationFailure': [
        [[{'throw': True}, {'fn.test': {}}], [{}, {'ErrorUnknown_': {}}]],
    ],
    'multipleFailures': [
        [[{}, {'fn.test': {'value!': {'struct!': {'optional!': 'wrong', 'a': False}}}}], [{'_assert': {'setCompare': True}}, {'ErrorInvalidRequestBody_': {'cases': [{'path': ['fn.test', 'value!', 'struct!', 'optional!'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}, {'path': ['fn.test', 'value!', 'struct!'], 'reason': {'RequiredObjectKeyMissing': {'key': 'required'}}}, {'path': ['fn.test', 'value!', 'struct!', 'a'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
    ],
    'api': [
        [[{}, {'fn.api_': {}}], [{}, {'Ok_': {'api': [{'///': [' This is the example schema. It is focussed on outlining type edge cases for     ', ' use in tests.                                                                   ', '                                                                                 ', ' As a reminder:                                                                  ', '                                                                                 ', ' - ! means optional field                                                        ', ' - ? means nullable type                                                         '], 'info.Example': {}}, {'///': ' An example function. ', 'fn.example': {'required': ['boolean'], 'optional!': ['boolean']}, '->': [{'Ok_': {'required': ['boolean'], 'optional!': ['boolean']}}]}, {'fn.getBigList': {}, '->': [{'Ok_': {'items': ['array', ['struct.Big']]}}]}, {'fn.test': {'value!': ['struct.Value']}, '->': [{'Ok_': {'value!': ['struct.Value']}}, {'ErrorExample': {'property': ['string']}}]}, {'requestHeader.in': ['boolean']}, {'responseHeader.out': ['boolean']}, {'struct.Big': {'aF': ['boolean'], 'cF': ['boolean'], 'bF': ['boolean'], 'dF': ['boolean']}}, {'///': [' The main struct example.                                                        ', '                                                                                 ', ' The [required] field must be supplied. The optional field does not need to be   ', ' supplied.                                                                       '], 'struct.ExStruct': {'required': ['boolean'], 'optional!': ['boolean'], 'optional2!': ['integer']}}, {'///': ' A struct value demonstrating all common type permutations. ', 'struct.Value': {'bool!': ['boolean'], 'nullBool!': ['boolean?'], 'arrBool!': ['array', ['boolean']], 'arrNullBool!': ['array', ['boolean?']], 'objBool!': ['object', ['boolean']], 'objNullBool!': ['object', ['boolean?']], 'int!': ['integer'], 'nullInt!': ['integer?'], 'arrInt!': ['array', ['integer']], 'arrNullInt!': ['array', ['integer?']], 'objInt!': ['object', ['integer']], 'objNullInt!': ['object', ['integer?']], 'num!': ['number'], 'nullNum!': ['number?'], 'arrNum!': ['array', ['number']], 'arrNullNum!': ['array', ['number?']], 'objNum!': ['object', ['number']], 'objNullNum!': ['object', ['number?']], 'str!': ['string'], 'nullStr!': ['string?'], 'arrStr!': ['array', ['string']], 'arrNullStr!': ['array', ['string?']], 'objStr!': ['object', ['string']], 'objNullStr!': ['object', ['string?']], 'arr!': ['array', ['any']], 'nullArr!': ['array?', ['any']], 'arrArr!': ['array', ['array', ['any']]], 'arrNullArr!': ['array', ['array?', ['any']]], 'objArr!': ['object', ['array', ['any']]], 'objNullArr!': ['object', ['array?', ['any']]], 'obj!': ['object', ['any']], 'nullObj!': ['object?', ['any']], 'arrObj!': ['array', ['object', ['any']]], 'arrNullObj!': ['array', ['object?', ['any']]], 'objObj!': ['object', ['object', ['any']]], 'objNullObj!': ['object', ['object?', ['any']]], 'any!': ['any'], 'nullAny!': ['any?'], 'arrAny!': ['array', ['any']], 'arrNullAny!': ['array', ['any?']], 'objAny!': ['object', ['any']], 'objNullAny!': ['object', ['any?']], 'struct!': ['struct.ExStruct'], 'nullStruct!': ['struct.ExStruct?'], 'arrStruct!': ['array', ['struct.ExStruct']], 'arrNullStruct!': ['array', ['struct.ExStruct?']], 'objStruct!': ['object', ['struct.ExStruct']], 'objNullStruct!': ['object', ['struct.ExStruct?']], 'union!': ['union.ExUnion'], 'nullUnion!': ['union.ExUnion?'], 'arrUnion!': ['array', ['union.ExUnion']], 'arrNullUnion!': ['array', ['union.ExUnion?']], 'objUnion!': ['object', ['union.ExUnion']], 'objNullUnion!': ['object', ['union.ExUnion?']], 'fn!': ['fn.example'], 'nullFn!': ['fn.example?'], 'arrFn!': ['array', ['fn.example']], 'arrNullFn!': ['array', ['fn.example?']], 'objFn!': ['object', ['fn.example']], 'objNullFn!': ['object', ['fn.example?']]}}, {'union.ExUnion': [{'One': {}}, {'Two': {'required': ['boolean'], 'optional!': ['boolean']}}]}]}}]],
    ],
    'serverHooks': [
        [[{'Ok_': {}, '_onRequestError': True}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
        [[{'Ok_': {}, '_onResponseError': True}, {'fn.test': {}}], [{'_onResponseError': True}, {'Ok_': {}}]],
        [[{'Ok_': {}, '_throwError': True}, {'fn.test': {}}], [{}, {'ErrorUnknown_': {}}]],
    ],
    'clientHeaders': [
        [[{'time_': 6000}, {'fn.ping_': {}}], [{}, {'Ok_': {}}]],
    ],
    'big': [
        [[{'Ok_': {'items': [{'aF': True, 'bF': False, 'cF': True, 'dF': False}, {'aF': True, 'dF': False, 'cF': False, 'bF': True}, {'cF': False, 'bF': True, 'aF': True, 'dF': False}]}}, {'fn.getBigList': {}}], [{}, {'Ok_': {'items': [{'aF': True, 'bF': False, 'cF': True, 'dF': False}, {'aF': True, 'dF': False, 'cF': False, 'bF': True}, {'cF': False, 'bF': True, 'aF': True, 'dF': False}]}}]]
    ],
    'customHeaders': [
        [[{'Ok_': {}, 'in': False, 'responseHeader': {'out': False}}, {'fn.test': {}}], [{'out': False}, {'Ok_': {}}]],
        [[{'Ok_': {}, 'in': 0}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['in'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok_': {}, 'in': ''}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['in'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok_': {}, 'in': []}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['in'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok_': {}, 'in': {}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['in'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok_': {}, 'responseHeader': {'out': 0}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['out'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok_': {}, 'responseHeader': {'out': ''}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['out'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok_': {}, 'responseHeader': {'out': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['out'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok_': {}, 'responseHeader': {'out': {}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['out'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}}]}}]],
    ]
}
