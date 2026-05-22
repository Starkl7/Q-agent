# Machine Learning For Trading Notes

Personal working notes for material pulled from Stefan Jansen's
`machine-learning-for-trading` repository.

## Structure

- `chapter-summaries/`: short chapter-by-chapter summaries
- `extraction-notes/`: code snippets, datasets, ideas, and implementation details worth reusing
- `qc-relevance/`: notes on what translates cleanly to QuantConnect and what does not

## Current Seed Files

- `chapter-summaries/book_toc.md`: whole-book table of contents with quick difficulty tags
- `chapter-summaries/advanced_sections.md`: notes for the most technical sections in the TOC
- `extraction-notes/advanced_building_blocks.md`: reusable research and implementation patterns
- `qc-relevance/advanced_sections_qc.md`: LEAN-specific fit, constraints, and substitutions

## Suggested Process

1. Read the chapter or notebook in `../../repos/machine-learning-for-trading/`.
2. Write a short summary in `chapter-summaries/`.
3. Capture reusable logic or data assumptions in `extraction-notes/`.
4. Record QC constraints, substitutions, and implementation ideas in `qc-relevance/`.
5. If the idea deserves a real strategy, create a new project in `MyProjects/` rather than adding it here.

## Naming

- Use filenames like `ch12_summary.md`, `ch12_extraction.md`, and `ch12_qc_relevance.md`.
- Use `ML4Trading_Ch12_<topic>` when the material becomes a dedicated QC project.
