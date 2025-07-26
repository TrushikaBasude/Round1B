#!/usr/bin/env python3
"""
Create a sample PDF for testing the Adobe Round 1B challenge
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import os

def create_sample_pdf():
    # Create output path
    output_path = "input/sample_research_paper.pdf"
    
    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("Graph Neural Networks for Drug Discovery: A Comprehensive Survey", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Abstract
    abstract_title = Paragraph("Abstract", styles['Heading1'])
    story.append(abstract_title)
    abstract_text = """Graph neural networks (GNNs) have emerged as a powerful tool for drug discovery, 
    particularly in molecular property prediction and drug-target interaction modeling. This paper presents 
    a comprehensive survey of GNN applications in pharmaceutical research, focusing on methodologies, 
    datasets, and performance benchmarks."""
    abstract = Paragraph(abstract_text, styles['Normal'])
    story.append(abstract)
    story.append(Spacer(1, 12))
    
    # Introduction
    intro_title = Paragraph("Introduction", styles['Heading1'])
    story.append(intro_title)
    intro_text = """The pharmaceutical industry faces significant challenges in drug discovery, with traditional 
    methods requiring extensive time and resources. Machine learning approaches, particularly graph neural networks, 
    offer promising solutions by leveraging molecular graph representations to predict drug properties and interactions.
    
    Graph neural networks excel at capturing complex molecular structures by treating atoms as nodes and bonds as edges. 
    This representation allows for the modeling of intricate chemical relationships that are crucial for understanding drug behavior."""
    intro = Paragraph(intro_text, styles['Normal'])
    story.append(intro)
    story.append(Spacer(1, 12))
    
    # Methodologies
    methods_title = Paragraph("Methodologies", styles['Heading1'])
    story.append(methods_title)
    
    gcn_title = Paragraph("2.1 Graph Convolution Networks", styles['Heading2'])
    story.append(gcn_title)
    gcn_text = """Graph Convolution Networks (GCNs) represent the foundation of most molecular property prediction models. 
    These networks aggregate information from neighboring atoms to create comprehensive molecular representations."""
    gcn = Paragraph(gcn_text, styles['Normal'])
    story.append(gcn)
    story.append(Spacer(1, 8))
    
    gat_title = Paragraph("2.2 Graph Attention Networks", styles['Heading2'])
    story.append(gat_title)
    gat_text = """Graph Attention Networks (GATs) introduce attention mechanisms to weight the importance of different 
    molecular fragments. This approach has shown superior performance in drug-target interaction prediction tasks."""
    gat = Paragraph(gat_text, styles['Normal'])
    story.append(gat)
    story.append(Spacer(1, 8))
    
    mpnn_title = Paragraph("2.3 Message Passing Networks", styles['Heading2'])
    story.append(mpnn_title)
    mpnn_text = """Message Passing Neural Networks (MPNNs) provide a general framework for molecular property 
    prediction by enabling flexible information exchange between atoms."""
    mpnn = Paragraph(mpnn_text, styles['Normal'])
    story.append(mpnn)
    story.append(Spacer(1, 12))
    
    # Datasets and Benchmarks
    datasets_title = Paragraph("Datasets and Benchmarks", styles['Heading1'])
    story.append(datasets_title)
    
    datasets_text = """Several benchmark datasets are commonly used for evaluating GNN performance:
    • QM9: Contains 130,000 small organic molecules with quantum mechanical properties
    • ZINC: Large database of commercially available compounds
    • ChEMBL: Bioactivity database with over 2 million compounds
    • DrugBank: Comprehensive resource containing drug and target information"""
    datasets = Paragraph(datasets_text, styles['Normal'])
    story.append(datasets)
    story.append(Spacer(1, 8))
    
    benchmarks_title = Paragraph("3.2 Performance Benchmarks", styles['Heading2'])
    story.append(benchmarks_title)
    benchmarks_text = """Recent studies have demonstrated that GNN-based approaches consistently outperform 
    traditional molecular descriptors:
    • Molecular property prediction: R² values ranging from 0.85 to 0.95
    • Drug-target interaction: AUC scores above 0.90
    • ADMET prediction: Accuracy improvements of 10-15% over baseline methods"""
    benchmarks = Paragraph(benchmarks_text, styles['Normal'])
    story.append(benchmarks)
    story.append(Spacer(1, 12))
    
    # Results
    results_title = Paragraph("Results and Analysis", styles['Heading1'])
    story.append(results_title)
    results_text = """Our analysis reveals that attention-based GNNs achieve the best performance across most 
    drug discovery tasks. The integration of molecular fingerprints with graph representations further enhances 
    predictive accuracy. Modern GNN architectures demonstrate excellent scalability, processing large molecular 
    databases within reasonable computational budgets."""
    results = Paragraph(results_text, styles['Normal'])
    story.append(results)
    story.append(Spacer(1, 12))
    
    # Conclusion
    conclusion_title = Paragraph("Conclusion", styles['Heading1'])
    story.append(conclusion_title)
    conclusion_text = """Graph neural networks have revolutionized computational drug discovery by providing 
    powerful tools for molecular representation learning. The combination of sophisticated architectures, 
    comprehensive datasets, and rigorous benchmarking has established GNNs as the state-of-the-art approach 
    for pharmaceutical applications."""
    conclusion = Paragraph(conclusion_text, styles['Normal'])
    story.append(conclusion)
    
    # Build PDF
    doc.build(story)
    print(f"Sample PDF created: {output_path}")

if __name__ == "__main__":
    create_sample_pdf()