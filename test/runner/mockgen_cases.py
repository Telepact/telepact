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

cases = {
    'simple': [
        [[{}, {'fn.setRandomSeed_': {'seed': 4}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.clearStubs_': {}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.clearCalls_': {}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.test': {}}], [{}, {'ErrorNoMatchingStub_': {}}]],
        [[{}, {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {}}}}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'->': {'Ok_': {}}, 'fn.example': {}}}}, 'data': {'field1': 'DMCYpA', 'field2': 424973015}, 'genericData': {'Two': {'field2A': 'SGRdEw', 'field2B': True}}, 'select': {'->': {'Ok_': ['createStub', 'data']}}, 'verify': {'fn.verify_': {'call': {'fn.example': {'arg1': 'DJ36uA'}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.example': {'arg1': 'eLDvBg'}, '->': {'Ok_': {'result': []}}}}}, 'data': {'field1': True, 'field2': 652711277}, 'genericData': {'Two': {'field2A': 'JqfiUw', 'field2B': False}}, 'select': {'struct.Data': ['field1', 'field2'], 'union.GenericData': {'One': [], 'Two': ['field2A']}}, 'verify': {'fn.verify_': {'call': {'fn.example': {'arg1': 'HbKyNw'}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {'data': {'field1': 'c/rZOQ'}, 'select': {'->': {'Ok_': ['data', 'genericData', 'verify']}, 'struct.Data': ['field1', 'field2']}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}}}}, 'data': {'field1': 1154191355, 'field2': 738514090}, 'genericData': {'One': {'field1A': 'fXoE6Q', 'field1B': 1273685929}}, 'select': {'struct.Data': ['field2']}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}]],
    ],
}
