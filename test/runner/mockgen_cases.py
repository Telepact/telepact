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
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.example': {}, '->': {'Ok_': {}}}}}, 'data': {'field1': 'DMCYpA', 'field2': 424973015}, 'genericData': {'Two': {'field2A': 'SGRdEw', 'field2B': True}}, 'select': {'->': {'Ok_': ['createStub', 'data']}}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {'data': {'field2': 2024861446}, 'genericData': {'Two': {}}, 'select': {}}}}}}, 'data': {'field1': True, 'field2': 103563748}, 'genericData': {'One': {'field1A': 714464785, 'field1B': 1681104842}}, 'select': {'->': {'Ok_': []}, 'union.GenericData': {'Two': []}}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {'genericData': {'One': {'field1B': 1651953946}}}}}}}, 'data': {'field1': 1402702433, 'field2': 1741099824}, 'genericData': {'One': {'field1A': 'SE/cEA', 'field1B': 503818891}}, 'select': {}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}]],
    ],
}
