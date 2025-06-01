#!/usr/bin/env python3
"""
Example usage demonstrations for the MoEngage Documentation Analyzer.

This script provides practical examples of how to use the documentation
analysis system for different use cases. It demonstrates both basic
and advanced usage patterns that content creators and developers
can adapt for their own workflows.

The examples cover:
1. Basic article analysis
2. Batch processing multiple URLs  
3. Custom analysis workflows
4. Integration with content management systems
"""

import os
from documentation_analyzer import DocumentationAnalyzer
from revision_agent import DocumentationRevisionAgent
import json
import time

def basic_analysis_example():
    """
    Demonstrate the most common use case: analyzing a single article.
    
    This example shows the typical workflow that most users will follow:
    1. Create an analyzer instance
    2. Fetch the article content
    3. Generate a comprehensive report
    4. Review the results
    """
    print("BASIC ANALYSIS EXAMPLE")
    print("=" * 25)
    print("This example demonstrates analyzing a single documentation article.")
    print()
    
    # Initialize the analyzer
    analyzer = DocumentationAnalyzer()
    
    # Define our target URL - using Python docs as an example since it's reliable
    url = "https://docs.python.org/3/tutorial/introduction.html"
    print(f"Analyzing: {url}")
    print()
    
    # Fetch the article content
    print("Step 1: Fetching article content...")
    if analyzer.fetch_article(url):
        print("Article fetched successfully!")
    else:
        print("Failed to fetch article - check the URL and your internet connection")
        return
    
    # Generate the comprehensive analysis report
    print("\nStep 2: Analyzing content quality...")
    start_time = time.time()
    report = analyzer.generate_report()
    analysis_time = time.time() - start_time
    
    # Display a summary of the results
    print(f"Analysis completed in {analysis_time:.2f} seconds")
    print("\nAnalysis Summary:")
    for dimension in ['readability', 'structure', 'completeness', 'style_guidelines']:
        section = report.get(dimension, {})
        suggestions_count = len(section.get('suggestions', []))
        print(f"  {dimension.title()}: {suggestions_count} suggestions")
    
    print("\nSUCCESS: Basic analysis completed!")
    
    # Show how to access specific results
    print("\nAccessing specific results:")
    readability = report.get('readability', {})
    if 'assessment' in readability:
        flesch_score = readability['assessment'].get('flesch_reading_ease', 'N/A')
        print(f"  Flesch Reading Ease Score: {flesch_score}")
    
    return report

def batch_analysis_example():
    """
    Demonstrate analyzing multiple URLs efficiently.
    
    This example is useful for content audits, competitive analysis,
    or regular quality checks across a documentation library.
    """
    print("\nBATCH ANALYSIS EXAMPLE")
    print("=" * 25)
    print("This example shows how to analyze multiple articles efficiently.")
    print()
    
    # Define a list of URLs to analyze
    # Using different Python documentation pages for demonstration
    urls = [
        "https://docs.python.org/3/tutorial/introduction.html",
        "https://docs.python.org/3/tutorial/datastructures.html",
        "https://docs.python.org/3/tutorial/modules.html"
    ]
    
    results = {}
    analyzer = DocumentationAnalyzer()
    
    print(f"Analyzing {len(urls)} articles...")
    print()
    
    for i, url in enumerate(urls, 1):
        print(f"Processing article {i}/{len(urls)}: {url}")
        
        # Fetch and analyze each article
        if analyzer.fetch_article(url):
            start_time = time.time()
            report = analyzer.generate_report()
            analysis_time = time.time() - start_time
            
            # Store results for later processing
            results[url] = {
                'report': report,
                'analysis_time': analysis_time,
                'status': 'success'
            }
            
            print(f"  Completed in {analysis_time:.2f} seconds")
        else:
            results[url] = {
                'status': 'failed',
                'error': 'Could not fetch article'
            }
            print("  Failed to fetch article")
        
        print()
    
    # Generate summary statistics across all articles
    print("BATCH ANALYSIS SUMMARY:")
    print("-" * 25)
    
    successful_analyses = [r for r in results.values() if r['status'] == 'success']
    failed_analyses = [r for r in results.values() if r['status'] == 'failed']
    
    print(f"Successfully analyzed: {len(successful_analyses)} articles")
    print(f"Failed to analyze: {len(failed_analyses)} articles")
    
    if successful_analyses:
        total_time = sum(r['analysis_time'] for r in successful_analyses)
        avg_time = total_time / len(successful_analyses)
        print(f"Average analysis time: {avg_time:.2f} seconds")
        
        # Calculate aggregate statistics
        total_suggestions = 0
        for result in successful_analyses:
            report = result['report']
            for section in report.values():
                if isinstance(section, dict) and 'suggestions' in section:
                    total_suggestions += len(section['suggestions'])
        
        print(f"Total suggestions generated: {total_suggestions}")
        print(f"Average suggestions per article: {total_suggestions / len(successful_analyses):.1f}")
    
    return results

