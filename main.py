#!/usr/bin/env python3
"""
Adobe Round 1B Challenge: Persona-Driven Document Intelligence
Main entry point for processing PDF documents based on persona and job requirements
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.pdf_processor import PDFProcessor
from src.text_analyzer_lite import LightweightTextAnalyzer
from src.section_ranker_lite import LightweightSectionRanker
from src.utils import setup_logging, validate_inputs, save_output

def main():
    """Main processing function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Define input/output directories - handle both Docker and local environments
    if os.path.exists("/app"):
        input_dir = Path("/app/input")
        output_dir = Path("/app/output")
    else:
        # Local development environment
        input_dir = Path("./input")
        output_dir = Path("./output")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info("Starting Adobe Round 1B Document Intelligence Processing")
        start_time = time.time()
        
        # Initialize lightweight components for faster processing
        pdf_processor = PDFProcessor()
        text_analyzer = LightweightTextAnalyzer()
        section_ranker = LightweightSectionRanker()
        
        # Check for input files
        if not input_dir.exists():
            logger.error(f"Input directory {input_dir} does not exist")
            return
        
        # Look for PDF files and configuration
        pdf_files = list(input_dir.glob("*.pdf"))
        config_file = input_dir / "config.json"
        
        if not pdf_files:
            logger.error("No PDF files found in input directory")
            return
        
        if not config_file.exists():
            logger.error("config.json not found in input directory")
            return
        
        # Load configuration (persona and job-to-be-done)
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validate configuration
        if not validate_inputs(config):
            logger.error("Invalid configuration format")
            return
        
        persona = config.get('persona', '')
        job_to_be_done = config.get('job_to_be_done', '')
        
        logger.info(f"Processing {len(pdf_files)} PDF files")
        logger.info(f"Persona: {persona}")
        logger.info(f"Job: {job_to_be_done}")
        
        # Process all PDF documents
        all_documents = []
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            try:
                document_data = pdf_processor.process_pdf(pdf_file)
                if document_data:
                    all_documents.append(document_data)
                    logger.info(f"Successfully processed {pdf_file.name}")
                else:
                    logger.warning(f"Failed to process {pdf_file.name}")
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
                continue
        
        if not all_documents:
            logger.error("No documents were successfully processed")
            return
        
        # Analyze text and extract semantic features
        logger.info("Analyzing document content")
        analyzed_docs = text_analyzer.analyze_documents(all_documents, persona, job_to_be_done)
        
        # Rank sections based on relevance
        logger.info("Ranking sections by relevance")
        ranked_results = section_ranker.rank_sections(analyzed_docs, persona, job_to_be_done)
        
        # Prepare output
        processing_time = time.time() - start_time
        output_data = {
            "metadata": {
                "input_documents": [doc['filename'] for doc in all_documents],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": round(processing_time, 2),
                "total_documents": len(all_documents)
            },
            "extracted_sections": ranked_results["sections"],
            "subsection_analysis": ranked_results["subsections"]
        }
        
        # Save output
        output_file = output_dir / "challenge1b_output.json"
        save_output(output_data, output_file)
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        logger.info(f"Output saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Fatal error in main processing: {str(e)}")
        raise

if __name__ == "__main__":
    main()
