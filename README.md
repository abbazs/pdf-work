# PDF Work

CLI toolkit to read, mask, replace, and delete text in PDF files.

Built with [cyclopts](https://cyclopts.readthedocs.io/), [Rich](https://rich.readthedocs.io/), and [rich-stepper](https://github.com/abbazs/rich-stepper).

## Install

```bash
uv sync
```

## Commands

### `pdf read` — Extract text from a PDF

Prints PDF text content to the terminal with per-page progress.

```bash
# Read entire PDF
pdf read -f document.pdf

# Read specific pages
pdf read -f document.pdf -p 1
pdf read -f document.pdf -p 1 3 5
```

#### Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--file` | `-f` | Path to the PDF file (required) |
| `--pages` | `-p` | Page numbers to extract |

---

### `pdf mask` — Redact text in a PDF

Finds text patterns and draws colored rectangles over them, saving a new PDF with the content permanently removed.

```bash
# Mask a single text pattern
pdf mask -f input.pdf -o output.pdf -t "SSN"

# Mask multiple patterns in one run
pdf mask -f input.pdf -o output.pdf -t "SSN" -t "Account No" -t "Phone"

# Mask with line mode — covers the entire line, not just the matched text
pdf mask -f input.pdf -o output.pdf -t "CONFIDENTIAL" --line

# Use a lighter fill color to save printer ink
pdf mask -f input.pdf -o output.pdf -t "SSN" --color white
pdf mask -f input.pdf -o output.pdf -t "SSN" --color gray
pdf mask -f input.pdf -o output.pdf -t "SSN" --color "#cccccc"

# Combine flags
pdf mask -f input.pdf -o output.pdf -t "SSN" -t "DOB" --line --color white -i
```

#### Flags

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--file` | `-f` | Input PDF path (required) | — |
| `--output` | `-o` | Output PDF path (required) | — |
| `--text` | `-t` | Text pattern to mask (repeatable) (required) | — |
| `--line` | `-l` | Mask the entire line containing the match | `false` |
| `--insensitive` | `-i` | Case-insensitive matching | `false` |
| `--color` | `-c` | Fill color — name or hex | `black` |

#### Available colors

| Name | Hex |
|------|-----|
| `black` | `#000000` |
| `white` | `#FFFFFF` |
| `gray` / `grey` | `#808080` |
| `red` | `#FF0000` |
| `green` | `#00FF00` |
| `blue` | `#0000FF` |
| `yellow` | `#FFFF00` |

Any `#RRGGBB` hex value is also accepted via `--color "#RRGGBB"`.

---

## Real-world examples

### Redact sensitive medical information

```bash
pdf mask -f medical_report.pdf -o safe_report.pdf \
  -t "Patient Name" -t "SSN" -t "Diagnosis" --line --color black
```

### Remove account numbers from a bank statement (ink-friendly)

```bash
pdf mask -f bank_statement.pdf -o clean_statement.pdf \
  -t "Account No" -t "Routing" --color white --line
```

### Mask only specific fields, keeping surrounding text visible

```bash
pdf mask -f contract.pdf -o redacted_contract.pdf \
  -t "Salary" -t "Compensation"
```

### Quick peek at a PDF before processing

```bash
pdf read -f contract.pdf -p 1 2 3
```

### Verify masking worked

```bash
pdf read -f redacted_contract.pdf | grep -i "salary"
# (should return nothing)
```