def custom_analysis_workflow_example():
    """
    Demonstrate a custom analysis workflow for specific needs.
    
    This example shows how to use individual analysis methods
    to create specialized reports or focus on specific quality aspects.
    """
    print("\nCUSTOM ANALYSIS WORKFLOW EXAMPLE")
    print("=" * 35)
    print("This example demonstrates creating custom analysis workflows.")
    print()
    
    analyzer = DocumentationAnalyzer()
    url = "https://docs.python.org/3/tutorial/introduction.html"
    
    if not analyzer.fetch_article(url):
        print("Failed to fetch article for custom analysis")
        return
    
    print("Creating a custom readability-focused report...")
    print()
    
    # Focus specifically on readability analysis
    readability_report = analyzer.analyze_readability()
    
    # Extract key readability metrics
    if 'assessment' in readability_report:
        assessment = readability_report['assessment']
        print("READABILITY METRICS:")
        print("-" * 20)
        print(f"Flesch Reading Ease: {assessment.get('flesch_reading_ease', 'N/A'):.1f}")
        print(f"Gunning Fog Index: {assessment.get('gunning_fog_index', 'N/A'):.1f}")
        print(f"Average Sentence Length: {assessment.get('average_sentence_length', 'N/A'):.1f} words")
        print(f"Technical Terms Found: {assessment.get('technical_terms_count', 'N/A')}")
        print(f"Readability Level: {assessment.get('readability_level', 'N/A')}")
    
    # Show how to create custom scoring
    print("\nCUSTOM SCORING SYSTEM:")
    print("-" * 22)
    
    # Create a simple scoring system based on our criteria
    score = 0
    max_score = 100
    
    if 'assessment' in readability_report:
        assessment = readability_report['assessment']
        
        # Score based on Flesch Reading Ease (0-30 points)
        flesch = assessment.get('flesch_reading_ease', 0)
        if flesch >= 60:
            flesch_score = 30
        elif flesch >= 50:
            flesch_score = 20
        elif flesch >= 30:
            flesch_score = 10
        else:
            flesch_score = 0
        score += flesch_score
        print(f"Readability Score: {flesch_score}/30 (Flesch: {flesch:.1f})")
        
        # Score based on sentence length (0-20 points)
        avg_length = assessment.get('average_sentence_length', 0)
        if avg_length <= 15:
            length_score = 20
        elif avg_length <= 20:
            length_score = 15
        elif avg_length <= 25:
            length_score = 10
        else:
            length_score = 0
        score += length_score
        print(f"Sentence Length Score: {length_score}/20 (Avg: {avg_length:.1f} words)")
        
        # Score based on technical terms (0-20 points)
        tech_terms = assessment.get('technical_terms_count', 0)
        if tech_terms <= 5:
            tech_score = 20
        elif tech_terms <= 10:
            tech_score = 15
        elif tech_terms <= 15:
            tech_score = 10
        else:
            tech_score = 0
        score += tech_score
        print(f"Technical Terms Score: {tech_score}/20 ({tech_terms} terms found)")
        
        # Remaining points for structure and completeness
        structure_score = 15  # Placeholder - could analyze structure
        completeness_score = 15  # Placeholder - could analyze completeness
        score += structure_score + completeness_score
        print(f"Structure Score: {structure_score}/15 (placeholder)")
        print(f"Completeness Score: {completeness_score}/15 (placeholder)")
    
    print(f"\nOVERALL CUSTOM SCORE: {score}/{max_score} ({score/max_score*100:.1f}%)")
    
    # Provide interpretation of the custom score
    if score >= 80:
        grade = "Excellent"
    elif score >= 60:
        grade = "Good"
    elif score >= 40:
        grade = "Fair"
    else:
        grade = "Needs Improvement"
    
    print(f"Content Grade: {grade}")
    
    return {
        'readability_report': readability_report,
        'custom_score': score,
        'grade': grade
    }

