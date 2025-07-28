#!/usr/bin/env python3

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime
import numpy as np
import pdfplumber
from PyPDF2 import PdfReader  # Fallback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_sections_from_pdf(pdf_path):
    """Improved PDF extraction: Better title detection to avoid 'Untitled'."""
    sections = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):  # Start pages from 1 for consistency
                text = page.extract_text() or ""
                words = page.extract_words()  # Use word metadata for better detection (e.g., font size)
                if text:
                    lines = text.split('\n')
                    current_section = {"title": "Untitled", "text": "", "page": page_num}
                    for line in lines:
                        stripped = line.strip()
                        # Improved heuristic: Short lines (<100 chars), potential titles (uppercase, digit start, or common patterns)
                        # Also check if line has larger font via words metadata
                        is_title = (
                            (stripped and len(stripped) < 100 and (stripped.isupper() or stripped[0].isdigit())) or
                            stripped.lower().startswith(('section', 'chapter', 'part', 'introduction', 'conclusion')) or
                            any(w['text'] == stripped and w['height'] > 12 for w in words)  # Rough font size check (adjust threshold if needed)
                        )
                        if is_title:
                            if current_section["text"]:
                                sections.append(current_section)
                            current_section = {"title": stripped, "text": "", "page": page_num}
                        else:
                            current_section["text"] += line + " "
                    if current_section["text"]:
                        # Fallback: If still "Untitled", use first few words of text as title
                        if current_section["title"] == "Untitled":
                            first_words = ' '.join(current_section["text"].strip().split()[:5])
                            current_section["title"] = first_words if first_words else "Untitled Section"
                        sections.append(current_section)
    except Exception as e:
        logger.warning(f"Fallback to PyPDF2 for {pdf_path}: {str(e)}")
        try:
            reader = PdfReader(pdf_path)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                lines = text.split('\n')
                current_section = {"title": "Untitled", "text": "", "page": page_num}
                for line in lines:
                    stripped = line.strip()
                    # Same improved heuristic (without font info in fallback)
                    is_title = (
                        (stripped and len(stripped) < 100 and (stripped.isupper() or stripped[0].isdigit())) or
                        stripped.lower().startswith(('section', 'chapter', 'part', 'introduction', 'conclusion'))
                    )
                    if is_title:
                        if current_section["text"]:
                            sections.append(current_section)
                        current_section = {"title": stripped, "text": "", "page": page_num}
                    else:
                        current_section["text"] += line + " "
                if current_section["text"]:
                    if current_section["title"] == "Untitled":
                        first_words = ' '.join(current_section["text"].strip().split()[:5])
                        current_section["title"] = first_words if first_words else "Untitled Section"
                    sections.append(current_section)
        except Exception as fallback_e:
            logger.error(f"Failed to process {pdf_path}: {str(fallback_e)}")
    return sections

def score_section_relevance(section_text, persona, job):
    """Simple scoring: Keyword overlap + length + position."""
    keywords = set(persona.lower().split() + job.lower().split())  # Extract keywords
    words = set(section_text.lower().split())
    overlap = len(keywords.intersection(words)) / max(len(keywords), 1)
    length_score = min(len(section_text) / 1000, 1.0)  # Normalize length
    return overlap * 0.6 + length_score * 0.4  # Weighted score

def rank_sections(all_sections, persona, job, top_n=5):
    """Rank by relevance score."""
    scored = []
    for doc, secs in all_sections.items():
        for sec in secs:
            score = score_section_relevance(sec["text"], persona, job)
            scored.append({"document": doc, "section_title": sec["title"], "importance_rank": 0, "page_number": sec["page"], "score": score, "text": sec["text"]})
    scored.sort(key=lambda x: x["score"], reverse=True)
    for i, item in enumerate(scored[:top_n], 1):
        item["importance_rank"] = i
    return [ {k: v for k, v in item.items() if k != "score" and k != "text"} for item in scored[:top_n] ], scored[:top_n]  # Return ranked + full for subsections

def main():
    input_dir = Path("/app/input") if os.path.exists("/app") else Path("./input")
    output_dir = Path("/app/output") if os.path.exists("/app") else Path("./output")
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))

    # Generalized: Find any .json file (assume exactly one)
    json_files = list(input_dir.glob("*.json"))
    if len(json_files) != 1:
        logger.error(f"Expected exactly one .json file, but found {len(json_files)}. Please ensure only one config JSON is in input.")
        return
    config_file = json_files[0]  # Take the first (and only) one
    logger.info(f"Found and loading config: {config_file.name}")

    with open(config_file, 'r') as f:
        config = json.load(f)
    persona = config.get('persona', {}).get('role', '')
    job = config.get('job_to_be_done', {}).get('task', '')

    all_sections = {}
    for pdf in pdf_files:
        all_sections[pdf.name] = extract_sections_from_pdf(pdf)

    ranked_sections, top_full = rank_sections(all_sections, persona, job)

    # Subsection analysis: Take top subsections, refine text (trim to essentials)
    subsection_analysis = []
    for item in top_full[:5]:  # Top 5
        refined = item["text"].strip()[:500] + "..." if len(item["text"]) > 500 else item["text"].strip()  # Simple refine
        subsection_analysis.append({
            "document": item["document"],
            "refined_text": refined,
            "page_number": item["page_number"]
        })

    output_data = {
        "metadata": {
            "input_documents": [f.name for f in pdf_files],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": ranked_sections,
        "subsection_analysis": subsection_analysis
    }

    output_file = output_dir / "challenge1b_output.json"
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)
    logger.info(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
