def build_map(arr: list[str]) -> dict[str, int]:
    """
    Builds a dictionary mapping each string to its index.
    """
    return {value: idx for idx, value in enumerate(arr)}


def find_string_index(target: str, map: dict[str, int]) -> int | None:
    """
    Returns the index of `target` in O(1) time if it exists, otherwise None.
    """
    return map.get(target)


def main(mw, notes, definedWords):
    fronts = []
    for note in notes:
        fronts.append(note["Front"])

    notesMap = build_map(fronts)

    for word, translation in definedWords:
        index = find_string_index(word, notesMap)
        if index is not None:
            notes[index]["Back"] = translation
            mw.col.update_note(notes[index])
