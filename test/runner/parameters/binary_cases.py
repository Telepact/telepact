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
    'data': 2,
    'example!': 3,
    'fn.api_': 4,
    'fn.def_': 5,
    'fn.example': 6,
    'fn.example_': 7,
    'fn.index_': 8,
    'fn.ping_': 9,
    'id': 10,
    'includeInternal!': 11,
    'inputExample!': 12,
    'name': 13,
    'outputExample!': 14,
    'schemaKey': 15,
}
_BINARY_CHECKSUM = -1288961102

cases = {
    'binary': [
        [[{'@bin_': []}, {'fn.ping_': {}}], [{'@enc_': _BINARY_ENCODING, '@bin_': [_BINARY_CHECKSUM]}, {0: {}}]],
        [[{'@msgpack': True, '@bin_': [0]}, {0: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM]}, {5: {}}], [{'@bin_': [_BINARY_CHECKSUM]}, {0: {}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM], '@pac_': True, '@ok_': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {6: {}}], [{'@bin_': [_BINARY_CHECKSUM], '@pac_': True}, {0: {2: [ExtType(17, b''), [None, 10, 13], [1, 'one'], [2, 'two']]}}]],
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
