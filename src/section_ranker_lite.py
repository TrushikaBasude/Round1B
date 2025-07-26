"""
Lightweight Section Ranking Module
Fast ranking with concise output optimized for Adobe challenge
"""

import logging
import re
from typing import Dict, List, Any
from operator import itemgetter

class LightweightSectionRanker:
    """Fast section ranking with concise output"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Optimized limits for generalized, accurate output (~150-200 lines total)
        self.max_sections = 10  # Focus on most relevant sections
        self.max_subsections = 12  # Streamlined subsection analysis
    
    def rank_sections(self, analyzed_documents: List[Dict[str, Any]], 
                     persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Rank sections with optimized, concise output"""
        try:
            all_sections = []
            all_subsections = []
            
            # Collect and score sections
            for doc in analyzed_documents:
                filename = doc.get('filename', 'unknown')
                doc_type = doc.get('document_features', {}).get('document_type', 'general')
                
                for section in doc.get('analyzed_sections', []):
                    # Enhanced section scoring
                    enhanced_section = self._score_section_optimized(
                        section, filename, doc_type, persona, job_to_be_done
                    )
                    all_sections.append(enhanced_section)
                    
                    # Process only high-quality subsections
                    for subsection in section.get('subsections', [])[:2]:  # Max 2 per section
                        if subsection.get('word_count', 0) >= 15:  # Quality filter
                            enhanced_subsection = self._score_subsection_optimized(
                                subsection, section, filename, doc_type
                            )
                            all_subsections.append(enhanced_subsection)
            
            # Rank and format with size limits
            ranked_sections = self._rank_and_format_sections_optimized(all_sections)
            ranked_subsections = self._rank_and_format_subsections_optimized(all_subsections)
            
            return {
                'sections': ranked_sections[:self.max_sections],
                'subsections': ranked_subsections[:self.max_subsections]
            }
            
        except Exception as e:
            self.logger.error(f"Error in section ranking: {str(e)}")
            return {'sections': [], 'subsections': []}
    
    def _score_section_optimized(self, section: Dict[str, Any], filename: str, 
                                doc_type: str, persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Optimized section scoring for speed and accuracy"""
        enhanced = section.copy()
        
        # Base relevance score
        base_score = section.get('combined_relevance', 0.0)
        
        # Document type boost (reward relevant document types)
        doc_type_boost = self._get_document_type_boost(doc_type, job_to_be_done)
        
        # Position boost (earlier sections often more important)
        position = section.get('position', 0)
        position_boost = max(0, (10 - position) * 0.02)  # Diminishing boost for later sections
        
        # Content length normalization (prefer substantial but not overly long content)
        content_length = len(section.get('content', ''))
        length_score = min(content_length / 500, 1.0) if content_length > 50 else 0.1
        
        # Final score calculation
        final_score = (base_score * 0.7 + 
                      doc_type_boost * 0.2 + 
                      position_boost * 0.05 + 
                      length_score * 0.05)
        
        enhanced.update({
            'final_relevance_score': round(final_score, 3),
            'document': filename,
            'page_number': section.get('page_number', 1),
            'section_title': self._clean_title(section.get('title', 'Untitled Section')),
            'content_preview': self._create_preview(section.get('content', ''))
        })
        
        return enhanced
    
    def _score_subsection_optimized(self, subsection: Dict[str, Any], parent_section: Dict[str, Any], 
                                   filename: str, doc_type: str) -> Dict[str, Any]:
        """Optimized subsection scoring"""
        content = subsection.get('content', '')
        
        # Inherit some relevance from parent section
        parent_relevance = parent_section.get('combined_relevance', 0.0)
        
        # Simple content quality scoring
        word_count = subsection.get('word_count', 0)
        quality_score = min(word_count / 20, 1.0) if word_count > 5 else 0.1
        
        return {
            'document': filename,
            'section_title': self._clean_title(parent_section.get('title', 'Section')),
            'refined_text': self._clean_content(content),
            'page_number': parent_section.get('page_number', 1),
            'relevance_score': round(parent_relevance * quality_score, 3)
        }
    
    def _get_document_type_boost(self, doc_type: str, job_to_be_done: str) -> float:
        """Universal document type relevance calculation"""
        job_lower = job_to_be_done.lower()
        
        # Universal patterns work across all domains
        type_boosts = {
            'instructional': 0.25 if any(word in job_lower for word in ['plan', 'organize', 'create', 'build']) else 0.1,
            'comprehensive': 0.3 if any(word in job_lower for word in ['comprehensive', 'complete', 'detailed']) else 0.15,
            'reference': 0.2 if any(word in job_lower for word in ['find', 'choose', 'select', 'options']) else 0.1,
            'overview': 0.15 if any(word in job_lower for word in ['understand', 'learn', 'overview']) else 0.1,
            'informational': 0.2
        }
        
        return type_boosts.get(doc_type, 0.15)
    
    def _rank_and_format_sections_optimized(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank sections with optimized output format"""
        # Sort by final relevance score
        sorted_sections = sorted(sections, key=lambda x: x.get('final_relevance_score', 0), reverse=True)
        
        # Format for output with minimal fields
        formatted_sections = []
        for i, section in enumerate(sorted_sections, 1):
            formatted_section = {
                'document': section.get('document', 'unknown'),
                'page_number': section.get('page_number', 1),
                'section_title': section.get('section_title', 'Untitled'),
                'importance_rank': i,
                'relevance_score': section.get('final_relevance_score', 0.0),
                'content_preview': section.get('content_preview', '')
            }
            formatted_sections.append(formatted_section)
        
        return formatted_sections
    
    def _rank_and_format_subsections_optimized(self, subsections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank subsections with optimized output format"""
        # Sort by relevance score
        sorted_subsections = sorted(subsections, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Format for output
        formatted_subsections = []
        for i, subsection in enumerate(sorted_subsections, 1):
            formatted_subsection = {
                'document': subsection.get('document', 'unknown'),
                'section_title': subsection.get('section_title', 'Section'),
                'refined_text': subsection.get('refined_text', ''),
                'page_number': subsection.get('page_number', 1),
                'importance_rank': i,
                'relevance_score': subsection.get('relevance_score', 0.0)
            }
            formatted_subsections.append(formatted_subsection)
        
        return formatted_subsections
    
    def _clean_title(self, title: str) -> str:
        """Clean and shorten section titles"""
        if not title:
            return "Untitled Section"
        
        # Remove common prefixes and clean
        cleaned = re.sub(r'^(section|chapter|part)\s*\d*:?\s*', '', title.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Limit length
        return cleaned[:100] + "..." if len(cleaned) > 100 else cleaned
    
    def _create_preview(self, content: str, max_length: int = 120) -> str:
        """Create concise content preview"""
        if not content:
            return ""
        
        # Clean and truncate
        cleaned = re.sub(r'\s+', ' ', content.strip())
        return cleaned[:max_length] + "..." if len(cleaned) > max_length else cleaned
    
    def _clean_content(self, content: str, max_length: int = 150) -> str:
        """Clean and limit subsection content"""
        if not content:
            return ""
        
        # Clean whitespace and limit length
        cleaned = re.sub(r'\s+', ' ', content.strip())
        return cleaned[:max_length] + "..." if len(cleaned) > max_length else cleaned