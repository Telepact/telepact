from typing import List, Dict, Any, Union
from uapi.internal.types import UNumber
from uapi.internal.validation import GetTypeUnexpectedValidationFailure


def validate_number(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, (int, float, complex)):
        return []
    elif isinstance(value, (UNumber.BigInteger, UNumber.BigDecimal)):
        return [
            {
                "path": [],
                "code": "NumberOutOfRange",
                "details": {}
            }
        ]
    else:
        return GetTypeUnexpectedValidationFailure.get_type_unexpected_validation_failure([], value, UNumber._NUMBER_NAME)
