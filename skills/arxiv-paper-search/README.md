# arxiv-paper-search

arXiv paper search Skill for the paper-reading-agent pipeline.

## Overview

Searches arXiv for academic papers by keywords, author, title, abstract, or categories with customizable time ranges. Uses arXiv HTTP API with pure standard library implementation (no `arxiv` package required).

## Architecture

- **Bundled script**: `scripts/arxiv_search.py` handles all search, display, and export logic
- **Pure stdlib**: Uses only Python standard library (`urllib`, `xml.etree`) for HTTP + XML parsing
- **Rate-limit aware**: Built-in retry logic and 3-second delays between paginated requests

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/arxiv_search.py` | Search arXiv, display results, export to Markdown |

## Key Features

- Search by keywords, title, author, abstract
- Filter by arXiv categories (cs.AI, cs.CL, cs.CV, etc.) with shortcut support
- Configurable time range (default: 1 year)
- Export results to Markdown
- Sort by submission date, relevance, or update date

## Usage

```bash
# Search by keywords
python scripts/arxiv_search.py -k "retrieval augmented generation" "RAG"

# Search by author
python scripts/arxiv_search.py -a "Yann LeCun"

# Filter by category with time range
python scripts/arxiv_search.py -k "LLM" -c nlp ai --days 30

# Export results
python scripts/arxiv_search.py -k "RAG" --export
```
