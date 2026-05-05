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

from parameters.schema_loader import normalize_schema_docstrings
from parameters.schema_loader import load_schema_definitions
from pathlib import Path


def _schema_key(definition: dict[str, object]) -> str:
    return next(
        key
        for key in definition.keys()
        if key not in {'///', '->', '_errors', 'example', 'inputExample', 'outputExample'}
    )


def _load_sorted_schema(*relative_paths: str) -> list[dict[str, object]]:
    root = Path(__file__).resolve().parents[3]
    definitions: list[dict[str, object]] = []
    for relative_path in relative_paths:
        definitions.extend(load_schema_definitions(root / relative_path))

    return sorted(
        definitions,
        key=lambda definition: (not _schema_key(definition).startswith('info.'), _schema_key(definition)),
    )


def _canonicalize_examples(*relative_paths: str, api: list[dict[str, object]]) -> list[dict[str, object]]:
    canonical_api = _load_sorted_schema(*relative_paths)
    examples_by_key = {
        _schema_key(definition): {
            key: value
            for key, value in definition.items()
            if key in {'example', 'inputExample', 'outputExample'}
        }
        for definition in api
    }

    return [
        {
            **definition,
            **examples_by_key.get(_schema_key(definition), {}),
        }
        for definition in canonical_api
    ]


auth_cases = {
    'api_examples_auth': [
        [
            [{}, {'fn.api_': {'includeExamples!': True}}],
            [{}, {'Ok_': {'api': [
                {'info.AuthExample': {}, 'example': {}},
                {'///': ' A standard error. ', 'errors.Auth_': [{'///': ' The credentials in the `_auth` header were missing or invalid. ', 'ErrorUnauthenticated_': {'message!': 'string'}}, {'///': ' The credentials in the `_auth` header were insufficient to run the function. ', 'ErrorUnauthorized_': {'message!': 'string'}}], 'example': {'ErrorUnauthorized_': {'message!': 'sigma'}}},
                {'fn.test': {}, '->': [{'Ok_': {}}], 'inputExample': {'fn.test': {}}, 'outputExample': {'Ok_': {}}},
                {'///': [' The `+auth_` header is the conventional location for sending credentials to     ', ' the server for the purpose of authentication and authorization.                 '], 'headers.Auth_': {'+auth_': 'union.Auth_'}, '->': {}, 'inputExample': {'+auth_': {'Token': {'token': 'sigma'}}}, 'outputExample': {}},
                {'union.Auth_': [{'Token': {'token': 'string'}}], 'example': {'Token': {'token': 'sigma'}}}
            ]}}]
        ],
    ],
}

auth_cases = normalize_schema_docstrings(auth_cases)
auth_cases['api_examples_auth'][0][1][1]['Ok_']['api'] = _canonicalize_examples(
    'test/runner/schema/auth/auth.telepact.json',
    'common/auth.telepact.yaml',
    api=auth_cases['api_examples_auth'][0][1][1]['Ok_']['api'],
)

