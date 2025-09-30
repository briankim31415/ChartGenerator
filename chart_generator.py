import argparse
import re
import sys
from pathlib import Path

from chart_generator.parser import parse_chart, split_sections, enforce_max_width, compress_repeated_sections
from chart_generator.transposer import transpose_chart, detect_key, CHORD_REGEX, is_chord_line
from chart_generator.nashville import convert_chart_to_nashville
from chart_generator.docx_writer import export_chart_to_docx


def main(argv=None):
    parser = argparse.ArgumentParser(description="Guitar chart generator")
    parser.add_argument("chart", help="Chart filename or path (e.g., my_song.txt)")
    parser.add_argument("--output", "-o", help="Output DOCX path (optional)")
    parser.add_argument("--input-dir", default="input", help="Directory containing input charts (default: input/)")
    parser.add_argument("--output-dir", default="output", help="Directory to place generated DOCX files (default: output/)")
    parser.add_argument("--key", help="Target key (e.g., G, F#)")
    parser.add_argument("--nashville", action="store_true", default=True, help="Convert to Nashville numbers (default: enabled)")
    parser.add_argument("--input-key", default="C", help="Key of the input chart (default: C; overrides auto-detection, e.g., Eb)")
    parser.add_argument("--lyrics-only", action="store_true", help="Generate document with lyrics only (no chords)")
    parser.add_argument("--max-width", type=int, default=80, help="Maximum text width")
    args = parser.parse_args(argv)

    # Resolve input path: if supplied path exists, use as-is else look in input-dir
    input_path = Path(args.chart)
    if not input_path.exists():
        input_path = Path(args.input_dir) / args.chart
    if not input_path.exists():
        parser.error(f"Input chart '{args.chart}' not found (looked in current dir and '{args.input_dir}/').")

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        op = Path(args.output)
        # If the user supplied only a basename (no directory parts) and it is not an absolute path,
        # place it inside the output directory automatically.
        if not op.is_absolute() and op.parent == Path('.'):
            output_path = output_dir / op
        else:
            output_path = op
    else:
        if args.key:
            suffix = f"_{args.key.upper()}"
        elif args.nashville:
            suffix = "_Nashville"
        elif args.lyrics_only:
            suffix = "_Lyrics"
        else:
            suffix = ""
        output_path = output_dir / f"{input_path.stem}{suffix}.docx"

    text = input_path.read_text()
    lines = parse_chart(text)

    if args.key:
        lines = transpose_chart(lines, args.key, args.input_key.upper() if args.input_key else None)
    elif args.nashville:
        if args.input_key:
            key = args.input_key.upper()
        else:
            original_chords = []
            for l in lines:
                original_chords.extend(re.findall(r"[A-G](?:#|b)?", l))
            key = detect_key(original_chords)
        # Transpose to same key first (identity), then convert
        lines = convert_chart_to_nashville(lines, key)

    sections = split_sections(lines)
    lines = compress_repeated_sections(sections)
    lines = enforce_max_width(lines, args.max_width)

    # Optionally strip chords to create a lyrics-only version
    if args.lyrics_only:
        import chart_generator.docx_writer as dw  # avoids circular at top-level

        def _remove_inline_chords(ln: str) -> str:
            """Remove any chord tokens within a mixed lyrics line while preserving spacing."""
            return CHORD_REGEX.sub("", ln).rstrip()

        lyric_lines = []
        for ln in lines:
            if is_chord_line(ln) or dw.is_nashville_line(ln):
                # Skip pure chord/nashville lines entirely
                continue
            lyric_lines.append(_remove_inline_chords(ln))
        lines = lyric_lines

    export_chart_to_docx(lines, str(output_path))
    print(f"Chart written to {output_path}")


if __name__ == "__main__":
    main()
