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

cases = {
    'garbage': [
        [b'false', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'0', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'""', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'[]', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'{}', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {}, {}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {'Ok_': 'wrong'}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[False, {'fn.ping_': {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[0, {'fn.ping_': {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [['', {'fn.ping_': {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[[], {'fn.ping_': {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, False], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, 0], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, ''], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, []], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]]
    ]
}
