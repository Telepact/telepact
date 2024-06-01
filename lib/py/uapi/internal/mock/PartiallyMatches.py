from typing import List


def partially_matches(whole_list: List[object], part_element: object) -> bool:
    from uapi.internal.mock.IsSubMapEntryEqual import is_sub_map_entry_equal

    for whole_element in whole_list:
        if is_sub_map_entry_equal(part_element, whole_element):
            return True
    return False
