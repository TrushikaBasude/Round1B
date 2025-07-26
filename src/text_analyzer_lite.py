"""
Lightweight Text Analysis Module
Fast, efficient text processing without heavy ML dependencies
"""

import logging
import re
from typing import Dict, List, Any
from collections import Counter

class LightweightTextAnalyzer:
    """Fast text analysis using simple keyword matching and scoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Domain-specific keywords for relevance scoring
        self.keyword_categories = {
            'planning': ['plan', 'organize', 'schedule', 'arrange', 'prepare', 'itinerary', 'logistics'],
            'travel': ['trip', 'travel', 'visit', 'tour', 'destination', 'journey', 'vacation', 'explore'],
            'activities': ['activity', 'experience', 'attraction', 'adventure', 'things', 'do', 'see'],
            'food': ['food', 'restaurant', 'cuisine', 'dining', 'eat', 'meal', 'cafe', 'bar', 'culinary'],
            'culture': ['culture', 'history', 'tradition', 'heritage', 'festival', 'art', 'museum'],
            'accommodation': ['hotel', 'stay', 'accommodation', 'lodging', 'room', 'guest', 'booking'],
            'budget': ['budget', 'cheap', 'affordable', 'student', 'cost', 'price', 'money', 'value'],
            'group': ['group', 'friends', 'together', 'social', 'party', 'team', 'collective']
        }
        
        # Stop words to filter out
        self.stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'may', 'might'
        }
    
    def analyze_documents(self, documents: List[Dict[str, Any]], 
                         persona: str, job_to_be_done: str) -> List[Dict[str, Any]]:
        """Analyze documents with lightweight processing"""
        analyzed_docs = []
        
        for doc in documents:
            try:
                analyzed_doc = self._analyze_single_document(doc, persona, job_to_be_done)
                analyzed_docs.append(analyzed_doc)
            except Exception as e:
                self.logger.error(f"Error analyzing document {doc.get('filename', 'unknown')}: {str(e)}")
                continue
        
        return analyzed_docs
    
    def _analyze_single_document(self, document: Dict[str, Any], 
                                persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Analyze single document with fast keyword-based scoring"""
        analyzed_doc = document.copy()
        
        # Simple document type classification
        analyzed_doc['document_features'] = self._classify_document_type(document)
        
        # Analyze sections with lightweight scoring
        analyzed_sections = []
        for section in document.get('sections', []):
            analyzed_section = self._analyze_section_fast(section, persona, job_to_be_done)
            analyzed_sections.append(analyzed_section)
        
        analyzed_doc['analyzed_sections'] = analyzed_sections
        return analyzed_doc
    
    def _analyze_section_fast(self, section: Dict[str, Any], 
                             persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Fast section analysis using keyword matching"""
        analyzed_section = section.copy()
        
        content = section.get('content', '').lower()
        title = section.get('title', '').lower()
        combined_text = f"{title} {content}"
        
        # Fast keyword extraction
        analyzed_section['keywords'] = self._extract_keywords_fast(combined_text)
        
        # Quick relevance scoring based on keyword matching
        persona_score = self._calculate_keyword_relevance(combined_text, persona.lower())
        job_score = self._calculate_keyword_relevance(combined_text, job_to_be_done.lower())
        
        analyzed_section['persona_relevance'] = persona_score
        analyzed_section['job_relevance'] = job_score
        analyzed_section['combined_relevance'] = (persona_score * 0.4 + job_score * 0.6)
        
        # Extract meaningful subsections (simplified)
        analyzed_section['subsections'] = self._extract_subsections_fast(content)
        
        return analyzed_section
    
    def _extract_keywords_fast(self, text: str, max_keywords: int = 8) -> List[str]:
        """Fast keyword extraction using word frequency"""
        if not text:
            return []
        
        # Extract words (3+ characters, alphabetic only)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words and count frequency
        filtered_words = [word for word in words if word not in self.stop_words]
        word_freq = Counter(filtered_words)
        
        # Return most frequent words
        return [word for word, _ in word_freq.most_common(max_keywords)]
    
    def _calculate_keyword_relevance(self, text: str, reference_text: str) -> float:
        """Calculate relevance using keyword matching and category scoring"""
        if not text or not reference_text:
            return 0.0
        
        # Basic word overlap scoring
        text_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
        ref_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', reference_text.lower()))
        
        if not text_words or not ref_words:
            return 0.0
        
        # Calculate word overlap
        overlap = len(text_words.intersection(ref_words))
        base_score = overlap / max(len(text_words), len(ref_words))
        
        # Boost score based on category keywords
        category_boost = 0.0
        for category, keywords in self.keyword_categories.items():
            category_matches = sum(1 for kw in keywords if kw in text)
            if category_matches > 0:
                category_boost += category_matches * 0.1
        
        return min(base_score + category_boost, 1.0)
    
    def _classify_document_type(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Simple document type classification"""
        filename = document.get('filename', '').lower()
        
        if any(word in filename for word in ['restaurant', 'hotel', 'accommodation']):
            doc_type = 'accommodation'
        elif any(word in filename for word in ['cuisine', 'food', 'dining']):
            doc_type = 'food'
        elif any(word in filename for word in ['things', 'activities', 'do']):
            doc_type = 'activities'
        elif any(word in filename for word in ['history', 'culture', 'tradition']):
            doc_type = 'culture'
        elif any(word in filename for word in ['cities', 'places', 'destinations']):
            doc_type = 'destinations'
        elif any(word in filename for word in ['tips', 'tricks', 'guide']):
            doc_type = 'guide'
        else:
            doc_type = 'general'
        
        return {
            'document_type': doc_type,
            'classification_confidence': 0.8
        }
    
    def _extract_subsections_fast(self, content: str) -> List[Dict[str, Any]]:
        """Fast subsection extraction using simple text patterns"""
        if not content:
            return []
        
        subsections = []
        sentences = re.split(r'[.!?]+', content)
        
        # Take only meaningful sentences (10+ words) as subsections
        for i, sentence in enumerate(sentences[:10]):  # Limit to 10 subsections
            sentence = sentence.strip()
            if len(sentence.split()) >= 10:  # At least 10 words
                subsections.append({
                    'content': sentence,
                    'position': i,
                    'word_count': len(sentence.split())
                })
        
        return subsections[:5]  # Limit to top 5 subsections