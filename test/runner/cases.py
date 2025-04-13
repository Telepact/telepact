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

from typing import Any
import base64

default_values = [False, 0, 0.1, '', [], {}]

class Base64String:
    pass


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
    elif the_type == Base64String:
        return 'Bytes'


def type_unexp(incorrect_value, the_type):
    return {'TypeUnexpected': {'actual': {get_type(type(incorrect_value), use_int=False): {}}, 'expected': {get_type(the_type): {}}}}

def cap(s: str):
    return s[:1].upper() + s[1:]

def b64(b: bytes):
    return base64.b64encode(b).decode('utf-8')

def get_values(given_field: str, the_type, given_correct_values, additional_incorrect_values):
    default_incorrect_values = list(filter(lambda n: type(n) not in (int, float) if the_type == float else type(n) not in (Base64String, str) if the_type == Base64String else False if the_type == Any else type(n) != the_type, default_values))
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
                expected_response_header['@assert_'] = {'skipFieldIdCheck': True}
            
            case = [[{'@good_': True, '@ok_': {'value!': {field: correct_value}}}, {'fn.test': {'value!': {field: correct_value}}}], [expected_response_header, {'Ok_': {'value!': {field: correct_value}}}]]

            yield case

        for incorrect_value, errors in incorrect_values:
            expected_response_header = {}
            cases = [{'path': ['fn.test', 'value!'] + base_path + path, 'reason': reason} for reason, path in errors]
            if len(cases) > 1:
                expected_response_header.setdefault('@assert_', {})['setCompare'] = True
            if has_too_many_keys(incorrect_value):
                expected_response_header.setdefault('@assert_', {})['skipFieldIdCheck'] = True

            yield [[{}, {'fn.test': {'value!': {field: incorrect_value}}}], [expected_response_header, {'ErrorInvalidRequestBody_': {'cases': cases}}]]

        for incorrect_value, errors in incorrect_values:
            expected_response_header = {}
            cases = [{'path': ['Ok_', 'value!'] + base_path + path, 'reason': reason} for reason, path in errors]
            if len(cases) > 1:
                expected_response_header.setdefault('@assert_', {})['setCompare'] = True
            if has_too_many_keys(incorrect_value):
                expected_response_header.setdefault('@assert_', {})['skipFieldIdCheck'] = True

            yield [[{'@ok_': {'value!': {field: incorrect_value}}}, {'fn.test': {}}], [expected_response_header, {'ErrorInvalidResponseBody_': {'cases': cases}}]]


additional_integer_cases = [
    (9223372036854775808, [({'NumberOutOfRange': {}}, [])]), 
    (-9223372036854775809, [({'NumberOutOfRange': {}}, [])])
]
additional_number_cases = [
    (9223372036854775808, [({'NumberOutOfRange': {}}, [])]),
    (-9223372036854775809, [({'NumberOutOfRange': {}}, [])])
]
additional_bytes_case = [
    ('@not_base64', [({'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Base64String': {}}}}, [])]),
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
sel_cases = [
    {'struct.ExStruct': ['optional!']},
    {'struct.ExStruct': ['optional!']},
    {'struct.ExStruct': ['optional!']},
    {'struct.ExStruct': ['optional!', 'required']},
    {'struct.ExStruct': ['optional!', 'required']},
    {'struct.ExStruct': []},
    {'struct.ExStruct': []},
    {'union.ExUnion': {}},
    {'union.ExUnion': {'Two': ['optional!']}},
    {'union.ExUnion': {'Two': ['optional!']}},
    {'union.ExUnion': {'Two': ['optional!']}},
    {'union.ExUnion': {'Two': ['optional!', 'required']}},
    {'union.ExUnion': {'Two': ['optional!', 'required']}},
    {'union.ExUnion': {'Two': []}},
    {'union.ExUnion': {'Two': []}},
    {'->': {'Ok_': []}},
    {'->': {'Ok_': []}},
    {'->': {'Ok_': ['optional!']}},
    {'->': {'Ok_': ['optional!']}},
    {'->': {'Ok_': ['optional!']}},
    {'->': {'Ok_': ['optional!', 'required']}},
    {'->': {'Ok_': ['optional!', 'required']}},
    {'struct.ExStruct': ['optional!']},
    {'struct.ExStruct': ['optional!']},
]
additional_sel_cases = [

]

