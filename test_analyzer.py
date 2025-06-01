#!/usr/bin/env python3
"""
Test script for the MoEngage Documentation Analyzer

This script tests various functionalities of the analyzer to ensure
it's working correctly.
"""

import unittest
from documentation_analyzer import DocumentationAnalyzer
import json

class TestDocumentationAnalyzer(unittest.TestCase):
    """Test cases for the Documentation Analyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = DocumentationAnalyzer()
        # Test with a working MoEngage documentation URL
        self.test_url = "https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service#h_01HMRTTR1Y5HBZW390A7S3HAFB"
    
    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsNone(self.analyzer.url)
        self.assertIsNone(self.analyzer.content)
        self.assertIsNone(self.analyzer.soup)
        self.assertIsNone(self.analyzer.text_content)
    
    def test_fetch_article(self):
        """Test article fetching"""
        # Test with valid URL
        result = self.analyzer.fetch_article(self.test_url)
        self.assertTrue(result)
        self.assertIsNotNone(self.analyzer.content)
        self.assertIsNotNone(self.analyzer.soup)
        self.assertIsNotNone(self.analyzer.text_content)
        
        # Test with invalid URL
        analyzer2 = DocumentationAnalyzer()
        result = analyzer2.fetch_article("https://invalid-url-that-does-not-exist.com")
        self.assertFalse(result)
    
    def test_readability_analysis(self):
        """Test readability analysis"""
        # First fetch an article
        self.analyzer.fetch_article(self.test_url)
        
        # Analyze readability
        readability = self.analyzer.analyze_readability()
        
        # Check structure
        self.assertIn('assessment', readability)
        self.assertIn('explanation', readability)
        self.assertIn('suggestions', readability)
        
        # Check assessment fields
        assessment = readability['assessment']
        self.assertIn('flesch_reading_ease', assessment)
        self.assertIn('gunning_fog_index', assessment)
        self.assertIn('average_sentence_length', assessment)
        self.assertIn('readability_level', assessment)
        self.assertIn('technical_terms_count', assessment)
        
        # Check data types
        self.assertIsInstance(assessment['flesch_reading_ease'], (int, float))
        self.assertIsInstance(assessment['gunning_fog_index'], (int, float))
        self.assertIsInstance(assessment['average_sentence_length'], (int, float))
        self.assertIsInstance(assessment['readability_level'], str)
        self.assertIsInstance(assessment['technical_terms_count'], int)
        
        # Check suggestions is a list
        self.assertIsInstance(readability['suggestions'], list)
    
    def test_structure_analysis(self):
        """Test structure analysis"""
        # First fetch an article
        self.analyzer.fetch_article(self.test_url)
        
        # Analyze structure
        structure = self.analyzer.analyze_structure()
        
        # Check structure
        self.assertIn('assessment', structure)
        self.assertIn('suggestions', structure)
        
        # Check assessment fields
        assessment = structure['assessment']
        self.assertIn('headings_count', assessment)
        self.assertIn('paragraphs_count', assessment)
        self.assertIn('lists_count', assessment)
        self.assertIn('code_blocks_count', assessment)
        self.assertIn('images_count', assessment)
        self.assertIn('average_paragraph_length', assessment)
        self.assertIn('heading_hierarchy', assessment)
        
        # Check data types
        self.assertIsInstance(assessment['headings_count'], int)
        self.assertIsInstance(assessment['paragraphs_count'], int)
        self.assertIsInstance(assessment['lists_count'], int)
        self.assertIsInstance(assessment['code_blocks_count'], int)
        self.assertIsInstance(assessment['images_count'], int)
        self.assertIsInstance(assessment['average_paragraph_length'], (int, float))
        self.assertIsInstance(assessment['heading_hierarchy'], dict)
        
        # Check suggestions is a list
        self.assertIsInstance(structure['suggestions'], list)
    
    def test_completeness_analysis(self):
        """Test completeness analysis"""
        # First fetch an article
        self.analyzer.fetch_article(self.test_url)
        
        # Analyze completeness
        completeness = self.analyzer.analyze_completeness()
        
        # Check structure
        self.assertIn('assessment', completeness)
        self.assertIn('suggestions', completeness)
        
        # Check assessment fields
        assessment = completeness['assessment']
        self.assertIn('code_examples_count', assessment)
        self.assertIn('images_count', assessment)
        self.assertIn('example_mentions', assessment)
        self.assertIn('has_step_by_step', assessment)
        self.assertIn('alerts_count', assessment)
        
        # Check data types
        self.assertIsInstance(assessment['code_examples_count'], int)
        self.assertIsInstance(assessment['images_count'], int)
        self.assertIsInstance(assessment['example_mentions'], int)
        self.assertIsInstance(assessment['has_step_by_step'], bool)
        self.assertIsInstance(assessment['alerts_count'], int)
        
        # Check suggestions is a list
        self.assertIsInstance(completeness['suggestions'], list)
    
    def test_style_guidelines_analysis(self):
        """Test style guidelines analysis"""
        # First fetch an article
        self.analyzer.fetch_article(self.test_url)
        
        # Analyze style
        style = self.analyzer.analyze_style_guidelines()
        
        # Check structure
        self.assertIn('assessment', style)
        self.assertIn('suggestions', style)
        
        # Check assessment fields
        assessment = style['assessment']
        self.assertIn('voice_tone', assessment)
        self.assertIn('clarity', assessment)
        self.assertIn('action_orientation', assessment)
        
        # Check voice_tone fields
        voice_tone = assessment['voice_tone']
        self.assertIn('passive_voice_percentage', voice_tone)
        self.assertIn('passive_examples', voice_tone)
        self.assertIn('first_person_count', voice_tone)
        
        # Check action_orientation fields
        action = assessment['action_orientation']
        self.assertIn('weak_verbs_count', action)
        self.assertIn('weak_verb_examples', action)
        self.assertIn('has_clear_actions', action)
        
        # Check suggestions is a list
        self.assertIsInstance(style['suggestions'], list)
    
    def test_generate_report(self):
        """Test full report generation"""
        # First fetch an article
        self.analyzer.fetch_article(self.test_url)
        
        # Generate report
        report = self.analyzer.generate_report()
        
        # Check main structure
        self.assertIn('url', report)
        self.assertIn('analysis_timestamp', report)
        self.assertIn('readability', report)
        self.assertIn('structure', report)
        self.assertIn('completeness', report)
        self.assertIn('style_guidelines', report)
        self.assertIn('overall_recommendations', report)
        
        # Check URL matches
        self.assertEqual(report['url'], self.test_url)
        
        # Check overall recommendations is a list
        self.assertIsInstance(report['overall_recommendations'], list)
        
        # Validate JSON serializable
        try:
            json_str = json.dumps(report)
            self.assertIsInstance(json_str, str)
        except Exception as e:
            self.fail(f"Report is not JSON serializable: {e}")
    
    def test_empty_content_handling(self):
        """Test handling of empty content"""
        # Try to analyze without fetching
        analyzer = DocumentationAnalyzer()
        
        readability = analyzer.analyze_readability()
        self.assertIn('error', readability)
        
        structure = analyzer.analyze_structure()
        self.assertIn('error', structure)
        
        completeness = analyzer.analyze_completeness()
        self.assertIn('error', completeness)
        
        style = analyzer.analyze_style_guidelines()
        self.assertIn('error', style)
        
        report = analyzer.generate_report()
        self.assertIn('error', report)


def run_validation_tests():
    """Run validation tests and print summary"""
    print("Running Documentation Analyzer Tests...\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDocumentationAnalyzer)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run validation tests
    success = run_validation_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1) 