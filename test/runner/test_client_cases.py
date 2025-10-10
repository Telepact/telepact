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
        [[{'@setSeed': 0, '@expectedPseudoJsonBody': {'Ok_': {}}}, {'fn.ping_': {}}], [{}, {'Ok_': {}}]],
        [[{'@expectMatch': False,'@expectedPseudoJsonBody': {'Ok_': {}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{'@assertionError': True}, {'ErrorUnknown_': {}}]],
        [[{'@expectedPseudoJsonBody': {'Ok_': {}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
        [[{'@expectedPseudoJsonBody': {'Ok_': {'value!': {}}}, '@result': {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],
        [[{'@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {}}}}, '@result': {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],
        [[{'@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],

        # The required field is missing and will be filled in with a random value, since a match is not expected.
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': False, 'optional!': True}}}}]],
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': False, 'optional!': True}}}}]],
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': False, 'optional!': True}}}}]],
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],

        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{'@assertionError': True}, {'ErrorUnknown_': {}}]],
    ],
}
