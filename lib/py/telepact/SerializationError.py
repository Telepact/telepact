#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

class SerializationError(Exception):
    def __init__(
        self,
        message: str = "telepact serialization failed",
        *,
        context: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        if context:
            message = f"{message} while {context}"
        if cause is not None:
            message = f"{message}: {cause}"
        super().__init__(message)
        self.context = context
        self.cause = cause
