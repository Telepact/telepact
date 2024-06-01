from typing import List, Union
from uapi.internal.mock.IsSubMap import is_sub_map
from uapi.internal.mock.PartiallyMatches import partially_matches


def is_sub_map_entry_equal(part_value: Union[dict, List], whole_value: Union[dict, List]) -> bool:
    if isinstance(part_value, dict) and isinstance(whole_value, dict):
        return is_sub_map(part_value, whole_value)
    elif isinstance(part_value, list) and isinstance(whole_value, list):
        for part_element in part_value:
            part_matches = partially_matches(whole_value, part_element)
            if not part_matches:
                return False
        return True
    else:
        return part_value == whole_value
