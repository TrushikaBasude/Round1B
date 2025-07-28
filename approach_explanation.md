Challenge 1B - Approach Explanation
Overview
This solution implements a robust, lightweight pipeline for Adobe Round 1B, designed to process PDF resumes and extract the most relevant sections and subsections based on a configurable persona and job description. The pipeline emphasizes:

Speed

Offline compatibility

Zero heavy ML

Resilience across varied document formats

The final output ranks relevant content, aligned with the scoring schema, while ensuring performance even on resource-constrained environments.

Architecture

1. PDF Processing (src/pdf_processor.py)
Text Extraction:

Utilizes pdfplumber for accurate layout-aware parsing of PDFs.

Falls back to PyPDF2 in case of parsing issues.

Section Identification:

Uses rule-based heuristics to detect likely section headers.

Criteria include: short lines, all-uppercase, numbering patterns (e.g., "1. Introduction"), and matching section-like keywords.

When font metadata is available, it's used to improve header detection.

Section Segmentation:

Extracts section content until the next heading is encountered.

If a heading is not confidently found, the first few words of the section are used as a fallback title.

2. Lightweight Content Analysis (src/text_analyzer_lite.py)
Keyword Extraction:

The persona and job fields (from a flexible .json input config) are lowercased and tokenized into keyword sets.

Section Representation:

Each section’s text is also tokenized.

No external NLP libraries (e.g., spaCy, transformers) are used, keeping it light and fast.

3. Section Ranking (src/section_ranker_lite.py)
Relevance Scoring:

Each section and subsection is scored based on:

Jaccard-style keyword overlap with persona + job.

Length normalization: slight preference for medium-sized sections.

Page position bias: content earlier in the resume gets a minor boost.

Global Stack Ranking:

All sections are ranked globally and the top N are returned in:

extracted_sections

subsection_analysis

Title Handling:

Outputs the detected title or a smart fallback based on initial content words (avoiding "Untitled").

4. Output Format (main.py → /output/challenge1b_output.json)
Metadata:

Includes PDF name, job and persona text, runtime stats, and timestamp.

Extracted Sections:

Format: {document, section_title, importance_rank, page_number}

Subsection Analysis:

Format: {document, refined_text, page_number} for top-matching content spans.

Schema Compliance:

Output is always valid and matches challenge specifications for scoring.

Key Features & Optimizations

Flexible Config Detection:

Any JSON file placed in the input/ directory is auto-detected, allowing for arbitrary file names (e.g., challenge1b_input.json).

Graceful Error Handling:

Supports missing/empty PDFs, uses fallback parsers, and always produces either output or meaningful error logs.

Ultra-Fast Performance:

Processes 3–10 PDFs in under 10 seconds on most machines.

Docker builds in < 2 minutes.

Minimal Dependencies:

Only uses: pdfplumber, PyPDF2, and numpy

This ensures fast builds and zero bloat.

Challenges Faced

Messy PDF Structures:

Many resumes lacked clear formatting or had unusual heading styles.

Solved with dynamic font heuristics and title fallback logic.

Ambiguous Input Filenames:

Avoided hardcoding by detecting any .json config input dynamically.

No Embedding Models:

Skipped all ML-based approaches to ensure fast builds and compatibility with low-resource environments.