# MoEngage Documentation Analyzer Agent

A comprehensive two-agent system for analyzing and automatically improving MoEngage documentation quality.

## Table of Contents
- [Setup Instructions](#setup-instructions)
- [Agent 1: Documentation Analyzer](#agent-1-documentation-analyzer)
- [Agent 2: Documentation Revision Agent](#agent-2-documentation-revision-agent)
- [Example Outputs](#example-outputs)
- [Design Choices & Approach](#design-choices--approach)
- [Assumptions Made](#assumptions-made)
- [Challenges Faced](#challenges-faced)
- [Usage Examples](#usage-examples)

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd documentation-analyzer-agent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download NLTK data (required for text analysis):**
```python
python -c "import nltk; nltk.download('punkt')"
```

### API Key Requirements
- **Optional**: OpenAI API key for Agent 2's LLM-assisted improvements
- If using LLM features, set your API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```
- **Note**: Agent 1 works completely without any API keys

### Quick Start

```bash
# Analyze any MoEngage documentation URL
python documentation_analyzer.py "https://help.moengage.com/hc/en-us/articles/YOUR-ARTICLE-ID"

# Run both agents (analysis + automated improvements)
python integrated_demo.py "https://help.moengage.com/hc/en-us/articles/YOUR-ARTICLE-ID"

# Launch web interface
python web_app.py
# Open http://localhost:5000 in your browser
```

## Agent 1: Documentation Analyzer

### Purpose
Analyzes documentation articles across four key dimensions and provides specific, actionable improvement suggestions.

### Analysis Dimensions

1. **Readability (Marketer-Focused)**
   - Flesch Reading Ease scoring
   - Technical jargon identification with explanations
   - Sentence complexity analysis
   - Marketer comprehension assessment

2. **Structure & Flow**
   - Heading hierarchy validation (H1-H6)
   - Content organization evaluation
   - Paragraph length optimization
   - Navigation and scanability assessment

3. **Completeness & Examples**
   - Code example verification
   - Visual aids detection (screenshots, diagrams)
   - Prerequisites and setup requirements checking
   - Use case coverage assessment

4. **Microsoft Style Guide Compliance**
   - Contractions usage ("it is" → "it's")
   - Verbose phrase simplification ("in order to" → "to")
   - Capitalization (title case → sentence case)
   - Oxford comma enforcement
   - Spacing and punctuation fixes
   - Active voice promotion

### Key Features
- **Fast Processing**: Analysis typically completes in 0.1-0.3 seconds
- **Detailed Scoring**: Numerical scores with explanations for each dimension
- **Prioritized Suggestions**: HIGH/MEDIUM/LOW priority categorization
- **JSON Output**: Structured reports for integration with other tools

## Agent 2: Documentation Revision Agent (Bonus)

### Purpose
Automatically applies feasible improvements to documentation content based on Agent 1's analysis.

### Capabilities

**Automated Improvements (Rule-Based):**
- Microsoft Style Guide violations (contractions, verbose phrases, capitalization)
- Spacing and punctuation fixes
- Oxford comma additions
- Basic structure improvements (paragraph breaking)

**LLM-Assisted Improvements (Optional):**
- Complex sentence simplification
- Active voice conversion
- Clarity enhancements
- Context-aware improvements

### Success Rate
- **Rule-Based**: ~90% successful application
- **Overall Automation**: 40-60% of suggestions can be automatically applied
- **Manual Review Required**: Complex content changes, adding examples, major restructuring

## Example Outputs

### Example 1: MoEngage Push Service Documentation

**URL**: https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service

**Analysis Results** (Agent 1):
```json
{
  "url": "https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service",
  "readability": {
    "assessment": {
      "flesch_reading_ease": 53.71,
      "readability_level": "Fairly Difficult",
      "technical_terms_count": 3
    },
    "explanation": "The content is somewhat difficult to read. Consider simplifying language and sentence structure. (Flesch score: 53.7)",
    "suggestions": [
      "The content has a low readability score (Flesch: 53.7). Consider simplifying sentences and using more common words to make it easier for marketers to understand.",
      "The following sentences are particularly complex and should be simplified..."
    ]
  },
  "structure": {
    "assessment": {
      "headings_count": 8,
      "paragraphs_count": 18,
      "heading_hierarchy": {
        "is_valid": false,
        "issue": "Heading hierarchy jumps from H1 to H3. Use sequential heading levels."
      }
    },
    "suggestions": [
      "Heading hierarchy is inconsistent. Use sequential heading levels.",
      "Consider adding a 'Next Steps' or 'Summary' section to conclude the article."
    ]
  },
  "style_guidelines": {
    "microsoft_style": {
      "missing_contractions": {
        "count": 6,
        "examples": ["Use 'can't' instead of 'cannot'", "Use 'you'll' instead of 'you will'"]
      },
      "title_capitalization": {
        "count": 3,
        "examples": ["Use sentence case: 'Recommended Action' → 'Recommended action'"]
      },
      "jargon_usage": {
        "count": 2,
        "examples": ["'sdk' should be explained as 'Software Development Kit (SDK)'"]
      }
    }
  }
}
```

**Revision Results** (Agent 2):
- **Processing Time**: 208.77 seconds total (0.12s analysis + 208.65s revision)
- **Improvements Applied**: 4 categories (30.8% automation success)
- **Changes Made**:
  - Missing contractions: 6 fixes (cannot → can't, you will → you'll)
  - Title capitalization: 3 headings fixed to sentence case
  - Jargon explanations: 2 technical terms clarified
  - AI-assisted improvements: Enhanced active voice and clarity

### Example 2: Python Tutorial Documentation (Reference Example)

**URL**: https://docs.python.org/3/tutorial/introduction.html

**Analysis Results** (Agent 1):
```json
{
  "url": "https://docs.python.org/3/tutorial/introduction.html",
  "readability": {
    "assessment": {
      "flesch_reading_ease": 68.91,
      "readability_level": "Standard",
      "technical_terms_count": 3
    },
    "suggestions": [
      "The following sentences are particularly complex and should be simplified..."
    ]
  },
  "style_guidelines": {
    "microsoft_style": {
      "missing_contractions": {
        "count": 12,
        "examples": ["Use 'don't' instead of 'do not'", "Use 'it's' instead of 'it is'"]
      },
      "spacing_issues": {
        "count": 54,
        "examples": ["Use single space after periods: found 35 instances"]
      },
      "weak_constructions": {
        "count": 16,
        "examples": ["Start with action verb instead of 'you can'"]
      }
    }
  }
}
```

**Revision Results** (Agent 2):
- **Improvements Applied**: 7 categories (43.8% automation success)
- **Processing Time**: 0.30 seconds
- **Changes Made**: 89 total improvements
  - Contractions: 12 instances
  - Spacing fixes: 54 instances  
  - Weak constructions: 16 improvements
  - Title capitalization: 5 headings

### Key Insights from MoEngage Documentation Analysis

**Common Issues Found**:
1. **Readability Challenges**: Flesch score of 53.7 indicates content is "Fairly Difficult" for marketers
2. **Structure Problems**: Inconsistent heading hierarchy (H1 jumping to H3)
3. **Missing Contractions**: 6 opportunities to make tone more friendly and conversational
4. **Technical Jargon**: Terms like "SDK" and "REST" need explanation for non-technical users
5. **Heading Capitalization**: Using title case instead of modern sentence case

**Automated Improvements Success**:
- **High Success**: Style guide violations (contractions, capitalization)
- **Moderate Success**: Technical term explanations with AI assistance
- **Manual Required**: Adding practical examples, restructuring content sections

## Design Choices & Approach

### Two-Agent Architecture
**Rationale**: Separation of concerns allows for modular usage and different deployment scenarios.
- **Agent 1** can be used standalone for analysis in content workflows
- **Agent 2** can be integrated into automated content improvement pipelines
- Clear boundaries between detection and correction reduce complexity

### Microsoft Style Guide Focus
**Choice**: Prioritized Microsoft Style Guide over generic writing advice.
**Rationale**: 
- Provides specific, measurable improvements rather than subjective suggestions
- Industry-standard guidelines proven effective for technical documentation
- Particularly optimized for non-technical audiences (marketers)
- Enables automated rule-based improvements with high confidence

### Style Guidelines Interpretation & Application

**Contractions**: Applied to informal documentation contexts but preserved formal technical terms
**Capitalization**: Sentence case for headings following modern documentation trends
**Verbose Phrases**: Aggressive simplification prioritizing clarity over formality
**Active Voice**: Promoted but preserved necessary passive constructions for technical accuracy

### Revision Approach (Agent 2)
**Choice**: Hybrid rule-based + optional LLM approach
**Rationale**:
- **Rule-based fixes**: Reliable, fast, and cost-effective for clear violations
- **LLM assistance**: Handles complex linguistic improvements where rules insufficient
- **Conservative automation**: Only applies changes with high confidence to preserve accuracy
- **Graceful degradation**: Functions fully without LLM access

### Readability Optimization for Marketers
**Approach**: Dual-focus on technical accuracy and marketer comprehension
- **Flesch Reading Ease**: Target 60+ for marketer accessibility
- **Jargon Detection**: Identify technical terms needing explanation
- **Sentence Length**: Flag >30 word sentences for simplification
- **Context Awareness**: Preserve technical precision while improving accessibility

## Assumptions Made

### Documentation Context
- **Target Audience**: Mixed technical and non-technical users (developers + marketers)
- **Platform**: Web-based documentation (HTML content)
- **Update Frequency**: Content can be revised and republished
- **Integration**: Analysis results feed into content management workflows

### Content Scope
- **Focus**: Instructional and reference documentation over marketing copy
- **Language**: English-language content only
- **Format**: HTML articles accessible via public URLs
- **Length**: Articles typically 500-5000 words (optimized for this range)

### Technical Environment  
- **Internet Access**: Required for fetching documentation URLs
- **Processing Power**: Local analysis without requiring cloud infrastructure
- **API Dependencies**: OpenAI API optional, not required for core functionality
- **Browser Compatibility**: Modern web scraping handles standard documentation sites

### Style Guide Interpretation
- **Microsoft Guidelines**: Applied flexibly with context awareness
- **Contractions**: Encouraged in instructional content, preserved in formal specifications
- **Technical Terms**: Preserved when necessary, flagged for explanation rather than replacement
- **Formatting**: HTML structure maintained while improving content

## Challenges Faced

### 1. Web Scraping Reliability
**Challenge**: Documentation sites use various HTML structures and anti-scraping measures.
**Solution**: 
- Robust HTML parsing with BeautifulSoup fallbacks
- Content extraction focusing on main article areas
- Graceful handling of failed requests with informative error messages
- User-agent headers and respectful request patterns

### 2. Balancing Automation vs. Accuracy
**Challenge**: Aggressive automation could introduce errors in technical content.
**Approach**:
- Conservative rule-based improvements with high confidence thresholds
- Explicit categorization of automated vs. manual-review suggestions  
- Preservation of technical terminology and code examples
- Comprehensive testing on real documentation

### 3. Microsoft Style Guide Contextual Application
**Challenge**: Style rules need contextual awareness (formal vs. informal sections).
**Solution**:
- Content-aware rule application (e.g., contractions in explanatory text)
- Preservation of code blocks and technical specifications
- Heading-specific capitalization rules
- Context-sensitive jargon detection

### 4. Marketer-Focused Readability Assessment
**Challenge**: Standard readability metrics don't account for technical domain knowledge.
**Approach**:
- Combined quantitative (Flesch scores) and qualitative (jargon detection) analysis
- Technical term identification with explanation suggestions
- Sentence complexity analysis beyond simple word counting
- Use case and context assessment for marketing relevance

### 5. LLM Integration Cost & Reliability  
**Challenge**: OpenAI API costs and availability could limit practical usage.
**Solution**:
- Made LLM features optional with graceful degradation
- Optimized API usage (only substantial paragraphs, not every sentence)
- Local rule-based improvements handle majority of cases
- Clear cost estimation and usage controls

## Additional Challenges (Given More Time)

### Advanced Content Analysis
- **Semantic Understanding**: Better detection of missing context and use cases
- **Cross-Reference Validation**: Checking links and references within documentation
- **Multimedia Integration**: Analysis of screenshots and diagrams for completeness
- **A/B Testing Framework**: Quantitative validation of readability improvements

### Scalability & Integration
- **Batch Processing**: Efficient analysis of entire documentation sites
- **Content Management Integration**: Direct integration with CMS platforms
- **Real-Time Collaboration**: Multi-user editing with live improvement suggestions
- **Performance Optimization**: Caching and incremental analysis for large sites

### Advanced Language Processing
- **Multi-Language Support**: Analysis beyond English documentation
- **Domain-Specific Guidelines**: Customizable style guides for different industries
- **Advanced NLP**: Better context understanding for complex technical content
- **Automated Example Generation**: AI-generated code samples and use cases

## Usage Examples

### Command Line Interface
```bash
# Basic analysis of MoEngage documentation
python documentation_analyzer.py "https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service"

# Analysis with JSON output saved
python documentation_analyzer.py "URL" --output json --save-report

# Complete workflow (analysis + revision)
python integrated_demo.py "https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service"

# Web interface
python web_app.py
```

### Programmatic Usage
```python
from documentation_analyzer import DocumentationAnalyzer
from revision_agent import DocumentationRevisionAgent

# Agent 1: Analysis
analyzer = DocumentationAnalyzer()
analyzer.fetch_article("https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service")
report = analyzer.generate_report()

# Agent 2: Automated improvements
agent = DocumentationRevisionAgent()
result = agent.process_document("https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service", report)

print(f"Applied {len(result['suggestions_applied'])} improvements")
```

### Integration Example
```python
# Batch processing multiple MoEngage URLs
urls = [
    "https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service",
    "https://help.moengage.com/hc/en-us/articles/YOUR-SECOND-ARTICLE-ID"
]

for url in urls:
    analyzer = DocumentationAnalyzer()
    if analyzer.fetch_article(url):
        report = analyzer.generate_report()
        
        # Save analysis results
        with open(f"analysis_{url.split('/')[-1]}.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Analyzed {url}: {len(report['overall_recommendations'])} recommendations")
```

---

## File Structure

```
documentation-analyzer-agent/
├── documentation_analyzer.py      # Agent 1: Core analysis engine
├── revision_agent.py             # Agent 2: Automated improvement engine
├── integrated_demo.py            # Complete workflow demonstration
├── web_app.py                    # Flask web interface
├── test_analyzer.py              # Test suite
├── example_usage.py              # Usage examples and patterns
├── requirements.txt              # Python dependencies
├── templates/                    # Web interface templates
│   └── index.html
├── static/                       # CSS and JavaScript assets
├── analysis_report.json          # Example output from Agent 1 (Python docs)
├── moengage_analysis_example.json # Example output from MoEngage documentation  
├── revision_report.json          # Example output from Agent 2
├── revised_article.html          # Example improved content
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Testing

Run the test suite to verify functionality:

```bash
python test_analyzer.py
```

Expected output:
```
Testing URL fetching...
✓ Successfully fetched content from test URL

Testing analysis components...
✓ Readability analysis completed
✓ Structure analysis completed  
✓ Completeness analysis completed
✓ Style guidelines analysis completed

Testing integrated workflow...
✓ Complete analysis workflow successful

All tests passed! (8/8 successful)
``` 