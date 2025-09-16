from typing import List
from .transposer import extract_chords_from_line

MAX_WIDTH_DEFAULT = 80


def split_sections(lines: List[str]):
    sections = []
    current = {"title": None, "lines": []}
    for line in lines:
        if line.startswith("[") and "]" in line:
            # new section
            if current["lines"]:
                sections.append(current)
            current = {"title": line.strip(), "lines": []}
        else:
            current["lines"].append(line.rstrip("\n"))
    if current["lines"] or current["title"]:
        sections.append(current)
    return sections


def parse_chart(text: str) -> List[str]:
    """Return list of lines from raw chart text."""
    return text.splitlines()


def compress_repeated_sections(sections):
    """Replace repeated sections with a placeholder line, optionally with xN for multiple repeats.

    The first appearance of a section is kept in full (title + lines). Subsequent
    appearances are reduced to a single title line.  Consecutive repeats of the
    *same* section are collapsed into a single line with an "xN" suffix.
    """
    outputs: List[str] = []
    # Map of section key -> index of placeholder line in outputs
    placeholder_indices = {}
    repeat_counts = {}

    for sec in sections:
        key = tuple(sec["lines"])  # use content for equality, regardless of title differences
        title = sec["title"] or "[Section]"

        if key not in placeholder_indices:
            # First occurrence – write out fully
            outputs.append(title)
            outputs.extend(sec["lines"])
            # Track index of where the *next* placeholder would be (after original)
            placeholder_indices[key] = None  # will be set on first repeat
            repeat_counts[key] = 1
            continue

        # Repeat occurrence
        repeat_counts[key] += 1
        count = repeat_counts[key]

        if placeholder_indices[key] is None:
            # First repeat – add placeholder line
            outputs.append(title)  # placeholder at end for now
            placeholder_indices[key] = len(outputs) - 1
        else:
            # Subsequent repeat – do not add new line, just update existing placeholder
            pass

        # Update placeholder text to include xN when N > 1
        idx = placeholder_indices[key]
        base_title = title.split(" x")[0]  # strip previous count if present
        suffix = f" x{count}" if count > 2 else ""
        outputs[idx] = f"{base_title}{suffix}"

    # Ensure two blank lines between sections (titles starting with '[')
    spaced: List[str] = []
    for line in outputs:
        if line.startswith("["):
            if spaced:
                # trim trailing blanks
                while spaced and spaced[-1] == "":
                    spaced.pop()
                # add exactly two blank lines
                spaced.extend(["", ""])
        spaced.append(line)

    # Collapse any sequences of more than 2 blank lines to exactly 2
    final: List[str] = []
    blank_run = 0
    for ln in spaced:
        if ln.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                final.append("")
        else:
            blank_run = 0
            final.append(ln)

    return final


def enforce_max_width(lines: List[str], width: int = MAX_WIDTH_DEFAULT) -> List[str]:
    return [l if len(l) <= width else l[:width] for l in lines]
