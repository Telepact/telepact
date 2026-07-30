#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import Optional


class InvalidMessage(Exception):
    def __init__(self, cause: Optional[Exception] = None) -> None:
        super().__init__(str(cause) if cause else None)
        self.cause = cause
