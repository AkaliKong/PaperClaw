# read-arxiv-paper

Deep paper reading Skill for the paper-reading-agent pipeline.

## Overview

Deeply reads an arXiv paper (via TeX source or PDF) and produces a structured knowledge card tailored for research in Generative Recommendation & LLM fields.

## Architecture

- **Agent-driven**: The Agent downloads, reads, and synthesizes — no deterministic script
- **Source priority**: Prefers TeX source over PDF for higher fidelity
- **Single-paper rule**: Strictly processes one paper per session to ensure quality

## Output

- **Knowledge card**: `research/papers/{sub_field}/{arxiv_id}_{tag}/card.md`
- **Cache**: `/data/workspace/research/cache/{arxiv_id}/`