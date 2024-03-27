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

    field = 'pStr{}'.format(cap(given_field))
    correct_values = [{'wrap': v} for v in given_correct_values]
    incorrect_values = [({'wrap': v}, e) for v, e in given_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, [field, 'wrap']

    field = 'pStrNull{}'.format(cap(given_field))
    correct_values = [{'wrap': v} for v in [None] + given_correct_values]
    incorrect_values = [({'wrap': v}, e) for v, e in given_incorrect_values]
    yield field, correct_values, incorrect_values, [field, 'wrap']

    field = 'pUnion{}'.format(cap(given_field))
    correct_values = [{'One': {}}] + [{'Two': {'ewrap': v}} for v in given_correct_values]
    incorrect_values = [({'Two': {'ewrap': v}}, e) for v, e in given_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, [field, 'Two', 'ewrap']

    field = 'pUnionNull{}'.format(cap(given_field))
    correct_values = [{'One': {}}] + [{'Two': {'ewrap': v}} for v in [None] + given_correct_values]
    incorrect_values = [({'Two': {'ewrap': v}}, e) for v, e in given_incorrect_values]
    yield field, correct_values, incorrect_values, [field, 'Two', 'ewrap']

    field = 'arrPStr{}'.format(cap(given_field))
    init_correct_values = [{'wrap': v} for v in given_correct_values]
    correct_values = [[]] + [[v] for v in init_correct_values] + [init_correct_values]
    init_incorrect_values_w_null = [({'wrap': v}, e) for v, e in given_incorrect_values_w_null]
    incorrect_values = [([init_correct_values[0], v], [(r, p)]) for v, [(r, p)] in init_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, [field, 1, 'wrap']

    field = 'arrP2Str{}'.format(cap(given_field))
    init_correct_values = [{'wrap': False, 'nest': [v]} for v in given_correct_values]
    correct_values = [[]] + [[v] for v in init_correct_values] + [init_correct_values]
    init_incorrect_values_w_null = [({'wrap': False, 'nest': [v]}, e) for v, e in given_incorrect_values_w_null]
    incorrect_values = [([init_correct_values[0], v], [(r, p)]) for v, [(r, p)] in init_incorrect_values_w_null]
    yield field, correct_values, incorrect_values, [field, 1, 'nest', 0]


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
            
            case = [[{'Ok': {'value!': {field: correct_value}}}, {'fn.test': {'value!': {field: correct_value}}}], [expected_response_header, {'Ok': {'value!': {field: correct_value}}}]]

            yield case

        for incorrect_value, errors in incorrect_values:
            expected_response_header = {}
            cases = [{'path': ['fn.test', 'value!'] + base_path + path, 'reason': reason} for reason, path in errors]
            if len(cases) > 1:
                expected_response_header.setdefault('_assert', {})['setCompare'] = True
            if has_too_many_keys(incorrect_value):
                expected_response_header.setdefault('_assert', {})['skipFieldIdCheck'] = True

            yield [[{}, {'fn.test': {'value!': {field: incorrect_value}}}], [expected_response_header, {'_ErrorInvalidRequestBody': {'cases': cases}}]]

        for incorrect_value, errors in incorrect_values:
            expected_response_header = {}
            cases = [{'path': ['Ok', 'value!'] + base_path + path, 'reason': reason} for reason, path in errors]
            if len(cases) > 1:
                expected_response_header.setdefault('_assert', {})['setCompare'] = True
            if has_too_many_keys(incorrect_value):
                expected_response_header.setdefault('_assert', {})['skipFieldIdCheck'] = True

            yield [[{'Ok': {'value!': {field: incorrect_value}}}, {'fn.test': {}}], [expected_response_header, {'_ErrorInvalidResponseBody': {'cases': cases}}]]


additional_integer_cases = [
    (9223372036854775808, [({'NumberOutOfRange': {}}, [])]), 
    (-9223372036854775809, [({'NumberOutOfRange': {}}, [])])
]
additional_number_cases = [
    (9223372036854775808, [({'NumberOutOfRange': {}}, [])]),
    (-9223372036854775809, [({'NumberOutOfRange': {}}, [])])
]
additional_struct_cases = [
    ({}, [({'RequiredObjectKeyMissing': {}}, ['required'])]),
    ({'required': False, 'a': False}, [({'ObjectKeyDisallowed': {}}, ['a'])])
]
additional_union_cases = [
    ({}, [({'ObjectSizeUnexpected': {'actual': 0, 'expected': 1}}, [])]),
    ({'One': {}, 'Two': {'optional!': False, 'required': False}}, [({'ObjectSizeUnexpected': {'actual': 2, 'expected': 1}}, [])]),
    ({'a': {}}, [({'ObjectKeyDisallowed': {}}, ['a'])]),
    ({'Two': {}}, [({'RequiredObjectKeyMissing': {}}, ['Two', 'required'])]),
    ({'One': False}, [({'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}, ['One'])]),
    ({'One': 0}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}, ['One'])]),
    ({'One': 0.1}, [({'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}, ['One'])]),
    ({'One': ''}, [({'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}, ['One'])]),
    ({'One': []}, [({'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}, ['One'])]),
]
additional_fn_cases = [
    ({}, [({'ObjectSizeUnexpected': {'actual': 0, 'expected': 1}}, [])]),
    ({'a': {}}, [({'ObjectKeyDisallowed': {}}, ['a'])]),
    ({'fn.example': {}}, [({'RequiredObjectKeyMissing': {}}, ['fn.example', 'required'])]),
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
    'p2Str': [v for v in generate_basic_cases('p2Str!', dict, [{'wrap': False, 'nest': [0]}, {'wrap': True, 'nest': [1]}], additional_p2Str_cases)],
    'p2Union': [v for v in generate_basic_cases('p2Union!', dict, [{'Two': {'ewrap': False, 'enest': [0]}}, {'Two': {'ewrap': True, 'enest': [1]}}], additional_p2Union_cases)],
    'testPdStr': [
        [[{'Ok': {'value!': {'pdStr!': {'dwrap': {'wrap': False}}}}}, {'fn.test': {'value!': {'pdStr!': {'dwrap': {'wrap': False}}}}}], [{}, {'Ok': {'value!': {'pdStr!': {'dwrap': {'wrap': False}}}}}]],
    ],
    'testPing': [
        [[{}, {'fn._ping': {}}], [{}, {'Ok': {}}]],
    ],
    'testCallId': [
        [[{'_id': 'abcd'}, {'fn._ping': {}}], [{'_id': 'abcd'}, {'Ok': {}}]],
        [[{'_id': 1234}, {'fn._ping': {}}], [{'_id': 1234}, {'Ok': {}}]],
    ],
    'testUnknownFunction': [
        [[{}, {'fn.notFound': {}}], [{'_assert': {'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestBody': {'cases': [{'path': ['fn.notFound'], 'reason': {'FunctionUnknown': {}}}]}}]],
    ],
    'testErrors': [
        [[{'result': {'ErrorExample': {'property': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorExample': {'property': 'a'}}]],
        [[{'result': {'ErrorExample': {'wrong': 'a'}}}, {'fn.test': {}}], [{}, {'_ErrorInvalidResponseBody': {'cases': [{'path': ['ErrorExample', 'property'], 'reason': {'RequiredObjectKeyMissing': {}}}, {'path': ['ErrorExample', 'wrong'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'result': {'errorUnknown': {'property': 'a'}}}, {'fn.test': {}}], [{}, {'_ErrorInvalidResponseBody': {'cases': [{'path': ['errorUnknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
    ],
    'testSelectFields': [
        [[{'_sel': {'struct.ExStruct': ['optional!']}, 'Ok': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'struct!': {'optional!': False}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional!']}, 'Ok': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'struct!': {}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional!']}, 'Ok': {'value!': {'struct!': {'optional!': False}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'struct!': {'optional!': False}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional!', 'required']}, 'Ok': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'struct!': {'optional!': False, 'required': False}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional!', 'required']}, 'Ok': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'struct!': {'required': False}}}}]],
        [[{'_sel': {'struct.ExStruct': []}, 'Ok': {'value!': {'struct!': {'optional!': False, 'required': False}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'struct!': {}}}}]],
        [[{'_sel': {'struct.ExStruct': []}, 'Ok': {'value!': {'struct!': {'required': False}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'struct!': {}}}}]],
        [[{'_sel': {'union.ExUnion': {}}, 'Ok': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}]],
        [[{'_sel': {'union.ExUnion': {'Two': ['optional!']}}, 'Ok': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'union!': {'Two': {'optional!': False}}}}}]],
        [[{'_sel': {'union.ExUnion': {'Two': ['optional!']}}, 'Ok': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'_sel': {'union.ExUnion': {'Two': ['optional!']}}, 'Ok': {'value!': {'union!': {'Two': {'optional!': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'union!': {'Two': {'optional!': False}}}}}]],
        [[{'_sel': {'union.ExUnion': {'Two': ['optional!', 'required']}}, 'Ok': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}]],
        [[{'_sel': {'union.ExUnion': {'Two': ['optional!', 'required']}}, 'Ok': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'union!': {'Two': {'required': False}}}}}]],
        [[{'_sel': {'union.ExUnion': {'Two': []}}, 'Ok': {'value!': {'union!': {'Two': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'_sel': {'union.ExUnion': {'Two': []}}, 'Ok': {'value!': {'union!': {'Two': {'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'union!': {'Two': {}}}}}]],
        [[{'_sel': {'->': {'Ok': []}}, 'Ok': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok': {}}]],
        [[{'_sel': {'->': {'Ok': []}}, 'Ok': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok': {}}]],
        [[{'_sel': {'->': {'Ok': ['optional!']}}, 'Ok': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok': {'optional!': False}}]],
        [[{'_sel': {'->': {'Ok': ['optional!']}}, 'Ok': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok': {}}]],
        [[{'_sel': {'->': {'Ok': ['optional!']}}, 'Ok': {'optional!': False}}, {'fn.example': {'required': False}}], [{}, {'Ok': {'optional!': False}}]],
        [[{'_sel': {'->': {'Ok': ['optional!', 'required']}}, 'Ok': {'optional!': False, 'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok': {'optional!': False, 'required': False}}]],
        [[{'_sel': {'->': {'Ok': ['optional!', 'required']}}, 'Ok': {'required': False}}, {'fn.example': {'required': False}}], [{}, {'Ok': {'required': False}}]],
        [[{'_sel': {'fn.example': ['optional!']}, 'Ok': {'value!': {'fn!': {'fn.example': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'fn!': {'fn.example': {'optional!': True}}}}}]],
        [[{'_sel': {'fn.example': ['optional!']}, 'Ok': {'value!': {'fn!': {'fn.example': {'required': True}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'fn!': {'fn.example': {}}}}}]],
        [[{'_sel': {'fn.example': ['optional!']}, 'Ok': {'value!': {'fn!': {'fn.example': {'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'fn!': {'fn.example': {'optional!': True}}}}}]],
        [[{'_sel': {'fn.example': ['optional!', 'required']}, 'Ok': {'value!': {'fn!': {'fn.example': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'fn!': {'fn.example': {'optional!': True, 'required': True}}}}}]],
        [[{'_sel': {'fn.example': ['optional!', 'required']}, 'Ok': {'value!': {'fn!': {'fn.example': {'required': True}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'fn!': {'fn.example': {'required': True}}}}}]],
        [[{'_sel': {'fn.example': []}, 'Ok': {'value!': {'fn!': {'fn.example': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'fn!': {'fn.example': {}}}}}]],
        [[{'_sel': {'fn.example': []}, 'Ok': {'value!': {'fn!': {'fn.example': {'required': True}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'fn!': {'fn.example': {}}}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional!']}, 'Ok': {'value!': {'arrStruct!': [{'required': False}, {'optional!': False, 'required': False}]}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'arrStruct!': [{}, {'optional!': False}]}}}]],
        [[{'_sel': {'struct.ExStruct': ['optional!']}, 'Ok': {'value!': {'objStruct!': {'a': {'required': False}, 'b': {'optional!': False, 'required': False}}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'objStruct!': {'a': {}, 'b': {'optional!': False}}}}}]],
        [[{'_sel': None}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': False}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': 0}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': ''}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': []}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': {'': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', ''], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'_sel': {'notStruct': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'notStruct'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'_sel': {'struct.Unknown': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.Unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'_sel': {'fn.notKnown': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'fn.notKnown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'_sel': {'struct.ExStruct': None}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': False}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': 0}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': ''}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': {}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [None]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [False]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [0]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [[]]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': [{}]}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'struct.ExStruct': ['unknownField']}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct', 0], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'_sel': {'struct.ExStruct': ['']}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'struct.ExStruct', 0], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'_sel': {'union.ExUnion': None}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': False}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': 0}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': ''}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': []}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': None}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': False}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': 0}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': ''}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': {}}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'Unknown': {}}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'Unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': [None]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': [False]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': [0]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': [[]]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{'_sel': {'union.ExUnion': {'One': [{}]}}}, {'fn.test': {}}], [{'_assert': {'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_sel', 'union.ExUnion', 'One', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
    ],
    'testUnsafe': [
        [[{'_unsafe': True, 'result': {'Ok': {'value!': {'bool!': 0}}}}, {'fn.test': {}}], [{}, {'Ok': {'value!': {'bool!': 0}}}]],
        [[{'_unsafe': True, 'result': {'ErrorExample': {'wrong': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorExample': {'wrong': 'a'}}]],
    ],
    'testApplicationFailure': [
        [[{'throw': True}, {'fn.test': {}}], [{}, {'_ErrorUnknown': {}}]],
    ],
    'multipleFailures': [
        [[{}, {'fn.test': {'value!': {'struct!': {'optional!': 'wrong', 'a': False}}}}], [{'_assert': {'setCompare': True}}, {'_ErrorInvalidRequestBody': {'cases': [{'path': ['fn.test', 'value!', 'struct!', 'optional!'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}, {'path': ['fn.test', 'value!', 'struct!', 'required'], 'reason': {'RequiredObjectKeyMissing': {}}}, {'path': ['fn.test', 'value!', 'struct!', 'a'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
    ],
    'api': [
        [[{}, {'fn._api': {}}], [{}, {'Ok': {'api': [{'///': [' This is the example schema. It is focussed on outlining type edge cases for use in tests. ', '                                                                                           ', ' As a reminder:                                                                            ', ' - ! means optional field                                                                  ', ' - ? means nullable type                                                                   '], 'info.Example': {}}, {'///': ' A struct value demonstrating all common type permutations. ', 'struct.Value': {'bool!': ['boolean'], 'nullBool!': ['boolean?'], 'arrBool!': ['array', ['boolean']], 'arrNullBool!': ['array', ['boolean?']], 'objBool!': ['object', ['boolean']], 'objNullBool!': ['object', ['boolean?']], 'pStrBool!': ['struct<1>.PStr', ['boolean']], 'pStrNullBool!': ['struct<1>.PStr', ['boolean?']], 'pUnionBool!': ['union<1>.PUnion', ['boolean']], 'pUnionNullBool!': ['union<1>.PUnion', ['boolean?']], 'arrPStrBool!': ['array', ['struct<1>.PStr', ['boolean']]], 'arrP2StrBool!': ['array', ['struct<2>.P2Str', ['boolean'], ['boolean']]], 'int!': ['integer'], 'nullInt!': ['integer?'], 'arrInt!': ['array', ['integer']], 'arrNullInt!': ['array', ['integer?']], 'objInt!': ['object', ['integer']], 'objNullInt!': ['object', ['integer?']], 'pStrInt!': ['struct<1>.PStr', ['integer']], 'pStrNullInt!': ['struct<1>.PStr', ['integer?']], 'pUnionInt!': ['union<1>.PUnion', ['integer']], 'pUnionNullInt!': ['union<1>.PUnion', ['integer?']], 'arrPStrInt!': ['array', ['struct<1>.PStr', ['integer']]], 'arrP2StrInt!': ['array', ['struct<2>.P2Str', ['boolean'], ['integer']]], 'num!': ['number'], 'nullNum!': ['number?'], 'arrNum!': ['array', ['number']], 'arrNullNum!': ['array', ['number?']], 'objNum!': ['object', ['number']], 'objNullNum!': ['object', ['number?']], 'pStrNum!': ['struct<1>.PStr', ['number']], 'pStrNullNum!': ['struct<1>.PStr', ['number?']], 'pUnionNum!': ['union<1>.PUnion', ['number']], 'pUnionNullNum!': ['union<1>.PUnion', ['number?']], 'arrPStrNum!': ['array', ['struct<1>.PStr', ['number']]], 'arrP2StrNum!': ['array', ['struct<2>.P2Str', ['boolean'], ['number']]], 'str!': ['string'], 'nullStr!': ['string?'], 'arrStr!': ['array', ['string']], 'arrNullStr!': ['array', ['string?']], 'objStr!': ['object', ['string']], 'objNullStr!': ['object', ['string?']], 'pStrStr!': ['struct<1>.PStr', ['string']], 'pStrNullStr!': ['struct<1>.PStr', ['string?']], 'pUnionStr!': ['union<1>.PUnion', ['string']], 'pUnionNullStr!': ['union<1>.PUnion', ['string?']], 'arrPStrStr!': ['array', ['struct<1>.PStr', ['string']]], 'arrP2StrStr!': ['array', ['struct<2>.P2Str', ['boolean'], ['string']]], 'arr!': ['array', ['any']], 'nullArr!': ['array?', ['any']], 'arrArr!': ['array', ['array', ['any']]], 'arrNullArr!': ['array', ['array?', ['any']]], 'objArr!': ['object', ['array', ['any']]], 'objNullArr!': ['object', ['array?', ['any']]], 'pStrArr!': ['struct<1>.PStr', ['array', ['any']]], 'pStrNullArr!': ['struct<1>.PStr', ['array?', ['any']]], 'pUnionArr!': ['union<1>.PUnion', ['array', ['any']]], 'pUnionNullArr!': ['union<1>.PUnion', ['array?', ['any']]], 'arrPStrArr!': ['array', ['struct<1>.PStr', ['array', ['any']]]], 'arrP2StrArr!': ['array', ['struct<2>.P2Str', ['boolean'], ['array', ['any']]]], 'obj!': ['object', ['any']], 'nullObj!': ['object?', ['any']], 'arrObj!': ['array', ['object', ['any']]], 'arrNullObj!': ['array', ['object?', ['any']]], 'objObj!': ['object', ['object', ['any']]], 'objNullObj!': ['object', ['object?', ['any']]], 'pStrObj!': ['struct<1>.PStr', ['object', ['any']]], 'pStrNullObj!': ['struct<1>.PStr', ['object?', ['any']]], 'pUnionObj!': ['union<1>.PUnion', ['object', ['any']]], 'pUnionNullObj!': ['union<1>.PUnion', ['object?', ['any']]], 'arrPStrObj!': ['array', ['struct<1>.PStr', ['object', ['any']]]], 'arrP2StrObj!': ['array', ['struct<2>.P2Str', ['boolean'], ['object', ['any']]]], 'any!': ['any'], 'nullAny!': ['any?'], 'arrAny!': ['array', ['any']], 'arrNullAny!': ['array', ['any?']], 'objAny!': ['object', ['any']], 'objNullAny!': ['object', ['any?']], 'pStrAny!': ['struct<1>.PStr', ['any']], 'pStrNullAny!': ['struct<1>.PStr', ['any?']], 'pUnionAny!': ['union<1>.PUnion', ['any']], 'pUnionNullAny!': ['union<1>.PUnion', ['any?']], 'arrPStrAny!': ['array', ['struct<1>.PStr', ['any']]], 'arrP2StrAny!': ['array', ['struct<2>.P2Str', ['boolean'], ['any']]], 'struct!': ['struct.ExStruct'], 'nullStruct!': ['struct.ExStruct?'], 'arrStruct!': ['array', ['struct.ExStruct']], 'arrNullStruct!': ['array', ['struct.ExStruct?']], 'objStruct!': ['object', ['struct.ExStruct']], 'objNullStruct!': ['object', ['struct.ExStruct?']], 'pStrStruct!': ['struct<1>.PStr', ['struct.ExStruct']], 'pStrNullStruct!': ['struct<1>.PStr', ['struct.ExStruct?']], 'pUnionStruct!': ['union<1>.PUnion', ['struct.ExStruct']], 'pUnionNullStruct!': ['union<1>.PUnion', ['struct.ExStruct?']], 'arrPStrStruct!': ['array', ['struct<1>.PStr', ['struct.ExStruct']]], 'arrP2StrStruct!': ['array', ['struct<2>.P2Str', ['boolean'], ['struct.ExStruct']]], 'union!': ['union.ExUnion'], 'nullUnion!': ['union.ExUnion?'], 'arrUnion!': ['array', ['union.ExUnion']], 'arrNullUnion!': ['array', ['union.ExUnion?']], 'objUnion!': ['object', ['union.ExUnion']], 'objNullUnion!': ['object', ['union.ExUnion?']], 'pStrUnion!': ['struct<1>.PStr', ['union.ExUnion']], 'pStrNullUnion!': ['struct<1>.PStr', ['union.ExUnion?']], 'pUnionUnion!': ['union<1>.PUnion', ['union.ExUnion']], 'pUnionNullUnion!': ['union<1>.PUnion', ['union.ExUnion?']], 'arrPStrUnion!': ['array', ['struct<1>.PStr', ['union.ExUnion']]], 'arrP2StrUnion!': ['array', ['struct<2>.P2Str', ['boolean'], ['union.ExUnion']]], 'fn!': ['fn.example'], 'nullFn!': ['fn.example?'], 'arrFn!': ['array', ['fn.example']], 'arrNullFn!': ['array', ['fn.example?']], 'objFn!': ['object', ['fn.example']], 'objNullFn!': ['object', ['fn.example?']], 'pStrFn!': ['struct<1>.PStr', ['fn.example']], 'pStrNullFn!': ['struct<1>.PStr', ['fn.example?']], 'pUnionFn!': ['union<1>.PUnion', ['fn.example']], 'pUnionNullFn!': ['union<1>.PUnion', ['fn.example?']], 'arrPStrFn!': ['array', ['struct<1>.PStr', ['fn.example']]], 'arrP2StrFn!': ['array', ['struct<2>.P2Str', ['boolean'], ['fn.example']]], 'p2Str!': ['struct<2>.P2Str', ['boolean'], ['integer']], 'nullP2Str!': ['struct<2>.P2Str?', ['boolean'], ['integer']], 'arrP2Str!': ['array', ['struct<2>.P2Str', ['boolean'], ['integer']]], 'arrNullP2Str!': ['array', ['struct<2>.P2Str?', ['boolean'], ['integer']]], 'objP2Str!': ['object', ['struct<2>.P2Str', ['boolean'], ['integer']]], 'objNullP2Str!': ['object', ['struct<2>.P2Str?', ['boolean'], ['integer']]], 'pStrP2Str!': ['struct<1>.PStr', ['struct<2>.P2Str', ['boolean'], ['integer']]], 'pStrNullP2Str!': ['struct<1>.PStr', ['struct<2>.P2Str?', ['boolean'], ['integer']]], 'pUnionP2Str!': ['union<1>.PUnion', ['struct<2>.P2Str', ['boolean'], ['integer']]], 'pUnionNullP2Str!': ['union<1>.PUnion', ['struct<2>.P2Str?', ['boolean'], ['integer']]], 'arrPStrP2Str!': ['array', ['struct<1>.PStr', ['struct<2>.P2Str', ['boolean'], ['integer']]]], 'arrP2StrP2Str!': ['array', ['struct<2>.P2Str', ['boolean'], ['struct<2>.P2Str', ['boolean'], ['integer']]]], 'p2Union!': ['union<2>.P2Union', ['boolean'], ['integer']], 'nullP2Union!': ['union<2>.P2Union?', ['boolean'], ['integer']], 'arrP2Union!': ['array', ['union<2>.P2Union', ['boolean'], ['integer']]], 'arrNullP2Union!': ['array', ['union<2>.P2Union?', ['boolean'], ['integer']]], 'objP2Union!': ['object', ['union<2>.P2Union', ['boolean'], ['integer']]], 'objNullP2Union!': ['object', ['union<2>.P2Union?', ['boolean'], ['integer']]], 'pStrP2Union!': ['struct<1>.PStr', ['union<2>.P2Union', ['boolean'], ['integer']]], 'pStrNullP2Union!': ['struct<1>.PStr', ['union<2>.P2Union?', ['boolean'], ['integer']]], 'pUnionP2Union!': ['union<1>.PUnion', ['union<2>.P2Union', ['boolean'], ['integer']]], 'pUnionNullP2Union!': ['union<1>.PUnion', ['union<2>.P2Union?', ['boolean'], ['integer']]], 'arrPStrP2Union!': ['array', ['struct<1>.PStr', ['union<2>.P2Union', ['boolean'], ['integer']]]], 'arrP2StrP2Union!': ['array', ['struct<2>.P2Str', ['boolean'], ['union<2>.P2Union', ['boolean'], ['integer']]]], 'pdStr!': ['struct<1>.PdStr', ['struct<1>.PStr', ['boolean']]]}}, {'///': [' The main struct example.                                                                ', '                                                                                         ', ' The [required] field must be supplied. The optional field does not need to be supplied. '], 'struct.ExStruct': {'required': ['boolean'], 'optional!': ['boolean'], 'optional2!': ['integer']}}, {'union.ExUnion': {'One': {}, 'Two': {'required': ['boolean'], 'optional!': ['boolean']}}}, {'struct<1>.PStr': {'wrap': ['T.0']}}, {'struct<1>.PdStr': {'dwrap': ['struct<1>.PStr', ['boolean']]}}, {'struct<2>.P2Str': {'wrap': ['T.0'], 'nest': ['array', ['T.1']]}}, {'union<1>.PUnion': {'One': {}, 'Two': {'ewrap': ['T.0']}}}, {'union<2>.P2Union': {'One': {}, 'Two': {'ewrap': ['T.0'], 'enest': ['array', ['T.1']]}}}, {'struct.Big': {'aF': ['boolean'], 'cF': ['boolean'], 'bF': ['boolean'], 'dF': ['boolean']}}, {'///': 'An example function.', 'fn.example': {'required': ['boolean'], 'optional!': ['boolean']}, '->': {'Ok': {'required': ['boolean'], 'optional!': ['boolean']}}}, {'fn.test': {'value!': ['struct.Value']}, '->': {'Ok': {'value!': ['struct.Value']}, 'ErrorExample': {'property': ['string']}}}, {'fn.getBigList': {}, '->': {'Ok': {'items': ['array', ['struct.Big']]}}}, {'///': ' Ping the server. ', 'fn._ping': {}, '->': {'Ok': {}}, 'errors': '^error\\._Validated$'}, {'///': ' Get the uAPI `schema` of this server. ', 'fn._api': {}, '->': {'Ok': {'api': ['array', ['object', ['any']]]}}, 'errors': '^error\\._Validated$'}, {'///': [' A placeholder function when the requested function is unknown. '], 'fn._unknown': {}, '->': {'Ok': {}}, 'errors': '^error\\._Validated$'}, {'struct._Auth': {}, 'ignoreIfDuplicate': True}, {'_ext._Select': {}}, {'///': [' uAPI standard headers.                                                                   ', '                                                                                          ', ' A `_id` request header will be reflected as-is in the `_id` response header.             ', '                                                                                          ', ' The `_sel` header is used to select fields from structs. It is an object of string       ', ' arrays keyed by struct reference name pointing to field names of that struct that should ', ' be selected. Field names not included in the array are omitted in the response wherever  ', ' that field would have appeared.                                                          ', '                                                                                          ', ' If the `_unsafe` request header is set to `true`, response validation by the server will ', ' be disabled.                                                                             ', '                                                                                          ', ' The `_tim` request header represents the timeout in milliseconds set by the client       ', ' when the request was submitted.                                                          ', '                                                                                          ', ' A `_bin` request header indicates the binary checksums known by the client, which will   ', ' prompt the inclusion of the `_bin` response header with the binary checksum currently in ', ' use by the server. If server binary checksum does not match one of the client-indicated  ', ' binary checksums in the `_bin` request header, then the server will also include the     ', ' `_enc` response header containing the binary encoding, an object of possible keys mapped ', ' onto a field id.                                                                         '], 'headers._Standard': {'_id': ['any'], '_unsafe': ['boolean'], '_sel': ['_ext._Select'], '_auth': ['struct._Auth'], '_tim': ['integer'], '_bin': ['array', ['integer']]}, '->': {'_id': ['any'], '_bin': ['array', ['integer']], '_enc': ['object', ['integer']]}}, {'///': ' A type. ', 'union._Type': {'Null': {}, 'Boolean': {}, 'Integer': {}, 'Number': {}, 'String': {}, 'Array': {}, 'Object': {}, 'Any': {}, 'Unknown': {}}}, {'///': ' A reason for the validation failure in the body. ', 'union._ValidationFailureReason': {'TypeUnexpected': {'expected': ['union._Type'], 'actual': ['union._Type']}, 'NullDisallowed': {}, 'ObjectKeyDisallowed': {}, 'NumberOutOfRange': {}, 'ObjectSizeUnexpected': {'expected': ['integer'], 'actual': ['integer']}, 'ExtensionValidationFailed': {'reason': ['string'], 'data!': ['object', ['any']]}, 'ObjectKeyRegexMatchCountUnexpected': {'regex': ['string'], 'expected': ['integer'], 'actual': ['integer']}, 'RequiredObjectKeyMissing': {}, 'FunctionUnknown': {}}}, {'///': ' A parse failure. ', 'union._ParseFailure': {'IncompatibleBinaryEncoding': {}, 'BinaryDecodeFailure': {}, 'JsonInvalid': {}, 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}, 'ExpectedJsonArrayOfTwoObjects': {}}}, {'///': ' A validation failure located at a `path` explained by a `reason`. ', 'struct._ValidationFailure': {'path': ['array', ['any']], 'reason': ['union._ValidationFailureReason']}}, {'///': [' All functions may return a validation error:                                                             ', ' - `_ErrorInvalidRequestHeaders`: The Headers on the Request is invalid as outlined by a list of `cases`. ', ' - `_ErrorInvalidRequestBody`: The Body on the Request is invalid as outlined by a list of `cases`.       ', ' - `_ErrorInvalidResponseBody`: The Body that the Server attempted to put on the Response is invalid as   ', '     outlined by a list of `cases.                                                                        ', ' - `_ErrorParseFailure`: The Request could not be parsed as a uAPI Message.                               '], 'error._Validated': {'->': {'_ErrorUnknown': {}, '_ErrorInvalidRequestHeaders': {'cases': ['array', ['struct._ValidationFailure']]}, '_ErrorInvalidRequestBody': {'cases': ['array', ['struct._ValidationFailure']]}, '_ErrorInvalidResponseBody': {'cases': ['array', ['struct._ValidationFailure']]}, '_ErrorParseFailure': {'reasons': ['array', ['union._ParseFailure']]}}}}, {'///': [' When the `struct._Auth` struct is defined, all functions may return one of the following errors:         ', ' 1. `_ErrorUnauthenticated` indicating that the credentials in the `_auth` header were missing or invalid ', ' 2. `_ErrorUnauthorized` indicating that the credentials in the `_auth` header were insufficient to run the function    '], 'error._Authenticated': {'->': {'_ErrorUnauthenticated': {'message!': ['string']}, '_ErrorUnauthorized': {'message!': ['string']}}}}]}}]],
    ],
    'serverHooks': [
        [[{'Ok': {}, '_onRequestError': True}, {'fn.test': {}}], [{}, {'Ok': {}}]],
        [[{'Ok': {}, '_onResponseError': True}, {'fn.test': {}}], [{'_onResponseError': True}, {'Ok': {}}]],
        [[{'Ok': {}, '_throwError': True}, {'fn.test': {}}], [{}, {'_ErrorUnknown': {}}]],
    ],
    'clientHeaders': [
        [[{'_tim': 6000}, {'fn._ping': {}}], [{}, {'Ok': {}}]],
    ],
    'big': [
        [[{'Ok': {'items': [{'aF': True, 'bF': False, 'cF': True, 'dF': False}, {'aF': True, 'dF': False, 'cF': False, 'bF': True}, {'cF': False, 'bF': True, 'aF': True, 'dF': False}]}}, {'fn.getBigList': {}}], [{}, {'Ok': {'items': [{'aF': True, 'bF': False, 'cF': True, 'dF': False}, {'aF': True, 'dF': False, 'cF': False, 'bF': True}, {'cF': False, 'bF': True, 'aF': True, 'dF': False}]}}]]
    ],
    'customHeaders': [
        [[{'Ok': {}, 'in': False, 'responseHeader': {'out': False}}, {'fn.test': {}}], [{'out': False}, {'Ok': {}}]],
        [[{'Ok': {}, 'in': 0}, {'fn.test': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['in'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok': {}, 'in': ''}, {'fn.test': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['in'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok': {}, 'in': []}, {'fn.test': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['in'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok': {}, 'in': {}}, {'fn.test': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['in'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok': {}, 'responseHeader': {'out': 0}}, {'fn.test': {}}], [{}, {'_ErrorInvalidResponseHeaders': {'cases': [{'path': ['out'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok': {}, 'responseHeader': {'out': ''}}, {'fn.test': {}}], [{}, {'_ErrorInvalidResponseHeaders': {'cases': [{'path': ['out'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok': {}, 'responseHeader': {'out': []}}, {'fn.test': {}}], [{}, {'_ErrorInvalidResponseHeaders': {'cases': [{'path': ['out'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Boolean': {}}}}}]}}]],
        [[{'Ok': {}, 'responseHeader': {'out': {}}}, {'fn.test': {}}], [{}, {'_ErrorInvalidResponseHeaders': {'cases': [{'path': ['out'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Boolean': {}}}}}]}}]],
    ]
}