mock_cases = {'api_examples_mock': [[[{}, {'fn.api_': {'includeInternal!': True, 'includeExamples!': True}}],
                                     [{},
                                      {'Ok_': {'api': [{'info.ApiExamplesMock': {}, 'example': {}},
                                                       {'///': [' See https://raw.githubusercontent.com/Telepact/telepact/main/doc/        ',
                                                                ' extensions.md for `_ext.Call_` documentation.                             '],
                                                        '_ext.Call_': {},
                                                        'example': {'fn.test': {'value': {'bytes!': 'APjHCQ==', 'sel!': {'->': {'Ok_': ['value']}, 'struct.Payload': ['sel!']}}}}},
                                                       {'///': [' See https://raw.githubusercontent.com/Telepact/telepact/main/doc/        ',
                                                                ' extensions.md for `_ext.Select_` documentation.                           '],
                                                        '_ext.Select_': {},
                                                        'example': {}},
                                                       {'///': [' See https://raw.githubusercontent.com/Telepact/telepact/main/doc/        ',
                                                                ' extensions.md for `_ext.Stub_` documentation.                             '],
                                                        '_ext.Stub_': {},
                                                        'example': {'fn.test': {'value': {'bytes!': 'AiHAMQ==', 'sel!': {'->': {'Ok_': ['value']}, 'struct.Payload': ['bytes!']}}}, '->': {'Ok_': {}}}},
                                                       {'errors.Mock_': [{'///': ' The mock could not return a result due to no matching stub being available. ', 'ErrorNoMatchingStub_': {}}],
                                                        'example': {'ErrorNoMatchingStub_': {}}},
                                                       {'///': ' A standard error. ',
                                                        'errors.Validation_': [{'///': ' The server implementation raised an unknown error. ', 'ErrorUnknown_': {}},
                                                                               {'///': ' The headers on the request are invalid. ', 'ErrorInvalidRequestHeaders_': {'cases': ['struct.ValidationFailure_']}},
                                                                               {'///': ' The body on the request is invalid. ', 'ErrorInvalidRequestBody_': {'cases': ['struct.ValidationFailure_']}},
                                                                               {'///': ' The headers on the response are invalid. ', 'ErrorInvalidResponseHeaders_': {'cases': ['struct.ValidationFailure_']}},
                                                                               {'///': ' The body that the server attempted to put on the response is invalid. ',
                                                                                'ErrorInvalidResponseBody_': {'cases': ['struct.ValidationFailure_']}},
                                                                               {'///': ' The request could not be parsed as a telepact Message. ', 'ErrorParseFailure_': {'reasons': ['union.ParseFailure_']}}],
                                                        'example': {'ErrorUnknown_': {'caseId': 'sigma'}}},
                                                       {'///': [' Get the telepact `schema` of this server. Set `includeInternal` to `true` to    ',
                                                                ' include Telepact internal definitions. Set `includeExamples` to `true` to add   ',
                                                                ' deterministic example payloads to each schema entry.                            '],
                                                        'fn.api_': {'includeInternal!': 'boolean', 'includeExamples!': 'boolean'},
                                                        '->': [{'Ok_': {'api': [{'string': 'any'}]}}],
                                                        '_errors': '^errors\\.Validation_$',
                                                        'inputExample': {'fn.api_': {'includeExamples!': False, 'includeInternal!': False}},
                                                        'outputExample': {'Ok_': {'api': [{'sigma': 415302837, 'xi': 'kappa'}, {'sigma': True, 'gamma': 225740852}]}}},
                                                       {'///': ' Clear all call data. ',
                                                        'fn.clearCalls_': {},
                                                        '->': [{'Ok_': {}}],
                                                        '_errors': '^errors\\.Validation_$',
                                                        'inputExample': {'fn.clearCalls_': {}},
                                                        'outputExample': {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}},
                                                                                                             {'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}},
                                                       {'///': ' Clear all stub conditions. ',
                                                        'fn.clearStubs_': {},
                                                        '->': [{'Ok_': {}}],
                                                        '_errors': '^errors\\.Validation_$',
                                                        'inputExample': {'fn.clearStubs_': {}},
                                                        'outputExample': {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}},
                                                                                                             {'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}},
                                                       {'///': [' Create a function stub that will cause the server to return the `stub` result   ',
                                                                ' when the `stub` argument matches the function argument on a request.            ',
                                                                '                                                                                 ',
                                                                ' If `ignoreMissingArgFields` is `true`, then the server will skip field          ',
                                                                ' omission validation on the `stub` argument, and the stub will match calls       ',
                                                                ' where the given `stub` argument is Exactly a json sub-structure of the request  ',
                                                                ' function argument.                                                              ',
                                                                '                                                                                 ',
                                                                ' If `generateMissingResultFields` is `true`, then the server will skip field     ',
                                                                ' omission validation on the `stub` result, and the server will generate the      ',
                                                                ' necessary data required to make the `result` pass on response validation.       '],
                                                        'fn.createStub_': {'stub': '_ext.Stub_', 'strictMatch!': 'boolean', 'count!': 'integer'},
                                                        '->': [{'Ok_': {}}],
                                                        '_errors': '^errors\\.Validation_$',
                                                        'inputExample': {'fn.createStub_': {'count!': 3178529, 'strictMatch!': False, 'stub': {'fn.test': {}, '->': {'Ok_': {}}}}},
                                                        'outputExample': {'ErrorUnknown_': {'caseId': 'xi'}}},
                                                       {'///': ' Ping the server. ',
                                                        'fn.ping_': {},
                                                        '->': [{'Ok_': {}}],
                                                        '_errors': '^errors\\.Validation_$',
                                                        'inputExample': {'fn.ping_': {}},
                                                        'outputExample': {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}},
                                                                                                             {'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}},
                                                       {'///': ' Set the seed of the random generator. ',
                                                        'fn.setRandomSeed_': {'seed': 'integer'},
                                                        '->': [{'Ok_': {}}],
                                                        '_errors': '^errors\\.Validation_$',
                                                        'inputExample': {'fn.setRandomSeed_': {'seed': 3178529}},
                                                        'outputExample': {'ErrorInvalidResponseHeaders_': {'cases': [{'path': [True, 415302837], 'reason': {'NumberOutOfRange': {}}},
                                                                                                                     {'path': ['kappa', 'tau'], 'reason': {'NumberOutOfRange': {}}}]}}},
                                                       {'fn.test': {'value': 'struct.Payload'},
                                                        '->': [{'Ok_': {'value': 'struct.Payload'}}],
                                                        'inputExample': {'fn.test': {'value': {'bytes!': 'ADCAIQ==', 'sel!': {'struct.Payload': ['bytes!', 'sel!']}}}},
                                                        'outputExample': {'ErrorParseFailure_': {'reasons': [{'BinaryDecodeFailure': {}}, {'IncompatibleBinaryEncoding': {}}]}}},
                                                       {'///': [' Verify that no interactions have occurred with this mock or that all            ',
                                                                ' interactions have been verified.                                                '],
                                                        'fn.verifyNoMoreInteractions_': {},
                                                        '->': [{'Ok_': {}}, {'ErrorVerificationFailure': {'additionalUnverifiedCalls': ['_ext.Call_']}}],
                                                        '_errors': '^errors\\.Validation_$',
                                                        'inputExample': {'fn.verifyNoMoreInteractions_': {}},
                                                        'outputExample': {'ErrorInvalidRequestHeaders_': {'cases': [{'path': [True, 'lambda'], 'reason': {'NumberOutOfRange': {}}},
                                                                                                                    {'path': [589180268, True],
                                                                                                                     'reason': {'TypeUnexpected': {'actual': {'Bytes': {}}, 'expected': {'Array': {}}}}}]}}},
                                                       {'///': [' Verify a call was made with this mock that matches the given `call` and         ',
                                                                ' `multiplicity` criteria. If `allowPartialArgMatch` is supplied as `true`, then  ',
                                                                ' the server will skip field omission validation, and match calls where the       ',
                                                                ' given `call` argument is Exactly a json sub-structure of the actual argument.   '],
                                                        'fn.verify_': {'call': '_ext.Call_', 'strictMatch!': 'boolean', 'count!': 'union.CallCountCriteria_'},
                                                        '->': [{'Ok_': {}}, {'ErrorVerificationFailure': {'reason': 'union.VerificationFailure_'}}],
                                                        '_errors': '^errors\\.Validation_$',
                                                        'inputExample': {'fn.verify_': {'call': {'fn.test': {}}, 'count!': {'Exact': {'times': 1598503090}}, 'strictMatch!': True}},
                                                        'outputExample': {'ErrorUnknown_': {'caseId': 'phi'}}},
                                                       {'///': [' The `+bin_` header indicates the valid checksums of binary encodings            ',
                                                                ' negotiated between the client and server. If the client sends a `+bin_` header  ',
                                                                ' with any value, the server will respond with a `+bin_` header with an array     ',
                                                                " containing the currently supported binary encoding checksum. If te client's     ",
                                                                " provided checksum does not match the server's checksum, the server will also    ",
                                                                ' send an `+enc_` header containing the binary encoding, which is a map of field  ',
                                                                ' names to field ids. The response body may also be encoded in binary.            ',
                                                                '                                                                                 ',
                                                                " The `+pac_` header can also be used to indicate usage of 'packed' binary        ",
                                                                ' encoding strategy. If the client submits a `+pac_` header with a `true` value,  ',
                                                                ' the server will respond with a `+pac_` header with a `true` value.              '],
                                                        'headers.Binary_': {'+bin_': ['integer'], '+pac_': 'boolean'},
                                                        '->': {'+bin_': ['integer'], '+enc_': {'string': 'integer'}, '+pac_': 'boolean'},
                                                        'inputExample': {'+bin_': [2163713, 3178529], '+pac_': False},
                                                        'outputExample': {'+bin_': [16303881, 954081041], '+enc_': {'lambda': 415302837, 'xi': 589180268}, '+pac_': True}},
                                                       {'///': [' The `+id_` header is used to correlate requests and responses. The server will  ',
                                                                ' reflect the client-provided `+id_` header as-is.                                '],
                                                        'headers.Id_': {'+id_': 'any'},
                                                        '->': {'+id_': 'any'},
                                                        'inputExample': {'+id_': 'sigma'},
                                                        'outputExample': {'+id_': True}},
                                                       {'///': ' The `+select_` header is used to select fields from structs. ',
                                                        'headers.Select_': {'+select_': '_ext.Select_'},
                                                        '->': {},
                                                        'inputExample': {'+select_': {}},
                                                        'outputExample': {}},
                                                       {'///': ' The `+time_` header indicates the request timeout honored by the client. ',
                                                        'headers.Time_': {'+time_': 'integer'},
                                                        '->': {},
                                                        'inputExample': {'+time_': 2163713},
                                                        'outputExample': {}},
                                                       {'///': [' If `+unsafe_` is set to `true`, response validation by the server will be       ',
                                                                ' disabled. The server will the client-provided the value of `+unsafe_` header    ',
                                                                ' in the response.                                                                '],
                                                        'headers.Unsafe_': {'+unsafe_': 'boolean'},
                                                        '->': {'+unsafe_': 'boolean'},
                                                        'inputExample': {'+unsafe_': False},
                                                        'outputExample': {'+unsafe_': False}},
                                                       {'///': ' The `+warn_` header is used to send warnings to the client. ',
                                                        'headers.Warning_': {},
                                                        '->': {'+warn_': ['any']},
                                                        'inputExample': {},
                                                        'outputExample': {'+warn_': ['sigma', True]}},
                                                       {'struct.Payload': {'bytes!': 'bytes', 'sel!': '_ext.Select_'}, 'example': {'bytes!': 'ACEEAQ==', 'sel!': {}}},
                                                       {'///': ' A validation failure located at a `path` explained by a `reason`. ',
                                                        'struct.ValidationFailure_': {'path': ['any'], 'reason': 'union.ValidationFailureReason_'},
                                                        'example': {'path': ['sigma', True], 'reason': {'ExtensionValidationFailed': {'data!': {'lambda': True, 'phi': True}, 'reason': 'tau'}}}},
                                                       {'///': ' The number of times a function is allowed to be called. ',
                                                        'union.CallCountCriteria_': [{'Exact': {'times': 'integer'}}, {'AtMost': {'times': 'integer'}}, {'AtLeast': {'times': 'integer'}}],
                                                        'example': {'Exact': {'times': 3178529}}},
                                                       {'///': ' A parse failure. ',
                                                        'union.ParseFailure_': [{'IncompatibleBinaryEncoding': {}},
                                                                                {'///': ' The binary decoder encountered a field id that could not be mapped to a key. ', 'BinaryDecodeFailure': {}},
                                                                                {'JsonInvalid': {}},
                                                                                {'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}},
                                                                                {'ExpectedJsonArrayOfTwoObjects': {}}],
                                                        'example': {'IncompatibleBinaryEncoding': {}}},
                                                       {'///': ' A type. ',
                                                        'union.Type_': [{'Null': {}},
                                                                        {'Boolean': {}},
                                                                        {'Integer': {}},
                                                                        {'Number': {}},
                                                                        {'String': {}},
                                                                        {'Array': {}},
                                                                        {'Object': {}},
                                                                        {'Any': {}},
                                                                        {'Base64String': {}},
                                                                        {'Bytes': {}},
                                                                        {'Unknown': {}}],
                                                        'example': {'Base64String': {}}},
                                                       {'///': ' A reason for the validation failure in the body. ',
                                                        'union.ValidationFailureReason_': [{'TypeUnexpected': {'expected': 'union.Type_', 'actual': 'union.Type_'}},
                                                                                           {'NullDisallowed': {}},
                                                                                           {'ObjectKeyDisallowed': {}},
                                                                                           {'RequiredObjectKeyPrefixMissing': {'prefix': 'string'}},
                                                                                           {'ArrayElementDisallowed': {}},
                                                                                           {'NumberOutOfRange': {}},
                                                                                           {'ObjectSizeUnexpected': {'expected': 'integer', 'actual': 'integer'}},
                                                                                           {'ExtensionValidationFailed': {'reason': 'string', 'data!': {'string': 'any'}}},
                                                                                           {'ObjectKeyRegexMatchCountUnexpected': {'regex': 'string',
                                                                                                                                   'expected': 'integer',
                                                                                                                                   'actual': 'integer',
                                                                                                                                   'keys': ['string']}},
                                                                                           {'RequiredObjectKeyMissing': {'key': 'string'}},
                                                                                           {'FunctionUnknown': {}}],
                                                        'example': {'FunctionUnknown': {}}},
                                                       {'///': ' Possible causes for a mock verification to fail. ',
                                                        'union.VerificationFailure_': [{'TooFewMatchingCalls': {'wanted': 'union.CallCountCriteria_', 'found': 'integer', 'allCalls': ['_ext.Call_']}},
                                                                                       {'TooManyMatchingCalls': {'wanted': 'union.CallCountCriteria_', 'found': 'integer', 'allCalls': ['_ext.Call_']}}],
                                                        'example': {'TooManyMatchingCalls': {'allCalls': [{'fn.test': {}}, {'fn.test': {}}], 'found': 326552725, 'wanted': {'Exact': {'times': 1074759177}}}}}]}}]]]}

mock_cases = normalize_schema_docstrings(mock_cases)
mock_cases['api_examples_mock'][0][1][1]['Ok_']['api'] = _canonicalize_examples(
    'test/runner/schema/api_examples_mock/api_examples_mock.telepact.json',
    'common/internal.telepact.yaml',
    'common/mock-internal.telepact.yaml',
    api=mock_cases['api_examples_mock'][0][1][1]['Ok_']['api'],
)
