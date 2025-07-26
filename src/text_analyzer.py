"""
Text Analysis Module
Handles NLP processing, semantic analysis, and content understanding
"""

import logging
import re
from typing import Dict, List, Any, Tuple
from collections import Counter

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except (ImportError, OSError):
    nlp = None
    spacy = None
    HAS_SPACY = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None
    HAS_SKLEARN = False

import numpy as np

class TextAnalyzer:
    """Handles text analysis and semantic processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize TF-IDF vectorizer
        if HAS_SKLEARN and TfidfVectorizer:
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
        else:
            self.vectorizer = None
            
        self.use_spacy = HAS_SPACY
        
    def analyze_documents(self, documents: List[Dict[str, Any]], 
                         persona: str, job_to_be_done: str) -> List[Dict[str, Any]]:
        """
        Analyze documents and extract semantic features
        
        Args:
            documents: List of processed document data
            persona: User persona description
            job_to_be_done: Task description
            
        Returns:
            List of analyzed documents with enhanced features
        """
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
        """Analyze a single document"""
        analyzed_doc = document.copy()
        
        # Analyze each section
        analyzed_sections = []
        for section in document.get('sections', []):
            analyzed_section = self._analyze_section(section, persona, job_to_be_done)
            analyzed_sections.append(analyzed_section)
        
        analyzed_doc['analyzed_sections'] = analyzed_sections
        
        # Extract document-level features
        analyzed_doc['document_features'] = self._extract_document_features(document)
        
        return analyzed_doc
    
    def _analyze_section(self, section: Dict[str, Any], 
                        persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Analyze a single section"""
        analyzed_section = section.copy()
        
        content = section.get('content', '')
        title = section.get('title', '')
        
        # Extract keywords and entities
        analyzed_section['keywords'] = self._extract_keywords(content)
        analyzed_section['entities'] = self._extract_entities(content)
        
        # Calculate relevance scores
        analyzed_section['persona_relevance'] = self._calculate_relevance(
            content + " " + title, persona
        )
        analyzed_section['job_relevance'] = self._calculate_relevance(
            content + " " + title, job_to_be_done
        )
        
        # Combined relevance score
        analyzed_section['combined_relevance'] = (
            analyzed_section['persona_relevance'] * 0.4 +
            analyzed_section['job_relevance'] * 0.6
        )
        
        # Extract subsections
        analyzed_section['subsections'] = self._extract_subsections(content)
        
        return analyzed_section
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        if self.use_spacy and nlp is not None:
            try:
                doc = nlp(cleaned_text)
                # Extract meaningful tokens (nouns, adjectives, proper nouns)
                keywords = [
                    token.lemma_.lower() for token in doc
                    if token.pos_ in ['NOUN', 'ADJ', 'PROPN'] 
                    and len(token.text) > 2
                    and not token.is_stop
                    and token.is_alpha
                ]
                return list(dict.fromkeys(keywords))[:max_keywords]  # Remove duplicates, preserve order
            except Exception as e:
                self.logger.warning(f"Error in spaCy keyword extraction: {str(e)}")
        
        # Fallback: simple word frequency
        words = re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_text.lower())
        word_freq = Counter(words)
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word, freq in word_freq.most_common(max_keywords * 2) 
                   if word not in stop_words]
        
        return keywords[:max_keywords]
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text"""
        entities = []
        
        if self.use_spacy and text and nlp is not None and HAS_SPACY:
            try:
                doc = nlp(text)
                for ent in doc.ents:
                    # Get entity description safely
                    try:
                        import spacy
                        description = spacy.explain(ent.label_) if hasattr(spacy, 'explain') else ent.label_
                    except:
                        description = ent.label_
                    
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'description': description
                    })
            except Exception as e:
                self.logger.warning(f"Error in entity extraction: {str(e)}")
        
        return entities
    
    def _calculate_relevance(self, text: str, reference_text: str) -> float:
        """Calculate semantic relevance between text and reference"""
        if not text or not reference_text:
            return 0.0
        
        try:
            if self.vectorizer and HAS_SKLEARN and TfidfVectorizer and cosine_similarity:
                # Use TF-IDF similarity
                texts = [self._clean_text(text), self._clean_text(reference_text)]
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            else:
                # Fallback: simple word overlap
                return self._calculate_word_overlap(text, reference_text)
                
        except Exception as e:
            self.logger.warning(f"Error calculating relevance: {str(e)}")
            return self._calculate_word_overlap(text, reference_text)
    
    def _calculate_word_overlap(self, text1: str, text2: str) -> float:
        """Calculate simple word overlap similarity"""
        words1 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower()))
        words2 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_subsections(self, content: str) -> List[Dict[str, Any]]:
        """Extract meaningful subsections from content"""
        if not content:
            return []
        
        # Split by paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        subsections = []
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 100:  # Only consider substantial paragraphs
                subsection = {
                    'id': i,
                    'text': paragraph,
                    'refined_text': self._refine_text(paragraph),
                    'length': len(paragraph),
                    'keywords': self._extract_keywords(paragraph, max_keywords=5)
                }
                subsections.append(subsection)
        
        return subsections
    
    def _refine_text(self, text: str) -> str:
        """Refine and clean text for better readability"""
        # Remove extra whitespace
        refined = re.sub(r'\s+', ' ', text).strip()
        
        # Fix common OCR errors
        refined = re.sub(r'(\w)- (\w)', r'\1\2', refined)  # Remove hyphenation
        refined = re.sub(r'\s+([.,;:!?])', r'\1', refined)  # Fix punctuation spacing
        
        return refined
    
    def _clean_text(self, text: str) -> str:
        """Clean text for processing"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s.,;:!?()-]', ' ', cleaned)
        
        return cleaned
    
    def _extract_document_features(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document-level features"""
        features = {
            'total_sections': len(document.get('sections', [])),
            'total_pages': len(document.get('pages', [])),
            'avg_section_length': 0,
            'document_type': self._classify_document_type(document)
        }
        
        # Calculate average section length
        sections = document.get('sections', [])
        if sections:
            total_length = sum(len(s.get('content', '')) for s in sections)
            features['avg_section_length'] = total_length / len(sections)
        
        return features
    
    def _classify_document_type(self, document: Dict[str, Any]) -> str:
        """Classify document type based on content patterns"""
        full_text = document.get('full_text', '').lower()
        
        # Research paper indicators
        research_indicators = ['abstract', 'methodology', 'results', 'conclusion', 'references', 'citation']
        research_score = sum(1 for indicator in research_indicators if indicator in full_text)
        
        # Business report indicators
        business_indicators = ['revenue', 'profit', 'quarterly', 'annual', 'financial', 'market']
        business_score = sum(1 for indicator in business_indicators if indicator in full_text)
        
        # Educational content indicators
        education_indicators = ['chapter', 'exercise', 'example', 'definition', 'theorem', 'practice']
        education_score = sum(1 for indicator in education_indicators if indicator in full_text)
        
        # Determine document type
        max_score = max(research_score, business_score, education_score)
        if max_score == 0:
            return 'general'
        elif max_score == research_score:
            return 'research'
        elif max_score == business_score:
            return 'business'
        else:
            return 'educational'
