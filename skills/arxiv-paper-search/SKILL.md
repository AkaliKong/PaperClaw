---
name: arxiv-paper-search
description: This skill should be used when the user wants to search for academic papers on arXiv. It supports searching by keywords, author, title, abstract, and categories with customizable time ranges. Use this skill when users ask to find papers, search for research, look up academic articles, or query arXiv for specific topics like "RAG papers", "LLM research", or "find papers by author X".
---

# arXiv Paper Search Skill

Search and download academic papers from arXiv with flexible query options.

## Capabilities

- Search by keywords, title, author, abstract
- Filter by arXiv categories (cs.AI, cs.CL, cs.CV, etc.)
- Set custom time ranges (default: 1 year)
- Download PDFs
- Export results to Markdown

## Dependencies

Install the required package before using:

```bash
pip install arxiv
```

## Bundled Script

The search script is bundled at `scripts/arxiv_search.py`. To use it:

1. Copy the script to a working directory or run directly from skill path
2. Install dependencies: `pip install arxiv`
3. Run the script with desired parameters

## Usage

### Command Line

```bash
# Search by keywords (default: last 1 year)
python scripts/arxiv_search.py -k "retrieval augmented generation" "RAG"

# Search by author
python scripts/arxiv_search.py -a "Yann LeCun"

# Search by title
python scripts/arxiv_search.py -t "transformer"

# Filter by category (supports shortcuts)
python scripts/arxiv_search.py -k "LLM" -c nlp ai

# Set time range
python scripts/arxiv_search.py -k "RAG" --days 7      # Last week
python scripts/arxiv_search.py -k "RAG" --days 30     # Last month

# Show detailed abstracts
python scripts/arxiv_search.py -k "RAG" -v

# Export to Markdown
python scripts/arxiv_search.py -k "RAG" --export

# Download papers
python scripts/arxiv_search.py -k "RAG" --download 1,2,3
python scripts/arxiv_search.py -k "RAG" --download all
```

### Category Shortcuts

| Shortcut | Category | Shortcut | Category |
|----------|----------|----------|----------|
| ai | cs.AI | ml | cs.LG |
| nlp | cs.CL | cv | cs.CV |
| ir | cs.IR | se | cs.SE |
| db | cs.DB | robotics | cs.RO |
| crypto | cs.CR | stat | stat.ML |

### Parameters

| Parameter | Description |
|-----------|-------------|
| `-k, --keywords` | Keywords (multiple supported) |
| `-t, --title` | Title keywords |
| `-a, --author` | Author name (comma-separated for multiple) |
| `-b, --abstract` | Abstract keywords |
| `-c, --categories` | Categories (e.g., cs.AI or shortcut ai) |
| `-i, --id` | arXiv ID (get specific paper) |
| `--days` | Time range in days (default: 365) |
| `-n, --num` | Max results (default: 20) |
| `-s, --sort` | Sort: submitted/relevance/updated |
| `-v, --verbose` | Show detailed abstracts |
| `--export` | Export to Markdown |
| `--download` | Download papers (indices or "all") |

### Python API

```python
# Import from skill's scripts directory
import sys
sys.path.append('<skill-path>/scripts')
from arxiv_search import ArxivSearcher

searcher = ArxivSearcher()

# Search
results = searcher.search(
    keywords=["RAG", "retrieval augmented generation"],
    categories=["cs.CL", "cs.AI"],
    days=30,
    max_results=20
)

# Display results
searcher.display(results, verbose=True)

# Export to Markdown
searcher.export_markdown(results)

# Download specific papers
searcher.download(results, indices=[1, 2, 3])
```

## Output Locations

- PDF downloads: `~/Downloads/arxiv_papers/`
- Markdown exports: `~/Downloads/arxiv_papers/search_results_*.md`

## Common Search Examples

```bash
# RAG research (last week)
python scripts/arxiv_search.py -k "RAG" "retrieval augmented generation" -c nlp ai --days 7 -v

# LLM Agent papers
python scripts/arxiv_search.py -k "LLM agent" "tool use" -c ai

# Multimodal models
python scripts/arxiv_search.py -k "multimodal" "vision language model" -c cv nlp

# Specific author's papers
python scripts/arxiv_search.py -a "Ilya Sutskever" --days 365

# Knowledge graph + RAG
python scripts/arxiv_search.py -k "knowledge graph" "RAG" -c ai ir

# Export weekly RAG summary
python scripts/arxiv_search.py -k "RAG" --days 7 --export
```

## Execution Workflow

When executing this skill:

1. Determine the script path (bundled `scripts/arxiv_search.py`)
2. Build the command with appropriate parameters based on user request
3. Execute the command and display results
4. Offer to download or export if user requests
