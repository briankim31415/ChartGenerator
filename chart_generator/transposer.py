import re
from collections import Counter
from typing import List, Tuple

NOTE_ORDER_SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# map enharmonic equivalents
ENHARMONIC_MAP = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
}

CHORD_REGEX = re.compile(r"(?P<root>[A-G](?:#|b)?)(?P<suffix>[^\s/]*)?(?:/(?P<bass>[A-G](?:#|b)?))?")


# Tokens that may legally appear in a chord suffix (letters and symbols). Anything outside this set
# is treated as lyrics.
_ALLOWED_SUFFIX_CHARS = set("mMajdimaug+susaddb#0123456789()ºø6°")


def _is_chord_token(token: str) -> bool:
    """Return True if the token matches CHORD_REGEX and its suffix consists only of allowed chars."""
    m = CHORD_REGEX.fullmatch(token)
    if not m:
        return False
    suffix = m.group("suffix") or ""
    return all(ch in _ALLOWED_SUFFIX_CHARS for ch in suffix)


def is_chord_line(line: str) -> bool:
    """A simplistic heuristic: every non-blank token in the line must be a valid chord token."""
    tokens = line.strip().split()
    return bool(tokens) and all(_is_chord_token(tok) for tok in tokens)


def _normalize_note(note: str) -> str:
    """Return canonical sharp representation for a note (e.g. Db -> C#)."""
    return ENHARMONIC_MAP.get(note, note)


def _note_index(note: str) -> int:
    return NOTE_ORDER_SHARPS.index(_normalize_note(note))


def transpose_note(note: str, interval: int) -> str:
    idx = (_note_index(note) + interval) % 12
    return NOTE_ORDER_SHARPS[idx]


def detect_key(chords: List[str]) -> str:
    """Very naive key detection: counts occurrences of each root and chooses the most common that matches major keys."""
    counts = Counter(_normalize_note(c) for c in chords)
    if not counts:
        return "C"  # default
    most_common_note, _ = counts.most_common(1)[0]
    return most_common_note  # simplistic: treat as major key


def parse_chord(chord: str) -> Tuple[str, str, str]:
    """Return (root, suffix, bass) tuple."""
    m = CHORD_REGEX.match(chord)
    if not m:
        raise ValueError(f"Invalid chord: {chord}")
    return m.group("root"), m.group("suffix") or "", m.group("bass") or ""


def build_chord(root: str, suffix: str, bass: str) -> str:
    chord = root + suffix
    if bass:
        chord += f"/{bass}"
    return chord


def transpose_chord(chord: str, interval: int) -> str:
    root, suffix, bass = parse_chord(chord)
    new_root = transpose_note(root, interval)
    new_bass = transpose_note(bass, interval) if bass else ""
    return build_chord(new_root, suffix, new_bass)


def extract_chords_from_line(line: str) -> List[str]:
    return [m.group(0) for m in CHORD_REGEX.finditer(line)]


# Added optional original_key to allow overriding auto-detection when the user specifies input key
def transpose_chart(lines: List[str], target_key: str, original_key: str | None = None) -> List[str]:
    if original_key is None:
        all_chords = []
        for l in lines:
            if is_chord_line(l):
                all_chords.extend(extract_chords_from_line(l))
        original_key = detect_key(all_chords)
    else:
        original_key = original_key
    interval = (_note_index(target_key) - _note_index(original_key)) % 12
    new_lines = []
    for line in lines:
        if is_chord_line(line):
            def _replace(match):
                return transpose_chord(match.group(0), interval)
            new_lines.append(CHORD_REGEX.sub(_replace, line))
        else:
            new_lines.append(line)
    return new_lines
