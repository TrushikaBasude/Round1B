"""
Section Ranking Module
Handles ranking and prioritization of document sections based on relevance
"""

import logging
from typing import Dict, List, Any, Tuple
from operator import itemgetter

class SectionRanker:
    """Handles section ranking and prioritization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def rank_sections(self, analyzed_documents: List[Dict[str, Any]], 
                     persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """
        Rank all sections across documents based on relevance
        
        Args:
            analyzed_documents: List of analyzed document data
            persona: User persona description
            job_to_be_done: Task description
            
        Returns:
            Dictionary containing ranked sections and subsections
        """
        try:
            # Collect all sections with additional scoring
            all_sections = []
            all_subsections = []
            
            for doc in analyzed_documents:
                filename = doc.get('filename', 'unknown')
                doc_type = doc.get('document_features', {}).get('document_type', 'general')
                
                for section in doc.get('analyzed_sections', []):
                    # Enhanced section scoring
                    enhanced_section = self._enhance_section_scoring(
                        section, filename, doc_type, persona, job_to_be_done
                    )
                    all_sections.append(enhanced_section)
                    
                    # Process subsections
                    for subsection in section.get('subsections', []):
                        enhanced_subsection = self._enhance_subsection_scoring(
                            subsection, section, filename, doc_type, persona, job_to_be_done
                        )
                        all_subsections.append(enhanced_subsection)
            
            # Rank sections
            ranked_sections = self._rank_and_format_sections(all_sections)
            
            # Rank subsections
            ranked_subsections = self._rank_and_format_subsections(all_subsections)
            
            return {
                'sections': ranked_sections,
                'subsections': ranked_subsections
            }
            
        except Exception as e:
            self.logger.error(f"Error in section ranking: {str(e)}")
            return {'sections': [], 'subsections': []}
    
    def _enhance_section_scoring(self, section: Dict[str, Any], filename: str, 
                                doc_type: str, persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Enhance section with additional scoring factors"""
        enhanced = section.copy()
        
        # Base relevance score
        base_score = section.get('combined_relevance', 0.0)
        
        # Additional scoring factors
        title_bonus = self._calculate_title_relevance(section.get('title', ''), persona, job_to_be_done)
        length_factor = self._calculate_length_factor(section.get('content', ''))
        position_factor = self._calculate_position_factor(section.get('page', 1))
        entity_bonus = self._calculate_entity_relevance(section.get('entities', []), persona, job_to_be_done)
        
        # Document type bonus
        doc_type_bonus = self._calculate_document_type_bonus(doc_type, persona)
        
        # Calculate final importance rank
        final_score = (
            base_score * 0.4 +
            title_bonus * 0.2 +
            length_factor * 0.1 +
            position_factor * 0.1 +
            entity_bonus * 0.1 +
            doc_type_bonus * 0.1
        )
        
        enhanced.update({
            'document': filename,
            'final_score': final_score,
            'scoring_details': {
                'base_score': base_score,
                'title_bonus': title_bonus,
                'length_factor': length_factor,
                'position_factor': position_factor,
                'entity_bonus': entity_bonus,
                'doc_type_bonus': doc_type_bonus
            }
        })
        
        return enhanced
    
    def _enhance_subsection_scoring(self, subsection: Dict[str, Any], parent_section: Dict[str, Any],
                                   filename: str, doc_type: str, persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Enhance subsection with scoring"""
        enhanced = subsection.copy()
        
        # Inherit some scoring from parent section
        parent_score = parent_section.get('combined_relevance', 0.0) * 0.3
        
        # Calculate subsection-specific relevance
        text = subsection.get('text', '')
        from .text_analyzer import TextAnalyzer
        analyzer = TextAnalyzer()
        
        persona_relevance = analyzer._calculate_relevance(text, persona)
        job_relevance = analyzer._calculate_relevance(text, job_to_be_done)
        
        subsection_score = (persona_relevance * 0.4 + job_relevance * 0.6) * 0.7
        
        final_score = parent_score + subsection_score
        
        enhanced.update({
            'document': filename,
            'section_title': parent_section.get('title', ''),
            'page_number': parent_section.get('page', 1),
            'final_score': final_score,
            'relevance_score': subsection_score
        })
        
        return enhanced
    
    def _calculate_title_relevance(self, title: str, persona: str, job_to_be_done: str) -> float:
        """Calculate relevance bonus based on section title"""
        if not title:
            return 0.0
        
        title_lower = title.lower()
        persona_lower = persona.lower()
        job_lower = job_to_be_done.lower()
        
        # Look for key terms in title
        persona_words = set(persona_lower.split())
        job_words = set(job_lower.split())
        title_words = set(title_lower.split())
        
        persona_overlap = len(persona_words.intersection(title_words)) / max(len(persona_words), 1)
        job_overlap = len(job_words.intersection(title_words)) / max(len(job_words), 1)
        
        return (persona_overlap * 0.4 + job_overlap * 0.6) * 0.5
    
    def _calculate_length_factor(self, content: str) -> float:
        """Calculate factor based on content length (optimal length gets higher score)"""
        if not content:
            return 0.0
        
        length = len(content)
        
        # Optimal length range: 200-2000 characters
        if 200 <= length <= 2000:
            return 1.0
        elif length < 200:
            return length / 200.0
        else:
            # Diminishing returns for very long sections
            return max(0.5, 2000 / length)
    
    def _calculate_position_factor(self, page_num: int) -> float:
        """Calculate factor based on section position (earlier sections get slight bonus)"""
        # First few pages get slight bonus
        if page_num <= 3:
            return 1.0
        elif page_num <= 10:
            return 0.9
        else:
            return 0.8
    
    def _calculate_entity_relevance(self, entities: List[Dict[str, str]], 
                                   persona: str, job_to_be_done: str) -> float:
        """Calculate relevance bonus based on named entities"""
        if not entities:
            return 0.0
        
        # Check if entities are relevant to persona or job
        relevant_count = 0
        persona_lower = persona.lower()
        job_lower = job_to_be_done.lower()
        
        for entity in entities:
            entity_text = entity.get('text', '').lower()
            if entity_text in persona_lower or entity_text in job_lower:
                relevant_count += 1
        
        return min(1.0, relevant_count / 3.0)  # Cap at 1.0, normalize by expected count
    
    def _calculate_document_type_bonus(self, doc_type: str, persona: str) -> float:
        """Calculate bonus based on document type alignment with persona"""
        persona_lower = persona.lower()
        
        # Define type-persona alignments
        alignments = {
            'research': ['researcher', 'scientist', 'academic', 'phd', 'analyst'],
            'business': ['analyst', 'manager', 'executive', 'investor', 'consultant'],
            'educational': ['student', 'teacher', 'learner', 'undergraduate']
        }
        
        relevant_terms = alignments.get(doc_type, [])
        for term in relevant_terms:
            if term in persona_lower:
                return 0.2
        
        return 0.0
    
    def _rank_and_format_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank and format sections for output"""
        # Sort by final score (descending)
        sorted_sections = sorted(sections, key=lambda x: x.get('final_score', 0), reverse=True)
        
        # Format for output and assign importance ranks
        formatted_sections = []
        for i, section in enumerate(sorted_sections[:20]):  # Top 20 sections
            formatted = {
                'document': section.get('document', ''),
                'page_number': section.get('page', 1),
                'section_title': section.get('title', ''),
                'importance_rank': i + 1,
                'relevance_score': round(section.get('final_score', 0), 3),
                'content_preview': self._create_content_preview(section.get('content', ''))
            }
            formatted_sections.append(formatted)
        
        return formatted_sections
    
    def _rank_and_format_subsections(self, subsections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank and format subsections for output"""
        # Sort by final score (descending)
        sorted_subsections = sorted(subsections, key=lambda x: x.get('final_score', 0), reverse=True)
        
        # Format for output
        formatted_subsections = []
        for i, subsection in enumerate(sorted_subsections[:30]):  # Top 30 subsections
            formatted = {
                'document': subsection.get('document', ''),
                'section_title': subsection.get('section_title', ''),
                'refined_text': subsection.get('refined_text', ''),
                'page_number': subsection.get('page_number', 1),
                'importance_rank': i + 1,
                'relevance_score': round(subsection.get('final_score', 0), 3)
            }
            formatted_subsections.append(formatted)
        
        return formatted_subsections
    
    def _create_content_preview(self, content: str, max_length: int = 200) -> str:
        """Create a preview of the content"""
        if not content:
            return ""
        
        if len(content) <= max_length:
            return content
        
        # Find a good breaking point (end of sentence)
        truncated = content[:max_length]
        last_period = truncated.rfind('.')
        last_space = truncated.rfind(' ')
        
        if last_period > max_length * 0.7:  # If period is reasonably close to end
            return content[:last_period + 1] + "..."
        elif last_space > max_length * 0.8:  # If space is close to end
            return content[:last_space] + "..."
        else:
            return truncated + "..."
