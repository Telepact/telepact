#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

cases = {
    'simple': [
        [[{'@setSeed': 0, '@expectedPseudoJsonBody': {'Ok_': {}}}, {'fn.ping_': {}}], [{}, {'Ok_': {}}]],
        [[{'@expectMatch': False,'@expectedPseudoJsonBody': {'Ok_': {}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{'@assertionError': True}, {'ErrorUnknown_': {}}]],
        [[{'@expectMatch': True, '@expectedPseudoJsonBody': {'Ok_': {}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
        [[{'@expectMatch': True, '@expectedPseudoJsonBody': {'Ok_': {'value!': {}}}, '@result': {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],
        [[{'@expectMatch': True, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {}}}}, '@result': {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],
        [[{'@expectMatch': True, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],

        # The required field is missing and will be filled in with a random value, since a match is not expected.
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': False, 'optional!': True}}}}]],
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': False, 'optional!': True}}}}]],
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': False, 'optional!': True}}}}]],
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],
        [[{'@expectMatch': False, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {}}}, {'fn.test': {}}], [{}, {'Ok_': {'value!': {'struct!': {'required': True, 'optional!': True}}}}]],

        [[{'@expectMatch': True, '@expectedPseudoJsonBody': {'Ok_': {'value!': {'struct!': {'optional!': True}}}}, '@result': {'Ok_': {'value!': {'struct!': {'required': True}}}}}, {'fn.test': {}}], [{'@assertionError': True}, {'ErrorUnknown_': {}}]],
    ],
}
