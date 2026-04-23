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
            [{}, {'fn.example_': {'schemaKey': 'fn.test'}}],
            [{}, {'Ok_': {'inputExample!': {'fn.test': {}}, 'outputExample!': {'Ok_': {}}}}],
        ],
        [
            [{}, {'fn.example_': {'schemaKey': 'headers.Auth_'}}],
            [{}, {'Ok_': {'inputExample!': {'@auth_': {'Token': {'token': 'sigma'}}}, 'outputExample!': {}}}],
        ],
        [
            [{}, {'fn.example_': {'schemaKey': 'errors.Auth_'}}],
            [{}, {'Ok_': {'example!': {'ErrorUnauthorized_': {'message!': 'sigma'}}}}],
        ],
    ],
}


mock_cases = {
    'api_examples_mock': [
        [
            [{}, {'fn.example_': {'schemaKey': 'fn.createStub_', 'includeInternal!': True}}],
            [{}, {'Ok_': {
                'inputExample!': {'fn.createStub_': {'count!': 3178529, 'strictMatch!': False, 'stub': {'fn.test': {}, '->': {'Ok_': {}}}}},
                'outputExample!': {'ErrorUnknown_': {'caseId': 'xi'}},
            }}],
        ],
        [
            [{}, {'fn.example_': {'schemaKey': '_ext.Stub_', 'includeInternal!': True}}],
            [{}, {'Ok_': {'example!': {'fn.test': {'value': {'bytes!': 'AiHAMQ==', 'sel!': {'->': {'Ok_': ['value']}, 'struct.Payload': ['bytes!']}}}, '->': {'Ok_': {}}}}}],
        ],
    ],
}
