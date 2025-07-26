# Adobe Round 1B: Persona-Driven Document Intelligence

A containerized Python solution that intelligently extracts and ranks document sections based on user persona and job requirements.

## Overview

This solution processes collections of PDF documents (3-10 files) and identifies the most relevant sections for a specific persona and their job-to-be-done. It uses advanced NLP techniques to understand document structure, extract semantic features, and rank content by relevance.

## Features

- **Robust PDF Processing**: Handles various PDF formats with fallback mechanisms
- **Intelligent Section Detection**: Automatically identifies document structure and headings
- **Semantic Analysis**: Uses TF-IDF and spaCy for content understanding
- **Multi-factor Ranking**: Combines relevance, position, length, and entity factors
- **Offline Processing**: No internet connectivity required
- **Fast Performance**: Processes 3-5 documents in under 60 seconds

## Requirements

- Docker with AMD64 architecture support
- Input PDFs (up to 10 documents)
- Configuration file with persona and job description

## Quick Start

### 1. Build the Docker Image

```bash
docker build --platform linux/amd64 -t persona-doc-intelligence:latest .