cases = {
    'boolean': [v for v in generate_basic_cases('bool!', bool, [False, True])],
    'integer': [v for v in generate_basic_cases('int!', int, [0, -1, 1, 9223372036854775807, -9223372036854775808], additional_integer_cases)],
    'number': [v for v in generate_basic_cases('num!', float, [0, -1, 1, -1.7976931348623157e+308, -2.2250738585072014e-308, 2.2250738585072014e-308, 1.7976931348623157e+308, -0.1, 0.1], additional_number_cases)],
    'string': [v for v in generate_basic_cases('str!', str, ['', 'abc'])],
    'array': [v for v in generate_basic_cases('arr!', list, [[], [False, 0, 0.1, '']])],
    'object': [v for v in generate_basic_cases('obj!', dict, [{}, {'a': False, 'b': 0, 'c': 0.1, 'd': ''}])],
    'any': [v for v in generate_basic_cases('any!', Any, [False, 0, 0.1, '', [], {}])],
    'bytes': [v for v in generate_basic_cases('bytes!', Base64String, [b64(b''), b64(b'abc'), b64(b'\x00\x01\x02')], additional_bytes_case)],
    'struct' : [v for v in generate_basic_cases('struct!', dict, [{'required': True}, {'optional!': False, 'required': True}, {'optional2!': 0, 'required': True}, {'optional!': False, 'optional2!': 0, 'required': True}], additional_struct_cases)],
    'union' : [v for v in generate_basic_cases('union!', dict, [{'One': {}}, {'Two':{'required': True}}, {'Two':{'optional!': False, 'required': True}}], additional_union_cases)],
    'fn' : [v for v in generate_basic_cases('fn!', dict, [{'fn.example':{'required': True}}, {'fn.example':{'optional!': False, 'required': True}}], additional_fn_cases)],
    'sel' : [v for v in generate_basic_cases('sel!', dict, [{}])],
    'testPing': [
        [[{}, {'fn.ping_': {}}], [{}, {'Ok_': {}}]],
    ],
    'testCallId': [
        [[{'@id_': 'abcd'}, {'fn.ping_': {}}], [{'@id_': 'abcd'}, {'Ok_': {}}]],
        [[{'@id_': 1234}, {'fn.ping_': {}}], [{'@id_': 1234}, {'Ok_': {}}]],
    ],
    'testUnknownFunction': [
        [[{}, {'fn.notFound': {}}], [{'@assert_': {'skipFieldIdCheck': True}}, {'ErrorInvalidRequestBody_': {'cases': [{'path': ['fn.notFound'], 'reason': {'FunctionUnknown': {}}}]}}]],
    ],
    'testErrors': [
        [[{'@result': {'ErrorExample': {'property': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorExample': {'property': 'a'}}]],
        [[{'@result': {'ErrorExample': {'wrong': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorInvalidResponseBody_': {'cases': [{'path': ['ErrorExample'], 'reason': {'RequiredObjectKeyMissing': {'key': 'property'}}}, {'path': ['ErrorExample', 'wrong'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'@result': {'errorUnknown': {'property': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorInvalidResponseBody_': {'cases': [{'path': ['errorUnknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
    ],
    'testSelectFields': [
        [[{'@select_': {'struct.ExStruct': ['optional!']}, '@ok_': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'optional!': False}}}}]],
        [[{'@select_': {'struct.ExStruct': ['optional!']}, '@ok_': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {}}}}]],
        [[{'@select_': {'struct.ExStruct': ['optional!']}, '@ok_': {'value!': {'struct!': {'optional!': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'optional!': False}}}}]],
        [[{'@select_': {'struct.ExStruct': ['optional!', 'required']}, '@ok_': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'optional!': False, 'required': False}}}}]],
        [[{'@select_': {'struct.ExStruct': ['optional!', 'required']}, '@ok_': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': False}}}}]],
        [[{'@select_': {'struct.ExStruct': []}, '@ok_': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {}}}}]],
        [[{'@select_': {'struct.ExStruct': []}, '@ok_': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {}}}}]],
        [[{'@select_': {'struct.Big': []}, '@ok_': {'items': [{'aF': False, 'bF': True, 'cF': False, 'dF': True}]}}, {'fn.getBigList': {}}], [{}, {'Ok_': {'items': [{}]}}]],
        [[{'@select_': {'struct.Big': ['aF']}, '@ok_': {'items': [{'aF': False, 'bF': True, 'cF': False, 'dF': True}]}}, {'fn.getBigList': {}}], [{}, {'Ok_': {'items': [{'aF': False}]}}]],
        [[{'@select_': {'union.ExUnion': {}}, '@ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}]],
        [[{'@select_': {'union.ExUnion': {'Two': ['optional!']}}, '@ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'optional!': False}}}}}]],
        [[{'@select_': {'union.ExUnion': {'Two': ['optional!']}}, '@ok_': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'@select_': {'union.ExUnion': {'Two': ['optional!']}}, '@ok_': {'value!': {'union!': {'Two': {'optional!': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'optional!': False}}}}}]],
        [[{'@select_': {'union.ExUnion': {'Two': ['optional!', 'required']}}, '@ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}]],
        [[{'@select_': {'union.ExUnion': {'Two': ['optional!', 'required']}}, '@ok_': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {'required': False}}}}}]],
        [[{'@select_': {'union.ExUnion': {'Two': []}}, '@ok_': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'@select_': {'union.ExUnion': {'Two': []}}, '@ok_': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'@select_': {'->': {'Ok_': []}}, '@ok_': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {}}]],
        [[{'@select_': {'->': {'Ok_': []}}, '@ok_': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {}}]],
        [[{'@select_': {'->': {'Ok_': ['optional!']}}, '@ok_': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {'optional!': False}}]],
        [[{'@select_': {'->': {'Ok_': ['optional!']}}, '@ok_': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {}}]],
        [[{'@select_': {'->': {'Ok_': ['optional!']}}, '@ok_': {'optional!': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {'optional!': False}}]],
        [[{'@select_': {'->': {'Ok_': ['optional!', 'required']}}, '@ok_': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {'optional!': False, 'required': False}}]],
        [[{'@select_': {'->': {'Ok_': ['optional!', 'required']}}, '@ok_': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok_': {'required': False}}]],
        [[{'@select_': {'struct.ExStruct': ['optional!']}, '@ok_': {'value!': {'arrStruct!': [{'required': False}, {'optional!': False, 'required': False}]}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'arrStruct!': [{}, {'optional!': False}]}}}]],
        [[{'@select_': {'struct.ExStruct': ['optional!']}, '@ok_': {'value!': {'objStruct!': {'a': {'required': False}, 'b': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'objStruct!': {'a': {}, 'b': {'optional!': False}}}}}]],
        [[{'@select_': {'fn.example': []}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'fn.example'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'@select_': None}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': False}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': 0}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': ''}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': []}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': {'': []}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', ''], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'@select_': {'notStruct': []}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'notStruct'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'@select_': {'struct.Unknown': []}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.Unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'@select_': {'fn.notKnown': []}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'fn.notKnown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'@select_': {'struct.ExStruct': None}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'struct.ExStruct': False}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'struct.ExStruct': 0}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'struct.ExStruct': ''}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'struct.ExStruct': {}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'struct.ExStruct': [None]}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'struct.ExStruct': [False]}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'struct.ExStruct': [0]}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'struct.ExStruct': [[]]}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'struct.ExStruct': [{}]}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'struct.ExStruct': ['unknownField']}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'struct.ExStruct': ['']}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'struct.ExStruct', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'union.ExUnion': None}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': False}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': 0}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': ''}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': []}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': None}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': False}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': 0}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': ''}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': {}}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Unknown': {}}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': [None]}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': [False]}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': [0]}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': [[]]}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
        [[{'@select_': {'union.ExUnion': {'Two': [{}]}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@select_', 'union.ExUnion', 'Two', 0], 'reason': {'ArrayElementDisallowed': {}}}]}}]],
    ],
    'testUnsafe': [
        [[{'@unsafe_': True, '@result': {'Ok_': {'value!': {'bool!': 0}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'bool!': 0}}}]],
        [[{'@unsafe_': True, '@result': {'ErrorExample': {'wrong': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorExample': {'wrong': 'a'}}]],
    ],
    'testApplicationFailure': [
        [[{'@throw': True}, {'fn.test': {}}], [{}, {'ErrorUnknown_': {}}]],
    ],
    'multipleFailures': [
        [[{}, {'fn.test': {'value!': {'struct!': {'optional!': 'wrong', 'a': False}}}}], [{'@assert_': {'setCompare': True}}, {'ErrorInvalidRequestBody_': {'cases': [{'path': ['fn.test', 'value!', 'struct!', 'optional!'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}, {'path': ['fn.test', 'value!', 'struct!'], 'reason': {'RequiredObjectKeyMissing': {'key': 'required'}}}, {'path': ['fn.test', 'value!', 'struct!', 'a'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
    ],
    'api': [
        [[{}, {'fn.api_': {}}], [{}, {'Ok_': {'api': [{'///': [' This is the example schema. It is focussed on outlining type edge cases for     ', ' use in tests.                                                                   ', '                                                                                 ', ' As a reminder:                                                                  ', '                                                                                 ', ' - ! means optional field                                                        ', ' - ? means nullable type                                                         '], 'info.Example': {}}, {'fn.circularLink1': {'field1': ['boolean']}, '->': [{'Ok_': {'follow': ['fn.circularLink2']}}]}, {'fn.circularLink2': {'field2': ['boolean']}, '->': [{'Ok_': {'follow': ['fn.circularLink1']}}]}, {'///': ' An example function. ', 'fn.example': {'required': ['boolean'], 'optional!': ['boolean']}, '->': [{'Ok_': {'required': ['boolean'], 'optional!': ['boolean']}}]}, {'fn.getBigList': {}, '->': [{'Ok_': {'items': ['array', ['struct.Big']]}}]}, {'fn.selfLink': {'required': ['boolean'], 'optional!': ['boolean']}, '->': [{'Ok_': {'followSelf': ['fn.selfLink']}}]}, {'fn.test': {'value!': ['struct.Value']}, '->': [{'Ok_': {'value!': ['struct.Value']}}, {'ErrorExample': {'property': ['string']}}]}, {'headers.ExampleHeaders': {'@in': ['boolean']}, '->': {'@out': ['boolean']}}, {'struct.Big': {'aF': ['boolean'], 'cF': ['boolean'], 'bF': ['boolean'], 'dF': ['boolean']}}, {'///': [' The main struct example.                                                        ', '                                                                                 ', ' The [required] field must be supplied. The optional field does not need to be   ', ' supplied.                                                                       '], 'struct.ExStruct': {'required': ['boolean'], 'optional!': ['boolean'], 'optional2!': ['integer']}}, {'///': ' A struct value demonstrating all common type permutations. ', 'struct.Value': {'bool!': ['boolean'], 'nullBool!': ['boolean?'], 'arrBool!': ['array', ['boolean']], 'arrNullBool!': ['array', ['boolean?']], 'objBool!': ['object', ['boolean']], 'objNullBool!': ['object', ['boolean?']], 'int!': ['integer'], 'nullInt!': ['integer?'], 'arrInt!': ['array', ['integer']], 'arrNullInt!': ['array', ['integer?']], 'objInt!': ['object', ['integer']], 'objNullInt!': ['object', ['integer?']], 'num!': ['number'], 'nullNum!': ['number?'], 'arrNum!': ['array', ['number']], 'arrNullNum!': ['array', ['number?']], 'objNum!': ['object', ['number']], 'objNullNum!': ['object', ['number?']], 'str!': ['string'], 'nullStr!': ['string?'], 'arrStr!': ['array', ['string']], 'arrNullStr!': ['array', ['string?']], 'objStr!': ['object', ['string']], 'objNullStr!': ['object', ['string?']], 'any!': ['any'], 'nullAny!': ['any?'], 'arrAny!': ['array', ['any']], 'arrNullAny!': ['array', ['any?']], 'objAny!': ['object', ['any']], 'objNullAny!': ['object', ['any?']], 'bytes!': ['bytes'], 'nullBytes!': ['bytes?'], 'arrBytes!': ['array', ['bytes']], 'arrNullBytes!': ['array', ['bytes?']], 'objBytes!': ['object', ['bytes']], 'objNullBytes!': ['object', ['bytes?']], 'arr!': ['array', ['any']], 'nullArr!': ['array?', ['any']], 'arrArr!': ['array', ['array', ['any']]], 'arrNullArr!': ['array', ['array?', ['any']]], 'objArr!': ['object', ['array', ['any']]], 'objNullArr!': ['object', ['array?', ['any']]], 'obj!': ['object', ['any']], 'nullObj!': ['object?', ['any']], 'arrObj!': ['array', ['object', ['any']]], 'arrNullObj!': ['array', ['object?', ['any']]], 'objObj!': ['object', ['object', ['any']]], 'objNullObj!': ['object', ['object?', ['any']]], 'struct!': ['struct.ExStruct'], 'nullStruct!': ['struct.ExStruct?'], 'arrStruct!': ['array', ['struct.ExStruct']], 'arrNullStruct!': ['array', ['struct.ExStruct?']], 'objStruct!': ['object', ['struct.ExStruct']], 'objNullStruct!': ['object', ['struct.ExStruct?']], 'union!': ['union.ExUnion'], 'nullUnion!': ['union.ExUnion?'], 'arrUnion!': ['array', ['union.ExUnion']], 'arrNullUnion!': ['array', ['union.ExUnion?']], 'objUnion!': ['object', ['union.ExUnion']], 'objNullUnion!': ['object', ['union.ExUnion?']], 'fn!': ['fn.example'], 'nullFn!': ['fn.example?'], 'arrFn!': ['array', ['fn.example']], 'arrNullFn!': ['array', ['fn.example?']], 'objFn!': ['object', ['fn.example']], 'objNullFn!': ['object', ['fn.example?']], 'sel!': ['_ext.Select_'], 'nullSel!': ['_ext.Select_?'], 'arrSel!': ['array', ['_ext.Select_']], 'arrNullSel!': ['array', ['_ext.Select_?']], 'objSel!': ['object', ['_ext.Select_']], 'objNullSel!': ['object', ['_ext.Select_?']]}}, {'union.ExUnion': [{'One': {}}, {'Two': {'required': ['boolean'], 'optional!': ['boolean']}}]}]}}]],
    ],
    'serverHooks': [
        [[{'@ok_': {}, '@onRequestError_': True}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
        [[{'@ok_': {}, '@onResponseError_': True}, {'fn.test': {}}], [{'@onResponseError_': True}, {'Ok_': {}}]],
        [[{'@ok_': {}, '@throwError_': True}, {'fn.test': {}}], [{}, {'ErrorUnknown_': {}}]],
    ],
    'clientHeaders': [
        [[{'@time_': 6000}, {'fn.ping_': {}}], [{}, {'Ok_': {}}]],
    ],
    'big': [
        [[{'@ok_': {'items': [{'aF': True, 'bF': False, 'cF': True, 'dF': False}, {'aF': True, 'dF': False, 'cF': False, 'bF': True}, {'cF': False, 'bF': True, 'aF': True, 'dF': False}]}}, {'fn.getBigList': {}}], [{}, {'Ok_': {'items': [{'aF': True, 'bF': False, 'cF': True, 'dF': False}, {'aF': True, 'dF': False, 'cF': False, 'bF': True}, {'cF': False, 'bF': True, 'aF': True, 'dF': False}]}}]]
    ],
    'customHeaders': [
        [[{'@ok_': {}, '@in': False, '@responseHeader': {'@out': False}}, {'fn.test': {}}], [{'@out': False}, {'Ok_': {}}]],
        [[{'@ok_': {}, '@in': 0}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@in'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'@ok_': {}, '@in': ''}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@in'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'@ok_': {}, '@in': []}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@in'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'@ok_': {}, '@in': {}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@in'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'@ok_': {}, 'randomIn': {}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['randomIn'], 'reason': {'RequiredObjectKeyPrefixMissing': {'prefix': '@'}}}]}}]],
        [[{'@ok_': {}, '@responseHeader': {'@out': 0}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['@out'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'@ok_': {}, '@responseHeader': {'@out': ''}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['@out'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'@ok_': {}, '@responseHeader': {'@out': []}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['@out'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'@ok_': {}, '@responseHeader': {'@out': {}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['@out'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'@ok_': {}, '@responseHeader': {'randomOut': {}}}, {'fn.test': {}}], [{'@assert_': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'ErrorInvalidResponseHeaders_': {'cases': [{'path': ['randomOut'], 'reason': {'RequiredObjectKeyPrefixMissing': {'prefix': '@'}}}]}}]],
    ]
}
