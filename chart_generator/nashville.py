import re
from typing import List
from .transposer import CHORD_REGEX, _normalize_note, _note_index, is_chord_line

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # semitone offsets from tonic
NASHVILLE_NUMBERS = {0: "1", 2: "2", 4: "3", 5: "4", 7: "5", 9: "6", 11: "7"}


def _degree(note_index: int, key_index: int) -> str:
    semitone = (note_index - key_index) % 12
    return NASHVILLE_NUMBERS.get(semitone, "?")


def convert_chart_to_nashville(lines: List[str], key: str) -> List[str]:
    key_index = _note_index(key)

    def _chord_to_nash(match: re.Match) -> str:
        root = _normalize_note(match.group("root"))
        suffix = match.group("suffix") or ""
        bass = match.group("bass") or ""
        num = _degree(_note_index(root), key_index)
        # Determine minor/major by lowercase suffix starting with 'm'
        if suffix.startswith("m") and num.isdigit():
            num = num + "m"
        out = num + suffix.lstrip("m")  # keep other suffix parts
        if bass:
            out += f"/{_degree(_note_index(bass), key_index)}"
        return out

    converted = []
    for line in lines:
        if is_chord_line(line):
            converted.append(CHORD_REGEX.sub(_chord_to_nash, line))
        else:
            converted.append(line)
    return converted
