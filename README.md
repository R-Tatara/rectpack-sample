[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
<img src="https://img.shields.io/badge/-Ubuntu-6F52B5.svg?logo=ubuntu&style=flat">

# rectpack-sample

A Python project demonstrating rectangle packing algorithms with multi-type workpiece support and visualization. Uses the rectpack library to efficiently pack workpieces into bins with configurable dimensions, rotation, and layering.

## Prerequisites

- Python 3.12 or later
- uv (Python package manager)

## Installation

```bash
git clone https://github.com/R-Tatara/rectpack-sample.git
cd rectpack-sample
uv sync
```

## Usage

### Single Item Type Packing

Pack identical workpieces across multiple bins with multiple layers per bin:

```bash
uv run python single_items.py
```

Output includes:
- Packing statistics grouped by box and layer
- Visual representation of packed items

### Mixed Item Types Packing

Pack different workpiece types into a single bin:

```bash
uv run python mixed_items.py
```

Output includes:
- Packing statistics by workpiece type
- Visualization with color-coded items

## LICENSE

MIT
