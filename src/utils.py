"""
Utility functions for the Adobe Round 1B challenge
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )

def validate_inputs(config: Dict[str, Any]) -> bool:
    """
    Validate input configuration
    
    Args:
        config: Configuration dictionary containing persona and job_to_be_done
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['persona', 'job_to_be_done']
    
    for field in required_fields:
        if field not in config:
            return False
        if not isinstance(config[field], str) or not config[field].strip():
            return False
    
    return True

def save_output(data: Dict[str, Any], output_path: Path) -> None:
    """
    Save output data to JSON file
    
    Args:
        data: Data to save
        output_path: Path to output file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving output to {output_path}: {str(e)}")
        raise

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON file safely
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {str(e)}")
        raise

def create_sample_config() -> Dict[str, Any]:
    """Create a sample configuration for testing"""
    return {
        "persona": "PhD Researcher in Computational Biology with expertise in machine learning applications to drug discovery and molecular modeling",
        "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks for graph neural networks in drug discovery"
    }

def estimate_processing_time(num_documents: int, avg_pages_per_doc: int = 10) -> float:
    """
    Estimate processing time based on document count and size
    
    Args:
        num_documents: Number of documents to process
        avg_pages_per_doc: Average pages per document
        
    Returns:
        Estimated processing time in seconds
    """
    # Rough estimates based on operations:
    # - PDF extraction: ~0.5 seconds per page
    # - Text analysis: ~0.2 seconds per page
    # - Section ranking: ~0.1 seconds per document
    
    time_per_page = 0.7  # seconds
    time_per_doc = 0.1   # seconds for ranking
    
    total_pages = num_documents * avg_pages_per_doc
    estimated_time = (total_pages * time_per_page) + (num_documents * time_per_doc)
    
    return estimated_time

def check_system_requirements() -> Dict[str, bool]:
    """
    Check if system meets requirements
    
    Returns:
        Dictionary with requirement check results
    """
    requirements = {
        'python_version': False,
        'memory_available': False,
        'dependencies': False
    }
    
    # Check Python version
    import sys
    if sys.version_info >= (3, 7):
        requirements['python_version'] = True
    
    # Check available memory (rough estimate)
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.available > 1024 * 1024 * 1024:  # 1GB available
            requirements['memory_available'] = True
    except ImportError:
        # Assume OK if psutil not available
        requirements['memory_available'] = True
    
    # Check key dependencies
    try:
        import PyPDF2
        requirements['dependencies'] = True
    except ImportError:
        try:
            import pdfplumber
            requirements['dependencies'] = True
        except ImportError:
            requirements['dependencies'] = False
    
    return requirements

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized

def create_directory_structure(base_path: Path) -> None:
    """Create necessary directory structure"""
    directories = [
        base_path / "input",
        base_path / "output",
        base_path / "logs",
        base_path / "temp"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def cleanup_temp_files(temp_dir: Path) -> None:
    """Clean up temporary files"""
    if temp_dir.exists():
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logging.warning(f"Could not clean up temp directory {temp_dir}: {str(e)}")
