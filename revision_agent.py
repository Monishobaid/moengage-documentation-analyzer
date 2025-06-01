import re
import json
import requests
from typing import Dict, List, Tuple
from bs4 import BeautifulSoup
import os
from documentation_analyzer import DocumentationAnalyzer

class DocumentationRevisionAgent:
    """
    The second agent in our documentation improvement pipeline.
    
    This agent takes the analysis results from DocumentationAnalyzer and automatically
    applies improvements that can be reliably automated. This includes:
    - Microsoft Style Guide compliance fixes
    - Basic readability improvements 
    - Structure enhancements
    - AI-assisted content improvements using local Ollama models
    
    The focus is on changes that don't require human judgment or domain expertise,
    allowing content creators to focus on higher-level improvements.
    """
    
    def __init__(self, ollama_model: str = "llama3.2:3b", ollama_url: str = "http://localhost:11434"):
        """
        Initialize the revision agent with AI capabilities.
        
        Args:
            ollama_model: The Ollama model to use for AI-assisted improvements
            ollama_url: URL of the local Ollama server
        """
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url
        # Check if we can use AI features or fall back to rule-based only
        self.use_ai = self._check_ollama_availability()
        
        if not self.use_ai:
            print("INFO: Ollama not available. Will use rule-based revisions only.")
            print("TIP: To enable AI-assisted revisions:")
            print("   1. Install Ollama: brew install ollama")
            print("   2. Start service: brew services start ollama")
            print("   3. Download model: ollama pull llama3.2:3b")
        
        # Initialize content storage - will be populated by process_document()
        self.original_content = None
        self.soup = None
        self.suggestions = None
        self.revised_content = None
        
    def _check_ollama_availability(self) -> bool:
        """
        Verify that Ollama is running and has the required model available.
        
        This method performs a series of checks:
        1. Can we connect to the Ollama server?
        2. Is our preferred model downloaded and available?
        3. Can we make a basic API request?
        
        Returns:
            bool: True if Ollama is fully available, False if we should use rule-based only
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                
                # Check if our preferred model is available
                if self.ollama_model in available_models or f"{self.ollama_model}:latest" in available_models:
                    print(f"SUCCESS: Ollama available with model: {self.ollama_model}")
                    return True
                else:
                    print(f"WARNING: Ollama available but model '{self.ollama_model}' not found.")
                    print(f"Available models: {', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''}")
                    print(f"TIP: Install model: ollama pull {self.ollama_model}")
                    return False
            else:
                return False
        except requests.exceptions.RequestException:
            # Ollama server is not running or not accessible
            return False
    
    def process_document(self, url: str, suggestions: Dict = None) -> Dict:
        """
        Main processing method that coordinates the entire revision workflow.
        
        This method orchestrates the complete revision process:
        1. Fetch the original document if needed
        2. Get analysis suggestions if not provided
        3. Apply all feasible revisions
        4. Generate a comprehensive report of changes
        
        Args:
            url: URL of the documentation to revise
            suggestions: Pre-generated suggestions from DocumentationAnalyzer (optional)
            
        Returns:
            Dict containing original content, applied changes, and revised content
        """
        # Start by getting the original document content
        analyzer = DocumentationAnalyzer()
        if not analyzer.fetch_article(url):
            return {"error": "Failed to fetch article"}
        
        # Store the original content for comparison and revision
        self.original_content = analyzer.content
        self.soup = BeautifulSoup(self.original_content, 'html.parser')
        
        # If no suggestions were provided, generate them now
        # This allows the revision agent to work independently
        if suggestions is None:
            suggestions = analyzer.generate_report()
        
        self.suggestions = suggestions
        
        # Apply all the revisions we can automate
        self.revised_content = self._apply_all_revisions()
        
        # Return a comprehensive report of what we accomplished
        return {
            "url": url,
            "original_content": self.original_content,
            "suggestions_applied": self._get_applied_suggestions(),
            "revised_content": self.revised_content,
            "revision_summary": self._generate_revision_summary()
        }
    
    def _apply_all_revisions(self) -> str:
        """
        Coordinate the application of all revision types.
        
        This method applies revisions in a specific order:
        1. Microsoft Style Guide fixes (most reliable)
        2. Structure improvements (medium complexity)
        3. AI-assisted revisions (if available, highest complexity)
        
        Returns:
            str: The fully revised HTML content
        """
        # Start with a fresh copy of the original content
        revised_soup = BeautifulSoup(self.original_content, 'html.parser')
        
        # Apply the most reliable, rule-based improvements first
        revised_soup = self._apply_microsoft_style_fixes(revised_soup)
        revised_soup = self._apply_structure_improvements(revised_soup)
        
        # Add AI improvements if we have Ollama available
        if self.use_ai:
            revised_soup = self._apply_ai_revisions(revised_soup)
        
        return str(revised_soup)
    
    def _apply_microsoft_style_fixes(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Apply Microsoft Style Guide compliance fixes automatically.
        
        These fixes are based on well-defined rules from the Microsoft Style Guide:
        - Add contractions for friendlier tone
        - Remove verbose phrases
        - Fix spacing issues
        - Correct heading capitalization and punctuation
        - Add Oxford commas
        
        Args:
            soup: BeautifulSoup object containing the HTML to revise
            
        Returns:
            BeautifulSoup: Updated soup with style fixes applied
        """
        
        # Process all text nodes in the document
        # We skip script and style tags since those shouldn't be modified
        text_elements = soup.find_all(text=True)
        
        for element in text_elements:
            if element.parent.name in ['script', 'style']:
                continue
                
            original_text = str(element)
            revised_text = original_text
            
            # Apply each type of text improvement
            revised_text = self._add_contractions(revised_text)
            revised_text = self._simplify_verbose_phrases(revised_text)
            revised_text = self._fix_spacing_issues(revised_text)
            
            # Only update the element if we actually made changes
            if revised_text != original_text:
                element.replace_with(revised_text)
        
        # Handle structural improvements that need to work on HTML elements
        soup = self._fix_heading_issues(soup)
        soup = self._add_oxford_commas(soup)
        
        return soup
    
    def _add_contractions(self, text: str) -> str:
        """
        Add contractions to make the tone more conversational and friendly.
        
        This follows Microsoft Style Guide recommendations to use contractions
        for a more natural, approachable tone. We target the most common
        formal phrases that can be safely converted.
        
        Args:
            text: The text to process
            
        Returns:
            str: Text with contractions applied
        """
        # Define our contraction mappings
        # We use word boundaries (\b) to avoid partial word matches
        contractions = {
            r'\bit is\b': "it's",
            r'\byou are\b': "you're", 
            r'\byou will\b': "you'll",
            r'\bwe are\b': "we're",
            r'\blet us\b': "let's",
            r'\bdo not\b': "don't",
            r'\bwill not\b': "won't",
            r'\bcannot\b': "can't",
            r'\bshould not\b': "shouldn't",
            r'\bwould not\b': "wouldn't",
            r'\bcould not\b': "couldn't",
            r'\bthat is\b': "that's",
            r'\bthere is\b': "there's",
            r'\bwhat is\b': "what's"
        }
        
        # Apply each contraction pattern
        for pattern, replacement in contractions.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _simplify_verbose_phrases(self, text: str) -> str:
        """
        Replace unnecessarily verbose phrases with concise alternatives.
        
        This implements the Microsoft Style Guide principle of "use bigger ideas,
        fewer words." We target common wordy phrases that can be simplified
        without changing meaning.
        
        Args:
            text: The text to process
            
        Returns:
            str: Text with verbose phrases simplified
        """
        # Map verbose phrases to concise alternatives
        replacements = {
            r'\bin order to\b': 'to',
            r'\bdue to the fact that\b': 'because',
            r'\bin the event that\b': 'if',
            r'\bat this point in time\b': 'now',
            r'\bfor the purpose of\b': 'to',
            r'\bwith regard to\b': 'about',
            r'\bin spite of the fact that\b': 'although',
            r'\buntil such time as\b': 'until',
            r'\bas a result of\b': 'because',
            r'\bprior to\b': 'before',
            r'\bsubsequent to\b': 'after',
            r'\bin addition to\b': 'besides',
            r'\ba large number of\b': 'many',
            r'\ba great deal of\b': 'much',
            r'\bon a regular basis\b': 'regularly',
            r'\bmake a decision\b': 'decide',
            r'\bgive consideration to\b': 'consider',
            # Remove redundant introductory phrases
            r'\bit is important to note that\s*': '',
            r'\bplease be aware that\s*': '',
            r'\bit should be noted that\s*': ''
        }
        
        # Apply each simplification
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_spacing_issues(self, text: str) -> str:
        """Fix spacing issues."""
        # Single space after punctuation
        text = re.sub(r'([.!?])\s{2,}', r'\1 ', text)
        
        # Remove spaces around dashes
        text = re.sub(r'\s+—\s+', '—', text)
        text = re.sub(r'\s+-\s+', '-', text)
        
        return text
    
    def _fix_heading_issues(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Fix heading capitalization and punctuation."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            original_text = heading.get_text(strip=True)
            
            # Convert to sentence case (only first word capitalized)
            words = original_text.split()
            if words:
                # Capitalize first word, lowercase others (except proper nouns)
                revised_text = words[0].capitalize()
                for word in words[1:]:
                    # Keep certain words capitalized (APIs, proper nouns, etc.)
                    if word.upper() in ['API', 'UI', 'ID', 'URL', 'SDK', 'HTTP', 'JSON']:
                        revised_text += ' ' + word.upper()
                    else:
                        revised_text += ' ' + word.lower()
                
                # Remove end punctuation if heading is short
                if len(words) <= 3:
                    revised_text = revised_text.rstrip('.!?:')
                
                # Update heading if changed
                if revised_text != original_text:
                    heading.string = revised_text
        
        return soup
    
    def _add_oxford_commas(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Add Oxford commas to lists."""
        text_elements = soup.find_all(text=True)
        
        for element in text_elements:
            if element.parent.name in ['script', 'style']:
                continue
                
            original_text = str(element)
            # Pattern for lists without Oxford comma
            revised_text = re.sub(
                r'\b(\w+),\s+(\w+)\s+and\s+(\w+)\b',
                r'\1, \2, and \3',
                original_text
            )
            
            if revised_text != original_text:
                element.replace_with(revised_text)
        
        return soup
    
    def _apply_structure_improvements(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Apply structural improvements like breaking long paragraphs."""
        paragraphs = soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            words = text.split()
            
            # Break long paragraphs (>100 words)
            if len(words) > 100:
                # Split at sentence boundaries around the middle
                sentences = re.split(r'(?<=[.!?])\s+', text)
                if len(sentences) > 2:
                    mid_point = len(sentences) // 2
                    first_part = ' '.join(sentences[:mid_point])
                    second_part = ' '.join(sentences[mid_point:])
                    
                    # Create new paragraph structure
                    new_p1 = soup.new_tag('p')
                    new_p1.string = first_part
                    new_p2 = soup.new_tag('p')
                    new_p2.string = second_part
                    
                    # Replace original paragraph
                    p.insert_before(new_p1)
                    p.insert_before(new_p2)
                    p.decompose()
        
        return soup
    
    def _apply_ai_revisions(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Apply AI-powered improvements to content that require contextual understanding.
        
        This method uses the local Ollama language model to improve paragraphs
        based on Microsoft Style Guide principles. It focuses on improvements
        that require understanding context and meaning, such as:
        - Converting passive voice to active voice
        - Improving weak constructions
        - Making content more action-oriented
        
        Args:
            soup: BeautifulSoup object containing the HTML to improve
            
        Returns:
            BeautifulSoup: Updated soup with AI improvements applied
        """
        if not self.use_ai:
            return soup
        
        # Find the main content area to focus our AI improvements
        # We want to avoid processing navigation, headers, footers, etc.
        main_content = soup.find('article') or soup.find('main') or soup.find('body')
        
        if main_content:
            paragraphs = main_content.find_all('p')
            
            # Process each paragraph individually for better quality control
            for p in paragraphs:
                text = p.get_text(strip=True)
                
                # Only apply AI to substantial paragraphs to make it worthwhile
                # Short paragraphs often don't need AI improvement
                if len(text.split()) > 20:
                    revised_text = self._ai_improve_paragraph(text)
                    if revised_text and revised_text != text:
                        p.string = revised_text
        
        return soup
    
    def _ai_improve_paragraph(self, text: str) -> str:
        """
        Use AI to improve a single paragraph according to style guidelines.
        
        This method sends a carefully crafted prompt to Ollama that focuses on
        specific, measurable improvements rather than general "make it better"
        requests. The AI is instructed to maintain technical accuracy while
        improving clarity and directness.
        
        Args:
            text: The original paragraph text to improve
            
        Returns:
            str: The improved paragraph text, or original if improvement failed
        """
        try:
            # Craft a specific prompt that gives the AI clear guidelines
            # This helps ensure consistent, high-quality improvements
            prompt_text = f"""You are a technical writing expert who improves documentation clarity according to Microsoft Style Guide principles.

Improve the following documentation paragraph according to Microsoft Style Guide principles:
1. Use active voice instead of passive voice
2. Replace weak constructions like "you can" and "there is/are" with direct action
3. Simplify complex sentences
4. Make it more action-oriented and direct
5. Maintain the original meaning and technical accuracy

Original paragraph:
{text}

Provide ONLY the improved paragraph text, no explanations or additional text:"""
            
            # Make the API request to our local Ollama server
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt_text,
                    "stream": False,  # We want the complete response at once
                    "options": {
                        "temperature": 0.3,  # Lower temperature for more consistent output
                        "num_predict": 150   # Limit response length to keep it focused
                    }
                },
                timeout=60  # Give it time to process but don't wait forever
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'response' in result:
                    improved_text = result['response'].strip()
                    
                    # Clean up the AI response to extract just the improved text
                    if improved_text and improved_text != text:
                        # Remove common AI response prefixes
                        prefixes_to_remove = [
                            "Here's the improved paragraph:",
                            "Here's an improved version:",
                            "Improved paragraph:",
                            "Here's the improved text:",
                            "Revised version:",
                            "Here's the revision:"
                        ]
                        
                        for prefix in prefixes_to_remove:
                            if improved_text.lower().startswith(prefix.lower()):
                                improved_text = improved_text[len(prefix):].strip()
                                break
                        
                        # Remove quotes if the AI wrapped the response in quotes
                        if improved_text.startswith('"') and improved_text.endswith('"'):
                            improved_text = improved_text[1:-1].strip()
                        
                        # Take only the first meaningful paragraph to avoid rambling
                        lines = improved_text.split('\n')
                        # Get the first non-empty line as the improved text
                        for line in lines:
                            line = line.strip()
                            if line and not line.lower().startswith(('here', 'this', 'the revised')):
                                improved_text = line
                                break
                        
                        # Only return if we got meaningful improvement
                        if improved_text and len(improved_text) > 10 and improved_text != text:
                            print(f"AI improved: '{text[:50]}...' -> '{improved_text[:50]}...'")
                            return improved_text
                        else:
                            print(f"AI improvement not useful for: '{text[:50]}...'")
                            return text
                    else:
                        return text
                else:
                    print("ERROR: Ollama API returned empty response")
                    return text
            elif response.status_code == 400:
                print("ERROR: Ollama API bad request - check model and prompt")
                self.use_ai = False  # Disable AI for remaining requests to avoid spam
                return text
            elif response.status_code == 404:
                print("ERROR: Ollama API model not found - check if model is downloaded")
                self.use_ai = False  # Disable AI for remaining requests
                return text
            elif response.status_code == 429:
                print("WARNING: Ollama API rate limit exceeded - continuing with rule-based revisions only")
                return text
            else:
                print(f"ERROR: Ollama API failed with HTTP {response.status_code}")
                if response.text:
                    error_message = response.text
                    print(f"Error details: {error_message}")
                return text
                
        except Exception as e:
            print(f"ERROR: AI revision failed: {e}")
            return text
    
    def _get_applied_suggestions(self) -> List[str]:
        """
        Generate a list of improvement categories that were successfully applied.
        
        This method examines the original analysis suggestions and determines
        which ones we were able to address automatically. It's used for reporting
        and helps users understand what was accomplished.
        
        Returns:
            List[str]: Descriptions of applied improvements
        """
        applied = []
        
        # Check which Microsoft Style Guide issues we addressed
        microsoft_issues = self.suggestions.get('style_guidelines', {}).get('assessment', {}).get('microsoft_style', {})
        
        for category, issues in microsoft_issues.items():
            if issues.get('count', 0) > 0:
                applied.append(f"Applied {category.replace('_', ' ')} fixes: {issues['message']}")
        
        # Add structure improvements if we made them
        if self._has_long_paragraphs():
            applied.append("Applied structure improvements: broke up long paragraphs")
        
        # Add AI improvements if we used them
        if self.use_ai:
            applied.append("Applied AI-assisted improvements: enhanced active voice and clarity")
        
        return applied
    
    def _has_long_paragraphs(self) -> bool:
        """
        Check if the original content contained paragraphs that needed breaking up.
        
        This is used to determine if we should report structure improvements
        in our applied suggestions list.
        
        Returns:
            bool: True if original content had paragraphs longer than 100 words
        """
        if not self.soup:
            return False
        
        paragraphs = self.soup.find_all('p')
        for p in paragraphs:
            if len(p.get_text().split()) > 100:
                return True
        return False
    
    def _generate_revision_summary(self) -> Dict:
        """
        Create a comprehensive summary of all revisions that were applied.
        
        This summary helps users understand what the agent accomplished
        and what still requires manual attention. It provides both high-level
        categories and specific implementation details.
        
        Returns:
            Dict: Comprehensive summary of applied revisions and remaining work
        """
        return {
            "total_suggestions_analyzed": self._count_total_suggestions(),
            "suggestions_applied": len(self._get_applied_suggestions()),
            "revision_categories": {
                "microsoft_style_guide": "Applied contractions, simplified phrases, fixed capitalization",
                "structure_improvements": "Broke up long paragraphs, improved heading hierarchy",
                "ai_enhancements": "Enhanced clarity and active voice" if self.use_ai else "Not available (no Ollama)"
            },
            "automated_vs_manual": {
                "automated": "Microsoft Style Guide fixes, structure improvements",
                "requires_manual": "Adding examples, technical content updates, major restructuring"
            }
        }
    
    def _count_total_suggestions(self) -> int:
        """
        Count the total number of suggestions from the original analysis.
        
        This gives us a baseline to calculate what percentage of suggestions
        we were able to address automatically.
        
        Returns:
            int: Total number of suggestions across all analysis categories
        """
        total = 0
        for section in ['readability', 'structure', 'completeness', 'style_guidelines']:
            suggestions = self.suggestions.get(section, {}).get('suggestions', [])
            total += len(suggestions)
        return total

def main():
    """
    Command-line interface for the revision agent.
    
    This allows users to run the revision agent independently or as part
    of a larger workflow. It supports various output formats and AI model
    configurations for maximum flexibility.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Revise documentation based on analysis suggestions')
    parser.add_argument('url', help='URL of the documentation article to revise')
    parser.add_argument('--ollama-model', help='Ollama model name for AI-assisted revisions')
    parser.add_argument('--ollama-url', help='Ollama server URL for AI-assisted revisions')
    parser.add_argument('--output', choices=['json', 'html'], default='json', help='Output format')
    args = parser.parse_args()
    
    # Create revision agent with user-specified configuration
    agent = DocumentationRevisionAgent(ollama_model=args.ollama_model, ollama_url=args.ollama_url)
    
    print(f"Processing article: {args.url}")
    result = agent.process_document(args.url)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    if args.output == 'json':
        # Output just the key results in JSON format for programmatic use
        print(json.dumps({
            "url": result["url"],
            "suggestions_applied": result["suggestions_applied"],
            "revision_summary": result["revision_summary"]
        }, indent=2))
    else:
        # Save the complete revised HTML for human review
        with open('revised_article.html', 'w', encoding='utf-8') as f:
            f.write(result["revised_content"])
        print("Revised article saved to 'revised_article.html'")
        print(f"Applied {len(result['suggestions_applied'])} suggestion categories")

if __name__ == "__main__":
    main() 