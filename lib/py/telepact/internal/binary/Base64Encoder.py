#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from abc import ABCMeta, abstractmethod


class Base64Encoder(metaclass=ABCMeta):

    @abstractmethod
    def decode(self, message: list[object]) -> list[object]:
        pass

    @abstractmethod
    def encode(self, message: list[object]) -> list[object]:
        pass
