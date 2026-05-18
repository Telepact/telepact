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

_BINARY_ENCODING = {
    'Ok_': 0,
    'active': 1,
    'api': 2,
    'code': 3,
    'data': 4,
    'flags': 5,
    'fn.api_': 6,
    'fn.example': 7,
    'fn.ping_': 8,
    'id': 9,
    'includeExamples!': 10,
    'includeInternal!': 11,
    'label': 12,
    'meta': 13,
    'name': 14,
}
_BINARY_CHECKSUM = -1780699065
_PACKED_SITES = [[['Ok_', 'data'], [None, 9, 14, [13, 3, [5, 1, 12]]]]]

cases = {
    'binary': [
        [[{'@bin_': []}, {'fn.ping_': {}}], [{'@assert_': {'skipPackedSiteCheck': True}, '@enc_': _BINARY_ENCODING, '@bin_': [_BINARY_CHECKSUM]}, {0: {}}]],
        [[{'@msgpack': True, '@bin_': [0]}, {0: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM]}, {8: {}}], [{'@bin_': [_BINARY_CHECKSUM]}, {0: {}}]],
        [[{'@msgpack': True, '@bin_': [_BINARY_CHECKSUM], '@ok_': {'data': [{'id': 1, 'name': 'one', 'meta': {'code': 7, 'flags': {'active': True, 'label': 'alpha'}}}, {'id': 2, 'name': 'two', 'meta': {'code': 8, 'flags': {'active': False, 'label': 'beta'}}}]}}, {7: {}}], [{'@bin_': [_BINARY_CHECKSUM]}, {0: {4: [{9: 1, 14: 'one', 13: {3: 7, 5: {1: True, 12: 'alpha'}}}, {9: 2, 14: 'two', 13: {3: 8, 5: {1: False, 12: 'beta'}}}]}}]],
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
