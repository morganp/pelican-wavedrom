# pelican-wavedrom

A [Pelican](https://getpelican.com/) plugin that renders [WaveDrom](https://wavedrom.com/) timing diagrams in blog posts. Write a fenced `wavedrom` code block in your markdown; the plugin converts it to an SVG during `make html` so the generated site shows an actual diagram.

## How it works

1. The plugin intercepts ` ```wavedrom ``` ` fenced blocks before Pelican's standard markdown processing.
2. It calls `wavedrom-cli` to render the WaveJSON to an SVG file, cached by content hash in `content/images/wavedrom/`.
3. The block is replaced with a standard image reference pointing to the SVG.
4. Pelican copies the SVG to `output/images/wavedrom/` as a static asset.

SVGs are cached — rebuilds only re-render diagrams whose source has changed.

---

## Requirements

- Pelican 4.5+
- Python 3.9+
- Node.js with `wavedrom-cli` installed globally:

```bash
npm install -g wavedrom-cli
```

---

## Installation

Clone or download this repo alongside your Pelican project, then install it into your Pelican virtualenv in editable mode:

```bash
source venv/bin/activate
pip install -e ../pelican-wavedrom --config-settings editable_mode=compat
```

> **Note:** The `editable_mode=compat` flag is required. Without it, modern setuptools editable installs use a path hook mechanism that prevents Pelican's namespace plugin auto-discovery from finding the plugin.

Pelican 4.5+ auto-discovers namespace plugins — **no changes to `pelicanconf.py` are needed**.

### Optional config

If `wavedrom-cli` is not on your `PATH` during the build (e.g. in a CI environment), set its full path in `pelicanconf.py`:

```python
WAVEDROM_CLI = '/opt/homebrew/bin/wavedrom-cli'
```

---

## Usage

In any markdown post, use a fenced code block with the language set to `wavedrom`:

````markdown
```wavedrom
{ "signal": [
  { "name": "CLK",  "wave": "p.....|..." },
  { "name": "Data", "wave": "x.345x|=.x", "data": ["head", "body", "tail", "data"] },
  { "name": "Request", "wave": "0.1..0|1.0" }
]}
```
````

This renders to:

![Example WaveDrom timing diagram](https://wavedrom.com/images/wavedrom.svg)

The block is replaced at build time with an `<img>` tag referencing the generated SVG. The SVG is a proper static asset served from `images/wavedrom/` in your site output.

### WaveJSON syntax

The block content is standard [WaveJSON](https://wavedrom.com/tutorial.html). Some common signal wave characters:

| Character | Meaning |
|-----------|---------|
| `p` / `n` | positive / negative clock edge |
| `0` / `1` | low / high |
| `x` | undefined |
| `z` | high impedance |
| `=` | data (labelled via `data` array) |
| `2`–`9` | data with colour coding |
| `.` | continue previous state |
| `\|` | gap |

See the full [WaveDrom tutorial](https://wavedrom.com/tutorial.html) for edges, delays, groups, and more.

---

## Fallback behaviour

If `wavedrom-cli` is not found or rendering fails, the block falls back to a fenced `json` code block so the post still builds — you just see the raw JSON instead of a diagram.

---

## Project structure

```
pelican-wavedrom/
├── pyproject.toml
├── pelican/                              # namespace package — no __init__.py
│   └── plugins/                          # namespace package — no __init__.py
│       └── wavedrom_generator/
│           ├── __init__.py               # plugin entry point, signal registration
│           └── preprocessor.py           # Markdown extension + preprocessor
```

The `pelican/` and `pelican/plugins/` directories intentionally have no `__init__.py` — they are PEP 420 namespace packages that merge with Pelican's own namespace.
