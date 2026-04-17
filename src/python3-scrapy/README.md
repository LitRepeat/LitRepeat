# LitRepeat – Scholarly Metadata Scraper

Scrapy-based tool that extracts scholarly article metadata from academic
publishers and exports it as JSON + BibTeX.

## Supported providers

| Provider | Spider | Example URL |
|----------|--------|-------------|
| [ACM Digital Library](https://dl.acm.org) | `acm` | `https://dl.acm.org/doi/abs/10.1145/1232425.1232431` |

## Prerequisites

### With Nix

[Nix](https://nixos.org/) provides all dependencies (including `uv`) automatically:

```bash
nix-shell
```

### Without Nix (macOS / Linux / Windows)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or via Homebrew
brew install uv
```

Then install dependencies and the Playwright browser:

```bash
uv sync
uv run playwright install chromium
```

## Usage

Run a spider by name, passing the article URL:

```bash
uv run scrapy crawl <spider> -a url=<article-url>
```

### Examples

```bash
# ACM Digital Library
uv run scrapy crawl acm -a url=https://dl.acm.org/doi/abs/10.1145/1232425.1232431
```

> **Nix users:** prefix commands with `nix-shell` to enter the development
> environment first.

## Output

Results are written to the `output/` directory:

| File | Content |
|------|---------|
| `<Year>-<Title>.json` | Article metadata (title, authors, abstract, DOI, venue, …) |
| `<Year>-<Title>.bib`  | BibTeX citation with matching reference key |

Responses are cached in `.scrapy/httpcache/` so repeated runs for the same URL
do not make additional requests.
