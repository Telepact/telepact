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

auth_cases = {
    'api_examples_auth': [
        [
            [{}, {'fn.example_': {'name': 'fn.test'}}],
            [{}, {'Ok_': {'inputExample': {'fn.test': {}}, 'outputExample': {'Ok_': {}}}}],
        ],
        [
            [{}, {'fn.example_': {'name': 'headers.Auth_'}}],
            [{}, {'Ok_': {'inputExample': {'@auth_': {'Token': {'token': 'sigma'}}}, 'outputExample': {}}}],
        ],
        [
            [{}, {'fn.example_': {'name': 'union.Auth_'}}],
            [{}, {'Ok_': {'example': {'Token': {'token': 'sigma'}}}}],
        ],
        [
            [{}, {'fn.example_': {'name': 'fn.ping_'}}],
            [{}, {'Ok_': {}}],
        ],
        [
            [{}, {'fn.example_': {'name': 'fn.ping_', 'includeInternal!': True}}],
            [{}, {'Ok_': {'inputExample': {'fn.ping_': {}}, 'outputExample': {'ErrorParseFailure_': {'reasons': [
                {'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}},
                {'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}},
            ]}}}}],
        ],
    ],
}


mock_cases = {
    'api_examples_mock': [
        [
            [{}, {'fn.example_': {'name': 'fn.test'}}],
            [{}, {'Ok_': {'inputExample': {'fn.test': {'value': {'bytes!': 'ADCAIQ==', 'sel!': {'struct.Payload': ['bytes!', 'sel!']}}}}, 'outputExample': {'ErrorParseFailure_': {'reasons': [{'BinaryDecodeFailure': {}}, {'IncompatibleBinaryEncoding': {}}]}}}}],
        ],
        [
            [{}, {'fn.example_': {'name': '_ext.Call_'}}],
            [{}, {'Ok_': {}}],
        ],
        [
            [{}, {'fn.example_': {'name': '_ext.Call_', 'includeInternal!': True}}],
            [{}, {'Ok_': {'example': {'fn.test': {'value': {'bytes!': 'APjHCQ==', 'sel!': {'->': {'Ok_': ['value']}, 'struct.Payload': ['sel!']}}}}}}],
        ],
        [
            [{}, {'fn.example_': {'name': 'errors.Mock_', 'includeInternal!': True}}],
            [{}, {'Ok_': {'example': {'ErrorNoMatchingStub_': {}}}}],
        ],
        [
            [{}, {'fn.example_': {'name': 'fn.createStub_', 'includeInternal!': True}}],
            [{}, {'Ok_': {'inputExample': {'fn.createStub_': {'count!': 3178529, 'strictMatch!': False, 'stub': {'fn.test': {}, '->': {'Ok_': {}}}}}, 'outputExample': {'ErrorUnknown_': {'caseId': 'xi'}}}}],
        ],
        [
            [{}, {'fn.example_': {'name': 'headers.Binary_', 'includeInternal!': True}}],
            [{}, {'Ok_': {'inputExample': {'@bin_': [2163713, 3178529], '@pac_': False}, 'outputExample': {'@bin_': [16303881, 954081041], '@enc_': {'lambda': 415302837, 'xi': 589180268}, '@pac_': True}}}],
        ],
    ],
}
