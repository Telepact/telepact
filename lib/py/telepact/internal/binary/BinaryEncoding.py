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

from typing import cast

class BinaryEncoding:
    def __init__(self, binary_encoding_map: dict[str, int], checksum: int,
                 keys: list[str] | None = None,
                 request_plan_descriptors: list[list[object]] | None = None,
                 response_plan_descriptors: list[list[object]] | None = None) -> None:
        from ...internal.binary.BinaryPlan import compile_plan_map

        self.encode_map: dict[str, int] = binary_encoding_map
        self.decode_map: dict[int, str] = {
            v: k for k, v in binary_encoding_map.items()}
        self.checksum: int = checksum
        self.keys: list[str] = keys if keys is not None else [
            self.decode_map[index] for index in sorted(self.decode_map.keys())]
        self.request_plan_descriptors: list[list[object]] = request_plan_descriptors or []
        self.response_plan_descriptors: list[list[object]] = response_plan_descriptors or []
        self.request_plans_by_root_id = compile_plan_map(self.request_plan_descriptors, self)
        self.response_plans_by_function_id = compile_plan_map(self.response_plan_descriptors, self)

    def negotiation_descriptor(self, function_id: int | None, include_bundle: bool) -> dict[str, object]:
        descriptor: dict[str, object] = {
            "v": 1,
        }
        if function_id is not None:
            descriptor["p"] = function_id
        if include_bundle:
            descriptor["k"] = self.keys
            descriptor["q"] = self.request_plan_descriptors
            descriptor["s"] = self.response_plan_descriptors
        return descriptor

    @staticmethod
    def from_negotiation_descriptor(checksum: int, descriptor: dict[str, object]) -> 'BinaryEncoding':
        keys = [cast(str, key) for key in cast(list[object], descriptor["k"])]
        encode_map = {key: index for index, key in enumerate(keys)}
        request_plan_descriptors = cast(list[list[object]], descriptor.get("q", []))
        response_plan_descriptors = cast(list[list[object]], descriptor.get("s", []))
        return BinaryEncoding(encode_map, checksum, keys, request_plan_descriptors, response_plan_descriptors)
