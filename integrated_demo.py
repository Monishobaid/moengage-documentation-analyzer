#!/usr/bin/env python3
"""
Demo of the complete documentation improvement workflow.

Shows off both agents working together:
1. Agent 1: Analyzes docs and finds problems
2. Agent 2: Actually fixes the stuff it can
3. Saves reports and improved content

Works with any documentation but designed for MoEngage docs.
"""

import time
import json
from documentation_analyzer import DocumentationAnalyzer
from revision_agent import DocumentationRevisionAgent

def run_integrated_demo(url: str):
    """
    Run the full demo - analysis plus automated improvements.
    
    Takes a URL, analyzes it, fixes what it can, and spits out
    detailed reports about what happened.
    """
    print("=" * 80)
    print("DOCUMENTATION IMPROVEMENT AGENT DEMONSTRATION")
    print("=" * 80)
    print(f"Target URL: {url}")
    print("-" * 80)
    
    # Phase 1: Let Agent 1 do its thing
    print("\nPHASE 1: COMPREHENSIVE DOCUMENTATION ANALYSIS")
    print("-" * 50)
    
    analyzer = DocumentationAnalyzer()
    
    # Grab the article first
    print("Fetching article content...")
    if not analyzer.fetch_article(url):
        print("FAILED: Unable to fetch article content")
        return
    
    print("SUCCESS: Article fetched successfully")
    print("Analyzing content across all quality dimensions...")
    
    # Time how long analysis takes
    analysis_start = time.time()
    analysis_report = analyzer.generate_report()
    analysis_time = time.time() - analysis_start
    
    print(f"SUCCESS: Analysis completed in {analysis_time:.2f} seconds")
    
    # Show what we found
    print("\nANALYSIS SUMMARY:")
    print("-" * 20)
    
    for dimension in ['readability', 'structure', 'completeness', 'style_guidelines']:
        section = analysis_report.get(dimension, {})
        suggestions_count = len(section.get('suggestions', []))
        print(f"  {dimension.title()}: {suggestions_count} suggestions")
    
    print("\nKEY SUGGESTIONS:")
    print("-" * 15)
    
    # Collect all the suggestions
    all_suggestions = []
    for section in analysis_report.values():
        if isinstance(section, dict) and 'suggestions' in section:
            all_suggestions.extend(section['suggestions'])
    
    # Show the first few as examples
    for i, suggestion in enumerate(all_suggestions[:5], 1):
        # Don't spam them with super long suggestions
        display_suggestion = suggestion[:100] + "..." if len(suggestion) > 100 else suggestion
        print(f"  {i}. {display_suggestion}")
    
    if len(all_suggestions) > 5:
        print(f"  ... and {len(all_suggestions) - 5} more suggestions")
    
    # Phase 2: Agent 2 tries to fix stuff
    print("\n" + "=" * 80)
    print("PHASE 2: AUTOMATED IMPROVEMENT APPLICATION")
    print("-" * 50)
    
    print("Applying automated revisions...")
    
    # Fire up the revision agent
    revision_agent = DocumentationRevisionAgent()
    
    # Time the revision process too
    revision_start = time.time()
    revision_result = revision_agent.process_document(url, analysis_report)
    revision_time = time.time() - revision_start
    
    if 'error' in revision_result:
        print(f"FAILED: Revision process encountered an error: {revision_result['error']}")
        return
    
    print(f"SUCCESS: Revisions completed in {revision_time:.2f} seconds")
    
    # Show what got fixed
    applied_suggestions = revision_result.get('suggestions_applied', [])
    revision_summary = revision_result.get('revision_summary', {})
    
    # Calculate how well we did
    total_analyzed = revision_summary.get('total_suggestions_analyzed', 0)
    total_applied = revision_summary.get('suggestions_applied', 0)
    success_rate = (total_applied / total_analyzed * 100) if total_analyzed > 0 else 0
    
    print(f"\nAPPLIED IMPROVEMENTS:")
    print("-" * 20)
    
    for improvement in applied_suggestions:
        print(f"  - {improvement}")
    
    # Break down what was automated vs needs human attention
    automated_vs_manual = revision_summary.get('automated_vs_manual', {})
    print(f"\nAUTOMATION SUMMARY:")
    print("-" * 17)
    print(f"  SUCCESS: Automated: {automated_vs_manual['automated']}")
    print(f"  MANUAL REQUIRED: {automated_vs_manual['requires_manual']}")
    
    # Save everything to files
    print("\n" + "=" * 80)
    print("PHASE 3: REPORT GENERATION AND FILE OUTPUT")
    print("-" * 50)
    
    # Save the analysis results
    with open('analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, indent=2, ensure_ascii=False)
    print("Analysis report saved to 'analysis_report.json'")
    
    # Save revision results
    revision_report = {
        "url": url,
        "processing_time": {
            "analysis_seconds": analysis_time,
            "revision_seconds": revision_time,
            "total_seconds": analysis_time + revision_time
        },
        "suggestions_applied": applied_suggestions,
        "revision_summary": revision_summary,
        "success_metrics": {
            "total_suggestions": total_analyzed,
            "automated_improvements": total_applied,
            "automation_success_rate": f"{success_rate:.1f}%"
        }
    }
    
    with open('revision_report.json', 'w', encoding='utf-8') as f:
        json.dump(revision_report, f, indent=2, ensure_ascii=False)
    print("Revision report saved to 'revision_report.json'")
    
    # Save the improved HTML
    with open('revised_article.html', 'w', encoding='utf-8') as f:
        f.write(revision_result['revised_content'])
    print("Revised article saved to 'revised_article.html'")
    
    # Wrap up with summary
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    print(f"Total processing time: {(analysis_time + revision_time):.2f} seconds")
    print(f"Analysis: {len([s for section in analysis_report.values() if isinstance(section, dict) for s in section.get('suggestions', [])])} total suggestions")
    print(f"Revisions: {len(applied_suggestions)} categories of improvements applied")
    print(f"Success rate: {success_rate:.1f}% of suggestions automated")
    
    # Tell them what to do next
    print("\nNEXT STEPS:")
    print("-" * 11)
    print("1. Review 'revised_article.html' to see the improved content")
    print("2. Check 'analysis_report.json' for detailed suggestions")
    print("3. Use 'revision_report.json' to track automation metrics")
    
    # Remind about AI features if they don't have them
    if not revision_agent.use_ai:
        print("\nTIP: To enable AI features:")
        print("  1. Install Ollama: brew install ollama")
        print("  2. Start service: brew services start ollama") 
        print("  3. Download model: ollama pull llama3.2:3b")
        print("  4. Rerun demo for enhanced AI-assisted improvements")

def main():
    """
    Command line entry point for the demo.
    
    Just handles the arguments and kicks off the demo.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Demonstrate the complete documentation improvement workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python integrated_demo.py https://help.moengage.com/hc/en-us/articles/123456789
  python integrated_demo.py https://docs.python.org/3/tutorial/introduction.html
        """
    )
    parser.add_argument('url', help='URL of the documentation to analyze and improve')
    
    args = parser.parse_args()
    
    # Execute the complete demonstration workflow
    run_integrated_demo(args.url)

if __name__ == "__main__":
    main() 