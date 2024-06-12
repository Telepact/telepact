from typing import cast


def is_sub_map(part: dict[str, object], whole: dict[str, object]) -> bool:
    from uapi.internal.mock.IsSubMapEntryEqual import is_sub_map_entry_equal

    for part_key in part.keys():
        whole_value = cast(dict[str, object], whole.get(part_key))
        part_value = cast(dict[str, object], part.get(part_key))
        entry_is_equal = is_sub_map_entry_equal(part_value, whole_value)
        if not entry_is_equal:
            return False
    return True
