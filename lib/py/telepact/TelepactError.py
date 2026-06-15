#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from uuid import uuid4


class TelepactError(Exception):
    """
    Indicates critical failure in telepact processing logic.
    """

    def __init__(
        self,
        message: str = "telepact error",
        *,
        kind: str | None = None,
        cause: BaseException | None = None,
        case_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.cause = cause
        self.case_id = case_id or str(uuid4())
