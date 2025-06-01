import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Tuple
import textstat
from urllib.parse import urlparse
import nltk
from collections import Counter
import argparse

# Download the NLTK sentence tokenizer if we don't have it yet
# This happens automatically the first time you run the script
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class DocumentationAnalyzer:
    """
    Analyzes MoEngage docs to see how marketer-friendly they are.
    
    We check four main things:
    1. Readability - Can marketers actually understand this?
    2. Structure - Is it organized well or a wall of text?
    3. Completeness - Missing examples? Screenshots? Step-by-step guides?
    4. Style - Following Microsoft's style guide (they know what they're doing)
    
    Spits out scores and tells you exactly what to fix.
    """
    
    def __init__(self):
        # Start with nothing - we'll load content when fetch_article() is called
        self.url = None
        self.content = None  # Raw HTML from the page
        self.soup = None     # BeautifulSoup parsed version
        self.text_content = None  # Just the text, no HTML tags
        
    def fetch_article(self, url: str) -> bool:
        """
        Grabs the article from a URL and gets it ready for analysis.
        
        Works best with MoEngage docs but will try other sites too.
        Returns True if it worked, False if something went wrong.
        """
        try:
            # Quick check - is this actually a MoEngage URL?
            parsed = urlparse(url)
            if 'help.moengage.com' not in parsed.netloc:
                print(f"Heads up: {url} isn't MoEngage docs, but I'll try anyway")
            
            # Pretend to be a real browser so we don't get blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Crash if we get a 404 or something
            
            # Save everything we got
            self.url = url
            self.content = response.text
            self.soup = BeautifulSoup(self.content, 'html.parser')
            
            # Try to find just the actual article content (skip navigation, footer, etc.)
            article_body = self.soup.find('article') or self.soup.find('div', class_='article-body')
            if article_body:
                self.text_content = article_body.get_text(separator=' ', strip=True)
            else:
                # Couldn't find an article container, just grab all the text
                self.text_content = self.soup.get_text(separator=' ', strip=True)
            
            return True
            
        except Exception as e:
            print(f"Couldn't fetch the article: {e}")
            return False
    
    def analyze_readability(self) -> Dict:
        """
        Figures out if marketers can actually read and understand this content.
        
        Uses real readability formulas plus some custom checks for tech jargon
        that might confuse non-developers.
        """
        if not self.text_content:
            return {"error": "No content to analyze"}
        
        # Run the standard readability tests
        flesch_score = textstat.flesch_reading_ease(self.text_content)  # 0-100, higher = easier
        fog_score = textstat.gunning_fog(self.text_content)  # Years of education needed
        avg_sentence_length = textstat.avg_sentence_length(self.text_content)
        
        # Look for scary technical terms
        technical_terms = self._identify_technical_terms()
        
        # Turn the Flesch score into something humans can understand
        readability_level = self._interpret_readability_score(flesch_score)
        
        # Bundle up all our findings
        assessment = {
            "flesch_reading_ease": flesch_score,
            "gunning_fog_index": fog_score,
            "average_sentence_length": avg_sentence_length,
            "readability_level": readability_level,
            "technical_terms_count": len(technical_terms)
        }
        
        suggestions = []
        
        # Give specific advice based on what we found
        if flesch_score < 60:  # Pretty hard to read
            suggestions.append(
                "The content has a low readability score (Flesch: {:.1f}). "
                "Consider simplifying sentences and using more common words to make it easier for marketers to understand."
                .format(flesch_score)
            )
        
        if avg_sentence_length > 20:
            suggestions.append(
                f"Average sentence length is {avg_sentence_length:.1f} words - that's pretty long! "
                "Try breaking sentences up. Aim for 15-20 words max."
            )
        
        if len(technical_terms) > 10:
            suggestions.append(
                f"Found {len(technical_terms)} technical terms that might confuse marketers. "
                f"Maybe add a glossary or explain terms like: {', '.join(list(technical_terms)[:5])}"
            )
        
        # Find the worst offender sentences
        difficult_sentences = self._find_difficult_sentences()
        if difficult_sentences:
            suggestions.append(
                "These sentences are particularly gnarly and should be simplified:\n" +
                "\n".join(f"- \"{sent[:100]}...\"" for sent in difficult_sentences[:3])
            )
        
        return {
            "assessment": assessment,
            "explanation": self._explain_readability(readability_level, flesch_score),
            "suggestions": suggestions
        }
    
    def analyze_structure(self) -> Dict:
        """
        Checks if the article is well-organized or just a blob of text.
        """
        if not self.soup:
            return {"error": "No content to analyze"}
        
        # Count up all the structural elements
        headings = self._extract_headings()
        paragraphs = self.soup.find_all('p')
        lists = self.soup.find_all(['ul', 'ol'])
        code_blocks = self.soup.find_all(['code', 'pre'])
        images = self.soup.find_all('img')
        
        # Check paragraph lengths - nobody likes walls of text
        paragraph_lengths = [len(p.get_text().split()) for p in paragraphs if p.get_text().strip()]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        assessment = {
            "headings_count": len(headings),
            "paragraphs_count": len(paragraphs),
            "lists_count": len(lists),
            "code_blocks_count": len(code_blocks),
            "images_count": len(images),
            "average_paragraph_length": avg_paragraph_length,
            "heading_hierarchy": self._check_heading_hierarchy(headings)
        }
        
        suggestions = []
        
        # Not enough headings = hard to scan
        if len(headings) < 3:
            suggestions.append(
                "This article needs more headings! Add subheadings to break up the content "
                "and make it easier to skim."
            )
        
        if not assessment["heading_hierarchy"]["is_valid"]:
            suggestions.append(
                "Heading hierarchy is inconsistent. " + assessment["heading_hierarchy"]["issue"]
            )
        
        # Check paragraph lengths
        if avg_paragraph_length > 100:
            suggestions.append(
                f"Average paragraph length is {avg_paragraph_length:.0f} words, which is quite long. "
                "Consider breaking up long paragraphs into smaller chunks (aim for 50-75 words)."
            )
        
        # Check for lists usage
        if len(lists) == 0 and len(paragraphs) > 5:
            suggestions.append(
                "No lists found in the article. Consider using bullet points or numbered lists "
                "to present steps, features, or options more clearly."
            )
        
        # Check logical flow
        flow_issues = self._analyze_content_flow(headings)
        if flow_issues:
            suggestions.extend(flow_issues)
        
        return {
            "assessment": assessment,
            "suggestions": suggestions
        }
    
    def analyze_completeness(self) -> Dict:
        """
        Analyzes the completeness of information and examples.
        
        Returns:
            Dict containing completeness assessment and suggestions
        """
        if not self.soup:
            return {"error": "No content to analyze"}
        
        # Look for examples, code snippets, and visual aids
        code_examples = self.soup.find_all(['code', 'pre'])
        images = self.soup.find_all('img')
        
        # Look for common example indicators
        example_indicators = ['example', 'for instance', 'such as', 'e.g.', 'sample', 'scenario']
        example_count = sum(1 for indicator in example_indicators 
                          if indicator.lower() in self.text_content.lower())
        
        # Check for step-by-step instructions
        numbered_lists = self.soup.find_all('ol')
        has_steps = len(numbered_lists) > 0 or bool(re.search(r'step \d+', self.text_content, re.IGNORECASE))
        
        # Look for warnings, notes, tips
        alerts = self.soup.find_all(['div', 'aside'], class_=re.compile('alert|note|tip|warning'))
        
        assessment = {
            "code_examples_count": len(code_examples),
            "images_count": len(images),
            "example_mentions": example_count,
            "has_step_by_step": has_steps,
            "alerts_count": len(alerts)
        }
        
        suggestions = []
        
        # Check for examples
        if example_count < 2 and len(code_examples) < 1:
            suggestions.append(
                "The article lacks concrete examples. Add practical examples showing how marketers "
                "would actually use this feature in real scenarios."
            )
        
        # Check for visual aids
        if len(images) == 0:
            suggestions.append(
                "No images or screenshots found. Consider adding visual aids to illustrate the UI, "
                "workflow, or results. Screenshots are especially helpful for non-technical users."
            )
        
        # Check for prerequisites
        if not self._check_prerequisites():
            suggestions.append(
                "The article doesn't clearly state prerequisites or required knowledge. "
                "Add a 'Prerequisites' or 'Before you begin' section."
            )
        
        # Check for common use cases
        if not self._check_use_cases():
            suggestions.append(
                "Consider adding a 'Common Use Cases' section to help marketers understand "
                "when and why they would use this feature."
            )
        
        # Specific example suggestions
        missing_examples = self._identify_missing_examples()
        if missing_examples:
            suggestions.extend(missing_examples)
        
        return {
            "assessment": assessment,
            "suggestions": suggestions
        }
    
    def analyze_style_guidelines(self) -> Dict:
        """
        Analyzes adherence to style guidelines focusing on voice, clarity, and action-oriented language.
        
        Returns:
            Dict containing style assessment and suggestions
        """
        if not self.text_content:
            return {"error": "No content to analyze"}
        
        # Analyze voice and tone
        voice_analysis = self._analyze_voice_and_tone()
        
        # Check for clarity and conciseness
        clarity_issues = self._check_clarity_and_conciseness()
        
        # Check for action-oriented language
        action_analysis = self._analyze_action_orientation()
        
        # Microsoft Style Guide specific checks
        microsoft_style_issues = self._check_microsoft_style_guide()
        
        assessment = {
            "voice_tone": voice_analysis,
            "clarity": clarity_issues,
            "action_orientation": action_analysis,
            "microsoft_style": microsoft_style_issues
        }
        
        suggestions = []
        
        # Voice and tone suggestions
        if voice_analysis["passive_voice_percentage"] > 20:
            suggestions.append(
                f"HIGH PRIORITY: High use of passive voice ({voice_analysis['passive_voice_percentage']:.1f}%). "
                "Convert passive constructions to active voice for clearer, more direct communication. "
                f"Examples: {', '.join(voice_analysis['passive_examples'][:2])}"
            )
        
        if voice_analysis["first_person_count"] > 5:
            suggestions.append(
                "MEDIUM PRIORITY: Avoid first-person pronouns (I, we, our). Use second-person (you, your) "
                "to speak directly to the reader."
            )
        
        # Clarity suggestions
        for issue in clarity_issues:
            suggestions.append(f"MEDIUM PRIORITY: {issue}")
        
        # Action-oriented suggestions
        if action_analysis["weak_verbs_count"] > 5:
            suggestions.append(
                "MEDIUM PRIORITY: Replace weak verbs with strong, action-oriented alternatives. "
                f"Examples: {', '.join(action_analysis['weak_verb_examples'][:3])}"
            )
        
        if not action_analysis["has_clear_actions"]:
            suggestions.append(
                "HIGH PRIORITY: Add clear action statements. Start sentences with imperative verbs "
                "(Click, Select, Navigate, Configure) to guide users effectively."
            )
        
        # Microsoft Style Guide suggestions
        for category, issues in microsoft_style_issues.items():
            if issues["count"] > 0:
                priority = "HIGH" if issues["count"] > 5 else "MEDIUM"
                suggestions.append(f"{priority} PRIORITY: {issues['message']}")
                if issues["examples"]:
                    suggestions.append(f"  Examples: {'; '.join(issues['examples'][:3])}")
        
        return {
            "assessment": assessment,
            "suggestions": suggestions
        }
    
    def generate_report(self) -> Dict:
        """
        Generates the complete analysis report.
        
        Returns:
            Dict containing the full structured report
        """
        if not self.url:
            return {"error": "No article has been analyzed"}
        
        report = {
            "url": self.url,
            "analysis_timestamp": self._get_timestamp(),
            "readability": self.analyze_readability(),
            "structure": self.analyze_structure(),
            "completeness": self.analyze_completeness(),
            "style_guidelines": self.analyze_style_guidelines()
        }
        
        # Add overall recommendations
        report["overall_recommendations"] = self._generate_overall_recommendations(report)
        
        return report
    
    # Helper methods
    def _identify_technical_terms(self) -> set:
        """Identifies potential technical terms in the content."""
        # Common technical terms in marketing automation
        tech_terms = {
            'api', 'sdk', 'json', 'webhook', 'payload', 'endpoint', 'integration',
            'script', 'code', 'database', 'query', 'parameter', 'variable',
            'authentication', 'token', 'oauth', 'rest', 'http', 'https'
        }
        
        words = re.findall(r'\b\w+\b', self.text_content.lower())
        found_terms = set()
        
        for word in words:
            if word in tech_terms or len(word) > 15:  # Long words are often technical
                found_terms.add(word)
        
        return found_terms
    
    def _interpret_readability_score(self, score: float) -> str:
        """Interprets Flesch reading ease score."""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _explain_readability(self, level: str, score: float) -> str:
        """Provides detailed explanation of readability for marketers."""
        explanations = {
            "Very Easy": "The content is very easy to read and understand, suitable for all marketers regardless of technical background.",
            "Easy": "The content is easy to read with simple language that most marketers will find accessible.",
            "Fairly Easy": "The content is reasonably easy to read, though some sections may require careful attention.",
            "Standard": "The content has average readability. Non-technical marketers may need to read some sections twice.",
            "Fairly Difficult": "The content is somewhat difficult to read. Consider simplifying language and sentence structure.",
            "Difficult": "The content is difficult to read and may be too technical for many marketers.",
            "Very Difficult": "The content is very difficult to read and likely too complex for non-technical marketers."
        }
        
        return f"{explanations.get(level, 'Unknown readability level')} (Flesch score: {score:.1f})"
    
    def _find_difficult_sentences(self) -> List[str]:
        """Finds sentences that are particularly difficult to read."""
        sentences = nltk.sent_tokenize(self.text_content)
        difficult = []
        
        for sent in sentences:
            word_count = len(sent.split())
            if word_count > 30:  # Long sentences
                difficult.append(sent)
            elif textstat.flesch_reading_ease(sent) < 30:  # Complex sentences
                difficult.append(sent)
        
        return difficult[:5]  # Return top 5 most difficult
    
    def _extract_headings(self) -> List[Tuple[str, int]]:
        """Extracts all headings with their levels."""
        headings = []
        for i in range(1, 7):
            for h in self.soup.find_all(f'h{i}'):
                headings.append((h.get_text(strip=True), i))
        return headings
    
    def _check_heading_hierarchy(self, headings: List[Tuple[str, int]]) -> Dict:
        """Checks if heading hierarchy is logical."""
        if not headings:
            return {"is_valid": True, "issue": None}
        
        prev_level = headings[0][1]
        for text, level in headings[1:]:
            if level > prev_level + 1:  # Skipped a level
                return {
                    "is_valid": False,
                    "issue": f"Heading hierarchy jumps from H{prev_level} to H{level}. Use sequential heading levels."
                }
            prev_level = level
        
        return {"is_valid": True, "issue": None}
    
    def _analyze_content_flow(self, headings: List[Tuple[str, int]]) -> List[str]:
        """Analyzes logical flow of content based on headings."""
        issues = []
        
        # Check for logical progression
        heading_texts = [h[0].lower() for h in headings]
        
        # Common logical flows
        setup_before_usage = any('setup' in h or 'configure' in h for h in heading_texts)
        usage_section = any('use' in h or 'using' in h for h in heading_texts)
        
        if usage_section and not setup_before_usage:
            issues.append(
                "Consider adding a 'Setup' or 'Configuration' section before explaining usage."
            )
        
        # Check for conclusion or next steps
        has_conclusion = any('conclusion' in h or 'next' in h or 'summary' in h for h in heading_texts)
        if len(headings) > 5 and not has_conclusion:
            issues.append(
                "Consider adding a 'Next Steps' or 'Summary' section to conclude the article."
            )
        
        return issues
    
    def _check_prerequisites(self) -> bool:
        """Checks if prerequisites are mentioned."""
        prereq_keywords = ['prerequisite', 'before you begin', 'requirements', 'need to', 'must have']
        return any(keyword in self.text_content.lower() for keyword in prereq_keywords)
    
    def _check_use_cases(self) -> bool:
        """Checks if use cases are mentioned."""
        use_case_keywords = ['use case', 'scenario', 'when to use', 'example scenario', 'common uses']
        return any(keyword in self.text_content.lower() for keyword in use_case_keywords)
    
    def _identify_missing_examples(self) -> List[str]:
        """Identifies where examples might be missing."""
        suggestions = []
        
        # Check for configuration without examples
        if 'configure' in self.text_content.lower() and not self._has_configuration_example():
            suggestions.append(
                "Add a configuration example showing actual values a marketer would use."
            )
        
        # Check for API/integration mentions without examples
        if ('api' in self.text_content.lower() or 'integration' in self.text_content.lower()) and len(self.soup.find_all('code')) < 2:
            suggestions.append(
                "API or integration mentioned but lacks code examples. Add practical examples with sample data."
            )
        
        return suggestions
    
    def _has_configuration_example(self) -> bool:
        """Checks if configuration examples exist."""
        code_blocks = self.soup.find_all(['code', 'pre'])
        return any('config' in str(block).lower() for block in code_blocks)
    
    def _analyze_voice_and_tone(self) -> Dict:
        """Analyzes voice and tone of the content."""
        sentences = nltk.sent_tokenize(self.text_content)
        
        # Check for passive voice
        passive_count = 0
        passive_examples = []
        passive_indicators = ['is being', 'was being', 'has been', 'have been', 'had been', 'will be', 'will have been', 'being', 'been']
        
        for sent in sentences:
            if any(indicator in sent.lower() for indicator in passive_indicators):
                passive_count += 1
                passive_examples.append(sent[:50] + "...")
        
        # Check for first person usage
        first_person = ['i ', 'we ', 'our ', 'us ', 'me ']
        first_person_count = sum(1 for word in first_person if word in self.text_content.lower())
        
        return {
            "passive_voice_percentage": (passive_count / len(sentences)) * 100 if sentences else 0,
            "passive_examples": passive_examples[:3],
            "first_person_count": first_person_count
        }
    
    def _check_clarity_and_conciseness(self) -> List[str]:
        """Checks for clarity and conciseness issues."""
        issues = []
        
        # Check for wordy phrases
        wordy_phrases = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'in the event that': 'if',
            'at this point in time': 'now',
            'for the purpose of': 'to'
        }
        
        for wordy, concise in wordy_phrases.items():
            if wordy in self.text_content.lower():
                issues.append(f"Replace '{wordy}' with '{concise}' for conciseness.")
        
        # Check for complex words
        complex_words = re.findall(r'\b\w{15,}\b', self.text_content)
        if len(complex_words) > 10:
            issues.append(
                f"Found {len(complex_words)} very long words (15+ characters). "
                "Consider using simpler alternatives where possible."
            )
        
        return issues
    
    def _analyze_action_orientation(self) -> Dict:
        """Analyzes if content uses action-oriented language."""
        # Check for weak verbs
        weak_verbs = ['can', 'could', 'may', 'might', 'should']
        weak_verb_count = 0
        weak_examples = []
        
        sentences = nltk.sent_tokenize(self.text_content)
        for sent in sentences:
            for verb in weak_verbs:
                if f' {verb} ' in sent.lower():
                    weak_verb_count += 1
                    weak_examples.append(f"'{verb}' in: {sent[:50]}...")
        
        # Check for imperative sentences (action-oriented)
        imperative_count = sum(1 for sent in sentences if sent.strip() and sent.split()[0][0].isupper() and not sent.split()[0].endswith('.'))
        
        return {
            "weak_verbs_count": weak_verb_count,
            "weak_verb_examples": weak_examples[:5],
            "has_clear_actions": imperative_count > 3
        }
    
    def _get_timestamp(self) -> str:
        """Returns current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_overall_recommendations(self, report: Dict) -> List[str]:
        """Generates overall recommendations based on all analyses."""
        recommendations = []
        
        # Priority 1: Readability issues
        if report['readability'].get('assessment', {}).get('flesch_reading_ease', 100) < 60:
            recommendations.append("HIGH PRIORITY: Improve readability by simplifying language and sentence structure.")
        
        # Priority 2: Missing examples
        if report['completeness'].get('assessment', {}).get('example_mentions', 0) < 2:
            recommendations.append("HIGH PRIORITY: Add practical examples to illustrate concepts.")
        
        # Priority 3: Microsoft Style Guide compliance
        microsoft_issues = report.get('style_guidelines', {}).get('assessment', {}).get('microsoft_style', {})
        total_style_issues = sum(issues.get('count', 0) for issues in microsoft_issues.values())
        
        if total_style_issues > 15:
            recommendations.append("HIGH PRIORITY: Address Microsoft Style Guide violations for better user experience.")
        elif total_style_issues > 5:
            recommendations.append("MEDIUM PRIORITY: Improve compliance with Microsoft Style Guide principles.")
        
        # Priority 4: Structure issues
        if report['structure'].get('assessment', {}).get('headings_count', 0) < 3:
            recommendations.append("MEDIUM PRIORITY: Improve article structure with more headings and sections.")
        
        # Priority 5: Weak writing constructions
        weak_constructions = microsoft_issues.get('weak_constructions', {}).get('count', 0)
        if weak_constructions > 5:
            recommendations.append("MEDIUM PRIORITY: Replace weak writing constructions with direct, action-oriented language.")
        
        # Priority 6: Voice and tone
        if report['style_guidelines'].get('assessment', {}).get('voice_tone', {}).get('passive_voice_percentage', 0) > 20:
            recommendations.append("MEDIUM PRIORITY: Revise passive voice constructions to active voice.")
        
        return recommendations
    
    def _check_microsoft_style_guide(self) -> Dict:
        """Comprehensive Microsoft Style Guide compliance check."""
        return {
            "verbose_phrases": self._check_verbose_phrases(),
            "missing_contractions": self._check_contractions(),
            "title_capitalization": self._check_capitalization(),
            "unnecessary_punctuation": self._check_heading_punctuation(),
            "oxford_comma": self._check_oxford_comma(),
            "spacing_issues": self._check_spacing(),
            "weak_constructions": self._check_weak_constructions(),
            "jargon_usage": self._check_jargon_and_technical_language()
        }
    
    def _check_verbose_phrases(self) -> Dict:
        """Check for verbose phrases that can be simplified (Use bigger ideas, fewer words)."""
        verbose_replacements = {
            'if you\'re ready to purchase': 'ready to buy',
            'contact your account representative': 'contact us',
            'in order to': 'to',
            'due to the fact that': 'because',
            'in the event that': 'if',
            'at this point in time': 'now',
            'for the purpose of': 'to',
            'with regard to': 'about',
            'in spite of the fact that': 'although',
            'until such time as': 'until',
            'as a result of': 'because',
            'prior to': 'before',
            'subsequent to': 'after',
            'in addition to': 'besides',
            'a large number of': 'many',
            'a great deal of': 'much',
            'on a regular basis': 'regularly',
            'make a decision': 'decide',
            'give consideration to': 'consider',
            'it is important to note that': '',
            'please be aware that': '',
            'it should be noted that': ''
        }
        
        issues = []
        count = 0
        
        text_lower = self.text_content.lower()
        for verbose, concise in verbose_replacements.items():
            if verbose in text_lower:
                count += 1
                replacement = f"'{concise}'" if concise else "remove entirely"
                issues.append(f"Replace '{verbose}' with {replacement}")
        
        return {
            "count": count,
            "examples": issues[:5],
            "message": f"Found {count} verbose phrases that can be simplified for clearer communication."
        }
    
    def _check_contractions(self) -> Dict:
        """Check for missing contractions (Project friendliness)."""
        contraction_pairs = [
            ('it is', "it's"),
            ('you are', "you're"),
            ('you will', "you'll"),
            ('we are', "we're"),
            ('let us', "let's"),
            ('do not', "don't"),
            ('will not', "won't"),
            ('cannot', "can't"),
            ('should not', "shouldn't"),
            ('would not', "wouldn't"),
            ('could not', "couldn't"),
            ('that is', "that's"),
            ('there is', "there's"),
            ('what is', "what's"),
            ('who is', "who's"),
            ('where is', "where's")
        ]
        
        issues = []
        count = 0
        
        sentences = nltk.sent_tokenize(self.text_content)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for formal, contracted in contraction_pairs:
                if formal in sentence_lower and contracted not in sentence_lower:
                    count += 1
                    issues.append(f"Use '{contracted}' instead of '{formal}' in: {sentence[:50]}...")
                    break  # Only count once per sentence
        
        return {
            "count": count,
            "examples": issues[:5],
            "message": f"Found {count} opportunities to use contractions for a friendlier tone."
        }
    
    def _check_capitalization(self) -> Dict:
        """Check for title case instead of sentence case (When in doubt, don't capitalize)."""
        headings = self._extract_headings()
        issues = []
        count = 0
        
        for heading_text, level in headings:
            # Skip if it's a proper noun or contains proper nouns
            words = heading_text.split()
            if len(words) <= 1:
                continue
                
            # Check if multiple words are capitalized (Title Case)
            capitalized_words = [word for word in words if word[0].isupper() and word.lower() not in ['api', 'ui', 'id']]
            
            if len(capitalized_words) > 1:  # More than just the first word
                count += 1
                issues.append(f"Use sentence case: '{heading_text}' → '{heading_text[0].upper() + heading_text[1:].lower()}'")
        
        return {
            "count": count,
            "examples": issues[:5],
            "message": f"Found {count} headings using title case instead of sentence case."
        }
    
    def _check_heading_punctuation(self) -> Dict:
        """Check for unnecessary punctuation in headings (Skip periods)."""
        headings = self._extract_headings()
        issues = []
        count = 0
        
        for heading_text, level in headings:
            # Check for end punctuation in short headings
            if len(heading_text.split()) <= 3 and heading_text.endswith(('.', '!', '?', ':')):
                count += 1
                clean_heading = heading_text.rstrip('.!?:')
                issues.append(f"Remove punctuation: '{heading_text}' → '{clean_heading}'")
        
        return {
            "count": count,
            "examples": issues[:5],
            "message": f"Found {count} headings with unnecessary end punctuation."
        }
    
    def _check_oxford_comma(self) -> Dict:
        """Check for missing Oxford commas (Remember the last comma)."""
        # Pattern to find lists of 3+ items without Oxford comma
        pattern = r'\b\w+,\s+\w+\s+and\s+\w+\b'
        matches = re.findall(pattern, self.text_content)
        
        issues = []
        for match in matches:
            # Suggest adding Oxford comma
            corrected = match.replace(' and ', ', and ')
            issues.append(f"Add Oxford comma: '{match}' → '{corrected}'")
        
        return {
            "count": len(matches),
            "examples": issues[:5],
            "message": f"Found {len(matches)} lists missing Oxford commas."
        }
    
    def _check_spacing(self) -> Dict:
        """Check for spacing issues (Don't be spacey)."""
        issues = []
        count = 0
        
        # Check for double spaces after punctuation
        double_spaces = re.findall(r'[.!?]\s{2,}', self.text_content)
        if double_spaces:
            count += len(double_spaces)
            issues.append(f"Use single space after periods: found {len(double_spaces)} instances of double spacing")
        
        # Check for spaces around dashes
        spaced_dashes = re.findall(r'\s+—\s+|\s+-\s+', self.text_content)
        if spaced_dashes:
            count += len(spaced_dashes)
            issues.append(f"Remove spaces around dashes: found {len(spaced_dashes)} instances")
        
        return {
            "count": count,
            "examples": issues,
            "message": f"Found {count} spacing issues that need correction."
        }
    
    def _check_weak_constructions(self) -> Dict:
        """Check for weak writing constructions (Revise weak writing)."""
        weak_patterns = [
            (r'\byou can\b', "Start with action verb instead of 'you can'"),
            (r'\bthere is\b|\bthere are\b|\bthere were\b', "Replace 'there is/are/were' with active construction"),
            (r'\bit is possible to\b', "Replace 'it is possible to' with direct action"),
            (r'\bit is important to\b', "Replace 'it is important to' with direct instruction"),
            (r'\byou should\b', "Use imperative: replace 'you should' with direct command"),
            (r'\byou need to\b', "Use imperative: replace 'you need to' with direct command")
        ]
        
        issues = []
        count = 0
        
        for pattern, suggestion in weak_patterns:
            matches = re.findall(pattern, self.text_content, re.IGNORECASE)
            if matches:
                count += len(matches)
                issues.append(f"{suggestion} (found {len(matches)} instances)")
        
        return {
            "count": count,
            "examples": issues,
            "message": f"Found {count} weak writing constructions that should be revised."
        }
    
    def _check_jargon_and_technical_language(self) -> Dict:
        """Enhanced jargon detection (Write like you speak)."""
        # Technical jargon that should be explained
        jargon_terms = {
            'api': 'Application Programming Interface (API)',
            'sdk': 'Software Development Kit (SDK)',
            'webhook': 'automated message sent between systems',
            'endpoint': 'connection point',
            'payload': 'data package',
            'authentication': 'identity verification',
            'oauth': 'secure login method',
            'json': 'data format',
            'rest': 'web service standard',
            'crud': 'create, read, update, delete operations',
            'uuid': 'unique identifier',
            'regex': 'text pattern matching',
            'ssl': 'secure connection',
            'cdn': 'content delivery network'
        }
        
        found_jargon = []
        words = re.findall(r'\b\w+\b', self.text_content.lower())
        
        for word in set(words):
            if word in jargon_terms:
                found_jargon.append(f"'{word}' should be explained as '{jargon_terms[word]}'")
        
        return {
            "count": len(found_jargon),
            "examples": found_jargon[:5],
            "message": f"Found {len(found_jargon)} technical terms that need explanation for non-technical users."
        }


def main():
    parser = argparse.ArgumentParser(description='Analyze MoEngage documentation for improvements')
    parser.add_argument('url', help='URL of the MoEngage documentation article to analyze')
    parser.add_argument('--output', choices=['json', 'text'], default='json', help='Output format')
    args = parser.parse_args()
    
    analyzer = DocumentationAnalyzer()
    
    print(f"Fetching article from: {args.url}")
    if not analyzer.fetch_article(args.url):
        print("Failed to fetch article")
        return
    
    print("Analyzing article...")
    report = analyzer.generate_report()
    
    if args.output == 'json':
        print(json.dumps(report, indent=2))
    else:
        # Text output
        print("\n" + "="*80)
        print(f"DOCUMENTATION ANALYSIS REPORT")
        print(f"URL: {report['url']}")
        print(f"Analyzed: {report['analysis_timestamp']}")
        print("="*80)
        
        sections = ['readability', 'structure', 'completeness', 'style_guidelines']
        section_titles = {
            'readability': 'READABILITY ANALYSIS',
            'structure': 'STRUCTURE & FLOW ANALYSIS',
            'completeness': 'COMPLETENESS & EXAMPLES ANALYSIS',
            'style_guidelines': 'STYLE GUIDELINES ANALYSIS'
        }
        
        for section in sections:
            print(f"\n{section_titles[section]}")
            print("-"*40)
            
            if 'error' in report[section]:
                print(f"Error: {report[section]['error']}")
                continue
            
            # Print assessment
            if 'assessment' in report[section]:
                print("Assessment:")
                for key, value in report[section]['assessment'].items():
                    if isinstance(value, dict):
                        print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
            
            # Print explanation if available
            if 'explanation' in report[section]:
                print(f"\nExplanation: {report[section]['explanation']}")
            
            # Print suggestions
            if 'suggestions' in report[section] and report[section]['suggestions']:
                print("\nSuggestions:")
                for i, suggestion in enumerate(report[section]['suggestions'], 1):
                    print(f"{i}. {suggestion}")
        
        # Print overall recommendations
        if 'overall_recommendations' in report and report['overall_recommendations']:
            print("\n" + "="*80)
            print("OVERALL RECOMMENDATIONS")
            print("="*80)
            for rec in report['overall_recommendations']:
                print(f"• {rec}")
            print()


if __name__ == "__main__":
    main()