def integration_example():
    """
    Demonstrate how to integrate the analyzer into larger systems.
    
    This example shows patterns useful for:
    - Content management systems
    - CI/CD pipelines
    - Automated quality checks
    - Publishing workflows
    """
    print("\nINTEGRATION EXAMPLE")
    print("=" * 20)
    print("This example shows integration patterns for larger systems.")
    print()
    
    def quality_gate_check(url, min_score=60):
        """
        Implement a quality gate that could be used in publishing workflows.
        
        Args:
            url: The article URL to check
            min_score: Minimum acceptable quality score
            
        Returns:
            dict: Quality gate results with pass/fail status
        """
        print(f"Running quality gate check for: {url}")
        
        analyzer = DocumentationAnalyzer()
        
        if not analyzer.fetch_article(url):
            return {
                'status': 'error',
                'message': 'Failed to fetch article',
                'score': 0,
                'passed': False
            }
        
        # Generate analysis report
        report = analyzer.generate_report()
        
        # Calculate a simple quality score
        total_suggestions = 0
        for section in report.values():
            if isinstance(section, dict) and 'suggestions' in section:
                total_suggestions += len(section['suggestions'])
        
        # Simple scoring: fewer suggestions = higher score
        # This is a basic example - real implementations would be more sophisticated
        if total_suggestions == 0:
            score = 100
        elif total_suggestions <= 5:
            score = 80
        elif total_suggestions <= 10:
            score = 60
        elif total_suggestions <= 15:
            score = 40
        else:
            score = 20
        
        passed = score >= min_score
        
        result = {
            'status': 'success',
            'score': score,
            'passed': passed,
            'total_suggestions': total_suggestions,
            'min_score': min_score,
            'report': report
        }
        
        print(f"  Quality Score: {score}/100")
        print(f"  Total Suggestions: {total_suggestions}")
        print(f"  Quality Gate: {'PASSED' if passed else 'FAILED'}")
        
        return result
    
    # Example usage in a publishing workflow
    test_url = "https://docs.python.org/3/tutorial/introduction.html"
    result = quality_gate_check(test_url, min_score=50)
    
    # Show how this could be used in automation
    print("\nExample automation usage:")
    print("```python")
    print("# In a CI/CD pipeline or publishing workflow:")
    print("for article_url in pending_articles:")
    print("    result = quality_gate_check(article_url)")
    print("    if result['passed']:")
    print("        publish_article(article_url)")
    print("    else:")
    print("        send_quality_feedback(article_url, result['report'])")
    print("```")
    
    return result

def main():
    """
    Run all example workflows to demonstrate the analyzer capabilities.
    
    This main function executes each example in sequence, providing
    a comprehensive demonstration of the different ways to use the
    documentation analyzer.
    """
    print("MOENGAGE DOCUMENTATION ANALYZER - USAGE EXAMPLES")
    print("=" * 55)
    print("This script demonstrates various ways to use the documentation analyzer.")
    print()
    
    # Run each example
    basic_report = basic_analysis_example()
    batch_results = batch_analysis_example()
    custom_results = custom_analysis_workflow_example()
    integration_results = integration_example()
    
    # Final summary
    print("\n" + "=" * 55)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 55)
    print("You've seen examples of:")
    print("1. Basic single-article analysis")
    print("2. Batch processing multiple articles")
    print("3. Custom analysis workflows")
    print("4. Integration patterns for larger systems")
    print()
    print("Next steps:")
    print("- Try analyzing your own documentation URLs")
    print("- Adapt these patterns for your specific use cases")
    print("- Integrate with your content management workflow")
    print("- Use the revision agent for automated improvements")

if __name__ == "__main__":
    main() 