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

from msgpack import ExtType

_BINARY_ENCODING = {
    'Ok_': 0,
    'api': 1,
    'contact': 2,
    'data': 3,
    'deepData': 4,
    'email': 5,
    'fn.api_': 6,
    'fn.example': 7,
    'fn.exampleNested': 8,
    'fn.exampleNestedList': 9,
    'fn.ping_': 10,
    'id': 11,
    'includeExamples!': 12,
    'includeInternal!': 13,
    'messages': 14,
    'name': 15,
    'nestedData': 16,
    'num': 17,
    'phone': 18,
    'text': 19,
}
_BINARY_CHECKSUM = 1689129573

_OK_ID = _BINARY_ENCODING['Ok_']
_DATA_ID = _BINARY_ENCODING['data']
_DEEP_DATA_ID = _BINARY_ENCODING['deepData']
_FN_EXAMPLE_ID = _BINARY_ENCODING['fn.example']
_FN_EXAMPLE_NESTED_ID = _BINARY_ENCODING['fn.exampleNested']
_FN_EXAMPLE_NESTED_LIST_ID = _BINARY_ENCODING['fn.exampleNestedList']
_FN_PING_ID = _BINARY_ENCODING['fn.ping_']
_ID_ID = _BINARY_ENCODING['id']
_NESTED_DATA_ID = _BINARY_ENCODING['nestedData']
_NUM_ID = _BINARY_ENCODING['num']
_TEXT_ID = _BINARY_ENCODING['text']

_PACK_SITE_TREE = {
    'fn.example': {'->': {'Ok_': {'data': [None, 'id', 'name']}}},
    'fn.exampleNested': {'->': {'Ok_': {'nestedData': [None, 'id', 'name', ['contact', 'email', 'phone']]}}},
    'fn.exampleNestedList': {'->': {'Ok_': {'deepData': [None, 'id', 'name', 'messages']}}},
}

cases = {
    'binary': [
        [[{'@bin_': []}, {'fn.ping_': {}}], [{'@enc_': _BINARY_ENCODING, '@encp_': _PACK_SITE_TREE, '@bin_': [_BINARY_CHECKSUM], '@fn_': 'fn.ping_'}, {_OK_ID: {}}]],
        [[{'@msgpack': True, '@bin_': [0]}, {0: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM]}, {_FN_PING_ID: {}}], [{'@bin_': [_BINARY_CHECKSUM], '@fn_': 'fn.ping_'}, {_OK_ID: {}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM], '@pac_': True, '@ok_': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {_FN_EXAMPLE_ID: {}}], [{'@bin_': [_BINARY_CHECKSUM], '@pac_': True, '@fn_': 'fn.example'}, {_OK_ID: {_DATA_ID: [ExtType(17, b''), [1, 'one'], [2, 'two']]}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM], '@pac_': True, '@ok_': {'nestedData': [{'id': 1, 'name': 'one', 'contact': {'email': 'one@example.com', 'phone': '111-1111'}}, {'id': 2, 'name': 'two', 'contact': {'email': 'two@example.com', 'phone': '222-2222'}}]}}, {_FN_EXAMPLE_NESTED_ID: {}}], [{'@bin_': [_BINARY_CHECKSUM], '@pac_': True, '@fn_': 'fn.exampleNested'}, {_OK_ID: {_NESTED_DATA_ID: [ExtType(17, b''), [1, 'one', ['one@example.com', '111-1111']], [2, 'two', ['two@example.com', '222-2222']]]}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM], '@pac_': True, '@ok_': {'deepData': [{'id': 1, 'name': 'one', 'messages': [{'num': 11, 'text': 'hello'}, {'num': 12, 'text': 'world'}]}, {'id': 2, 'name': 'two', 'messages': [{'num': 21, 'text': 'apple'}, {'num': 22, 'text': 'banana'}]}]}}, {_FN_EXAMPLE_NESTED_LIST_ID: {}}], [{'@bin_': [_BINARY_CHECKSUM], '@pac_': True, '@fn_': 'fn.exampleNestedList'}, {_OK_ID: {_DEEP_DATA_ID: [ExtType(17, b''), [1, 'one', [{_NUM_ID: 11, _TEXT_ID: 'hello'}, {_NUM_ID: 12, _TEXT_ID: 'world'}]], [2, 'two', [{_NUM_ID: 21, _TEXT_ID: 'apple'}, {_NUM_ID: 22, _TEXT_ID: 'banana'}]]]}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM]}, {255: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
        [[{'@bin_': None}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@bin_': False}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@bin_': 0}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@bin_': ''}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@bin_': {}}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'@bin_': [None]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'@bin_': [False]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'@bin_': [0.1]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'@bin_': ['']}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'@bin_': [[]]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'@bin_': [{}]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['@bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}}]}}]],
    ]
}

binary_client_rotation_cases = {
    'rotation': [
        [[{'@ok_': {}, '@toggleAlternateServer_': True}, {'fn.test': {}}], [{'@assert_': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'@ok_': {}, '@toggleAlternateServer_': True}, {'fn.test': {}}], [{'@assert_': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'@ok_': {}, '@toggleAlternateServer_': True}, {'fn.test': {}}], [{'@assert_': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'@ok_': {}, '@toggleAlternateServer_': True}, {'fn.test': {}}], [{'@assert_': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'@ok_': {}}, {'fn.test': {}}], [{'@assert_': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'@ok_': {}}, {'fn.test': {}}], [{'@assert_': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'@ok_': {}}, {'fn.test': {}}], [{'@assert_': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'@ok_': {}}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
    ]
}
