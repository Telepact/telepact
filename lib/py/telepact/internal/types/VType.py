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

from typing import TYPE_CHECKING
from abc import ABCMeta, abstractmethod


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .VTypeDeclaration import VTypeDeclaration
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext


class VType(metaclass=ABCMeta):
    @abstractmethod
    def get_type_parameter_count(self) -> int:
        pass

    @abstractmethod
    def validate(self, value: object,
                 type_parameters: list['VTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        pass

    @abstractmethod
    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['VTypeDeclaration'], ctx: 'GenerateContext') -> object:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
