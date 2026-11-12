# gCalc

A terminal-based grade calculator built with [Textual](https://textual.textualize.io/). Track scores in a spreadsheet-style table, organize them into categories, and see your overall grade update as you edit.

## Features

- Spreadsheet-style grade table in the terminal
- Add, remove, and rename category columns
- Edit scores in place with a popup editor
- Assign a weight to each category
- Live overall grade display

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended)

## Installation

```bash
git clone https://github.com/S-Roomi/gCalc.git
cd gCalc
uv sync
```

## Usage

```bash
uv run main.py
```

### Key Bindings

| Key | Action |
| --- | --- |
| `e` | Edit the selected cell |
| `a` | Add a row to the selected column |
| `A` | Add a column |
| `r` | Remove the last row |
| `R` | Remove the last column |
| `n` | Rename the selected column |
| `w` | Set the selected column's weight (e.g. `0.5` for 50%) |
| `q` | Quit |

Use the arrow keys to move between cells. Clicking a column header also renames it.

## Project Structure

```
gCalc/
├── main.py           # Textual app and UI
├── gCalc.tcss        # App stylesheet
└── src/
    └── grade.py      # Course model and grade calculations
```

## License

Released under the [MIT License](LICENSE).
