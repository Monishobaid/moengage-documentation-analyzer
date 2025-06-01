#!/usr/bin/env python3
"""
Web interface for the Documentation Analyzer

Just a simple Flask app that gives you a nice web UI instead of
having to mess around with command line arguments.
"""

from flask import Flask, render_template, request, jsonify
from documentation_analyzer import DocumentationAnalyzer
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """Show the main page with the analyzer form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Do the actual analysis when someone submits a URL"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Fire up the analyzer
        analyzer = DocumentationAnalyzer()
        
        if not analyzer.fetch_article(url):
            return jsonify({'error': 'Failed to fetch article. Please check the URL.'}), 400
        
        # Run the full analysis
        report = analyzer.generate_report()
        
        # Calculate some summary stats for the dashboard
        summary = {
            'total_suggestions': 0,
            'high_priority': 0,
            'sections': {}
        }
        
        # Count up suggestions by section
        for section in ['readability', 'structure', 'completeness', 'style_guidelines']:
            if section in report and 'suggestions' in report[section]:
                count = len(report[section]['suggestions'])
                summary['total_suggestions'] += count
                summary['sections'][section] = count
        
        # Count high priority items
        for rec in report.get('overall_recommendations', []):
            if 'HIGH PRIORITY' in rec:
                summary['high_priority'] += 1
        
        report['summary'] = summary
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Simple health check - useful for monitoring"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Make sure we have the directories we need
    import os
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, port=5000) 