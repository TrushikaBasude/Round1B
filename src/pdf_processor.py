"""
PDF Processing Module
Handles PDF text extraction and initial document structure analysis
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    PyPDF2 = None
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    pdfplumber = None
    HAS_PDFPLUMBER = False

class PDFProcessor:
    """Handles PDF text extraction and preprocessing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Check available PDF libraries
        if not HAS_PYPDF2 and not HAS_PDFPLUMBER:
            raise ImportError("No PDF processing library available. Install PyPDF2 or pdfplumber.")
        
        self.use_pdfplumber = HAS_PDFPLUMBER
        
    def process_pdf(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single PDF file and extract structured content
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing document structure and content
        """
        try:
            if self.use_pdfplumber:
                return self._extract_with_pdfplumber(pdf_path)
            else:
                return self._extract_with_pypdf2(pdf_path)
                
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return None
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text using pdfplumber"""
        if not HAS_PDFPLUMBER:
            raise ImportError("pdfplumber is not available")
            
        document_data = {
            'filename': pdf_path.name,
            'pages': [],
            'full_text': '',
            'sections': []
        }
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        page_data = {
                            'page_number': page_num,
                            'text': text.strip(),
                            'sections': self._identify_sections(text, page_num)
                        }
                        document_data['pages'].append(page_data)
                        document_data['full_text'] += f"\n[Page {page_num}]\n{text}"
                        document_data['sections'].extend(page_data['sections'])
                        
                except Exception as e:
                    self.logger.warning(f"Error extracting page {page_num}: {str(e)}")
                    continue
        
        return document_data
    
    def _extract_with_pypdf2(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text using PyPDF2"""
        if not HAS_PYPDF2:
            raise ImportError("PyPDF2 is not available")
            
        document_data = {
            'filename': pdf_path.name,
            'pages': [],
            'full_text': '',
            'sections': []
        }
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        page_data = {
                            'page_number': page_num,
                            'text': text.strip(),
                            'sections': self._identify_sections(text, page_num)
                        }
                        document_data['pages'].append(page_data)
                        document_data['full_text'] += f"\n[Page {page_num}]\n{text}"
                        document_data['sections'].extend(page_data['sections'])
                        
                except Exception as e:
                    self.logger.warning(f"Error extracting page {page_num}: {str(e)}")
                    continue
        
        return document_data
    
    def _identify_sections(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Identify sections within a page based on text patterns
        
        Args:
            text: Page text content
            page_num: Page number
            
        Returns:
            List of identified sections
        """
        sections = []
        lines = text.split('\n')
        
        # Patterns for identifying headings/sections
        heading_patterns = [
            r'^[A-Z][A-Za-z\s]{10,}$',  # All caps or title case lines
            r'^\d+\.\s+[A-Z]',  # Numbered sections
            r'^[A-Z][a-z]+:',   # Section labels with colons
            r'^[IVX]+\.\s+',    # Roman numerals
            r'^\w+\s+\d+',      # Chapter/Section numbers
            r'^Abstract$|^Introduction$|^Conclusion$|^References$|^Methods$|^Results$|^Discussion$',  # Common academic sections
        ]
        
        current_section = None
        section_text = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches heading patterns
            is_heading = any(re.match(pattern, line, re.IGNORECASE) for pattern in heading_patterns)
            
            # Additional heuristics for headings
            if not is_heading:
                # Check for short lines that might be headings
                if len(line) < 100 and i < len(lines) - 1:
                    next_line = lines[i + 1].strip()
                    if next_line and len(next_line) > 50:
                        is_heading = True
            
            if is_heading:
                # Save previous section
                if current_section and section_text:
                    current_section['content'] = '\n'.join(section_text).strip()
                    if len(current_section['content']) > 50:  # Only save substantial sections
                        sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': line,
                    'page': page_num,
                    'content': '',
                    'start_line': i
                }
                section_text = []
            else:
                # Add to current section
                if current_section:
                    section_text.append(line)
                else:
                    # Create a default section for content without explicit heading
                    if not sections:
                        current_section = {
                            'title': 'Document Content',
                            'page': page_num,
                            'content': '',
                            'start_line': 0
                        }
                        section_text = [line]
        
        # Save the last section
        if current_section and section_text:
            current_section['content'] = '\n'.join(section_text).strip()
            if len(current_section['content']) > 50:
                sections.append(current_section)
        
        return sections
    
    def extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata if available"""
        metadata = {}
        
        try:
            if self.use_pdfplumber and HAS_PDFPLUMBER:
                with pdfplumber.open(pdf_path) as pdf:
                    if hasattr(pdf, 'metadata') and pdf.metadata:
                        metadata = dict(pdf.metadata)
            elif HAS_PYPDF2:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    if pdf_reader.metadata:
                        metadata = dict(pdf_reader.metadata)
                        
        except Exception as e:
            self.logger.warning(f"Could not extract metadata from {pdf_path}: {str(e)}")
        
        return metadata
