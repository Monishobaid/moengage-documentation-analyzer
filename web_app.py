#!/usr/bin/env python3
"""
Web interface for the MoEngage Documentation Analyzer

A simple Flask web app that provides a user-friendly interface
for analyzing documentation.
"""

from flask import Flask, render_template, request, jsonify
from documentation_analyzer import DocumentationAnalyzer
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a documentation URL"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Create analyzer and fetch article
        analyzer = DocumentationAnalyzer()
        
        if not analyzer.fetch_article(url):
            return jsonify({'error': 'Failed to fetch article. Please check the URL.'}), 400
        
        # Generate report
        report = analyzer.generate_report()
        
        # Add summary statistics
        summary = {
            'total_suggestions': 0,
            'high_priority': 0,
            'sections': {}
        }
        
        for section in ['readability', 'structure', 'completeness', 'style_guidelines']:
            if section in report and 'suggestions' in report[section]:
                count = len(report[section]['suggestions'])
                summary['total_suggestions'] += count
                summary['sections'][section] = count
        
        for rec in report.get('overall_recommendations', []):
            if 'HIGH PRIORITY' in rec:
                summary['high_priority'] += 1
        
        report['summary'] = summary
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    import os
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, port=5000) 