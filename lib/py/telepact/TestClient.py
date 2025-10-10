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

from typing import TYPE_CHECKING, Optional, cast
import json

if TYPE_CHECKING:
    from .Client import Client
    from .Message import Message
    from .TelepactSchema import TelepactSchema
    from .internal.types.TUnion import TUnion

class TestClient:
    class Options:
        generated_collection_length_min: int = 0
        generated_collection_length_max: int = 3

    def __init__(self, client: 'Client', options: Options):
        from .RandomGenerator import RandomGenerator

        self.client = client
        self.random = RandomGenerator(options.generated_collection_length_min, options.generated_collection_length_max)
        self.schema: Optional['TelepactSchema'] = None

    async def assert_request(self, request_message: 'Message', expected_pseudo_json_body: dict[str, object], expect_match: bool) -> 'Message':
        from .internal.mock.IsSubMap import is_sub_map
        from .Message import Message
        from .TelepactSchema import TelepactSchema
        from .internal.generation.GenerateContext import GenerateContext
        from .internal.types.TUnion import TUnion

        if self.schema is None:
            response = await self.client.request(Message({}, {"fn.api_": {}}))
            ok = cast(dict, response.body["Ok_"])
            api = ok["api"]
            json_str = json.dumps(api)
            self.schema = TelepactSchema.from_json(json_str)

        response_message = await self.client.request(request_message)

        did_match = is_sub_map(expected_pseudo_json_body, response_message.body)

        if expect_match:
            if not did_match:
                raise AssertionError(f"Expected response body was not a sub map. Expected: {expected_pseudo_json_body} Actual: {response_message.body}")
            else:
                return response_message
        else:
            if did_match:
                raise AssertionError(f"Expected response body was a sub map. Expected: {expected_pseudo_json_body} Actual: {response_message.body}")
            else:
                use_blueprint_value = True
                include_optional_fields = False
                always_include_required_fields = True
                randomize_optional_field_generation = False

                function_name = request_message.get_body_target()
                definition = cast(TUnion, self.schema.parsed[f"{function_name}.->"])

                generated_result = definition.generate_random_value(
                    expected_pseudo_json_body, use_blueprint_value, [],
                    GenerateContext(
                        include_optional_fields, randomize_optional_field_generation,
                        always_include_required_fields, function_name,
                        self.random))

                return Message(response_message.headers, cast(dict, generated_result))

    def set_seed(self, seed: int):
        self.random.set_seed(seed)