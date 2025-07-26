# Adobe Round 1B: Persona-Driven Document Intelligence
## Approach Explanation

### Overview
Our solution implements a multi-stage pipeline that processes PDF documents and extracts the most relevant sections based on a specific persona and their job-to-be-done. The system combines traditional NLP techniques with semantic analysis to rank content by relevance.

### Architecture

#### 1. PDF Processing (`pdf_processor.py`)
- **Text Extraction**: Uses pdfplumber (primary) or PyPDF2 (fallback) for robust text extraction
- **Section Identification**: Employs pattern matching and heuristics to identify document structure
- **Content Segmentation**: Breaks documents into logical sections with titles and content

#### 2. Text Analysis (`text_analyzer.py`)
- **Keyword Extraction**: Uses spaCy for linguistic analysis and TF-IDF for importance scoring
- **Named Entity Recognition**: Identifies key entities that might be relevant to personas
- **Semantic Similarity**: Calculates relevance scores using TF-IDF cosine similarity
- **Document Classification**: Automatically classifies documents as research, business, or educational

#### 3. Section Ranking (`section_ranker.py`)
- **Multi-factor Scoring**: Combines relevance, position, length, and entity factors
- **Persona Alignment**: Matches document types with persona characteristics
- **Hierarchical Ranking**: Ranks both sections and subsections independently
- **Importance Prioritization**: Generates final ranked lists with confidence scores

### Key Features

#### Robust PDF Processing
- Handles various PDF formats and structures
- Fallback mechanisms for different text extraction libraries
- OCR error correction and text cleaning

#### Intelligent Section Detection
- Pattern-based heading identification
- Content-aware section boundaries
- Adaptive to different document styles

#### Semantic Understanding
- Context-aware relevance scoring
- Multi-dimensional similarity calculations
- Entity-based relevance boosting

#### Scalable Architecture
- Modular design for easy testing and maintenance
- Efficient processing pipeline
- Memory-optimized for large document collections

### Scoring Algorithm

The final relevance score combines multiple factors:
- **Base Relevance (40%)**: TF-IDF similarity between section content and persona/job
- **Title Relevance (20%)**: Keyword overlap between section titles and requirements
- **Content Quality (10%)**: Optimal content length scoring
- **Position Factor (10%)**: Slight bonus for earlier sections
- **Entity Relevance (10%)**: Named entity alignment with persona/job
- **Document Type (10%)**: Bonus for document type matching persona

### Performance Optimizations

- **Efficient Text Processing**: Vectorized operations using NumPy and scikit-learn
- **Smart Preprocessing**: Content cleaning and normalization
- **Memory Management**: Streaming processing to handle large documents
- **Caching**: Reuse of computed features across processing stages

### Handling Edge Cases

- **Empty or Corrupted PDFs**: Graceful error handling and logging
- **Multiple Languages**: Basic multilingual support through spaCy
- **Unusual Document Structures**: Adaptive section detection algorithms
- **Large Documents**: Memory-efficient processing strategies

### Output Format Compliance

The system generates JSON output matching the specified schema:
- Comprehensive metadata tracking
- Ranked section lists with importance scores
- Detailed subsection analysis with refined text
- Full traceability of processing decisions

This approach ensures reliable, accurate, and efficient processing of diverse document collections while maintaining the flexibility to handle various persona types and job requirements.
