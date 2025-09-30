# Guitar Chart Generator

Generate neatly-formatted, monospace chord charts in **Word (DOCX)** format.
The tool can:

-   Detect the original key of a song.
-   Transpose all chords into any new key while preserving alignment.
-   Convert chords to the Nashville Number System.
-   Collapse repeated sections (e.g. `[Chorus] x2`).
-   Respect a maximum text width so charts don’t overflow the page.
-   Output chords **bolded** while lyrics stay regular.

---

## Installation

```bash
# clone the repository
$ git clone <repo-url> ChartGenerator
$ cd ChartGenerator

# (optional) create a virtual environment
$ python -m venv venv
$ source venv/bin/activate

# install dependencies
$ pip install -r requirements.txt
```

Dependencies are minimal – the main external library is `python-docx` for Word export.

---

## Usage – CLI

```bash
python chart_generator.py <chart.txt> [--key NEW_KEY | --nashville] [-o OUTPUT.docx] [--input-key KEY]
                         [--input-dir DIR] [--output-dir DIR] [--max-width N]
```

Arguments:

| Argument / Flag    | Description                                                                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `chart.txt`        | Name or path of the input chord chart. If not a full path, the tool looks inside `input/`.                                                      |
| `-o`, `--output`   | Destination DOCX path or **just a filename**. If only a filename is provided, it is placed inside `output/`. Defaults to `output/<chart>.docx`. |
| `--input-dir DIR`  | Directory where charts are stored (default: `input/`).                                                                                          |
| `--output-dir DIR` | Directory where generated DOCX files are written (default: `output/`).                                                                          |
| `--key NEW_KEY`    | Transpose to a new key (e.g. `G`, `F#`, `Bb`).                                                                                                  |
| `--input-key KEY`  | Specify the original key of the input chart (default: `C`; overrides auto-detection).                                                           |
| `--nashville`      | Convert chords to Nashville numbers (default: enabled).                                                                                         |
| `--max-width N`    | Wrap / truncate lines at width _N_ (default **80**).                                                                                            |

Only one of `--key` _or_ `--nashville` should be supplied.

### Example 1 – Default directories

```bash
# Copy or move your chart into the default input directory
cp my_song.txt input/

# Transpose and write to output/my_song.docx
python chart_generator.py my_song.txt --key G
```

### Example 2 – Custom output path

```bash
# Convert to Nashville numbers and write to a custom file name
cp my_song.txt input/

python chart_generator.py my_song.txt --nashville -o my_song_nashville.docx
```

The generated `.docx` keeps the original spacing. Chords appear in **bold Courier New**, lyrics in regular Courier New.

---

## Input Format

-   Monospaced (text) chord charts – each chord sits exactly above the lyric syllable it accompanies.
-   Section headings inside square brackets, e.g. `[Verse 1]`, `[Chorus]`.
-   Slash chords (e.g. `D/F#`) and accidentals (`C#`, `Bb`) are supported.

```text
[Verse 1]
       D/F#              G
In the darkness, we were waiting
        A             D
Without hope, without light
```

The same section repeated later is automatically reduced to `[Chorus]` or `[Chorus] xN` for multiple identical repeats.

---

## Library API (Python)

```python
from chart_generator import (
    parse_chart,
    transpose_chart,
    convert_chart_to_nashville,
    export_chart_to_docx,
)

text = Path("examples/example_song.txt").read_text()
lines = parse_chart(text)

# transpose
lines = transpose_chart(lines, "F")

# convert to Nashville numbers (will auto-detect key)
# lines = convert_chart_to_nashville(lines, "D")

export_chart_to_docx(lines, "out.docx")
```

All helper functions are documented in their respective modules.

---

## Project Structure

```
chart_generator/
  ├── __init__.py          # exports public API
  ├── parser.py            # parsing, section handling, width enforcement
  ├── transposer.py        # chord parsing, transposition, key detection
  ├── nashville.py         # Nashville number conversion
  └── docx_writer.py       # DOCX generation (python-docx)
chart_generator.py          # CLI entry point
examples/
  └── example_song.txt     # sample input chart
requirements.txt
README.md
```

---

## Why Courier New?

A true monospaced font ensures chord alignment remains intact when exported to Word. Courier New is universally available on Windows and macOS; feel free to change it in `chart_generator/docx_writer.py`.

---

## License

MIT – use freely, PRs welcome!
