#!/usr/bin/env python3
"""
Test script for the Documentation Analyzer

Just makes sure everything's working properly before you start
using it on real documentation.
"""

import unittest
from documentation_analyzer import DocumentationAnalyzer
import json

class TestDocumentationAnalyzer(unittest.TestCase):
    """Basic tests to make sure the analyzer isn't broken"""
    
    def setUp(self):
        """Get ready for each test"""
        self.analyzer = DocumentationAnalyzer()
        # Use a working MoEngage URL for testing
        self.test_url = "https://help.moengage.com/hc/en-us/articles/23072207451540-Discontinuation-of-Mi-Push-Service#h_01HMRTTR1Y5HBZW390A7S3HAFB"
    
    def test_initialization(self):
        """Make sure the analyzer starts up clean"""
        self.assertIsNone(self.analyzer.url)
        self.assertIsNone(self.analyzer.content)
        self.assertIsNone(self.analyzer.soup)
        self.assertIsNone(self.analyzer.text_content)
    
    def test_fetch_article(self):
        """Test that we can actually grab articles from URLs"""
        # Try with a good URL
        result = self.analyzer.fetch_article(self.test_url)
        self.assertTrue(result)
        self.assertIsNotNone(self.analyzer.content)
        self.assertIsNotNone(self.analyzer.soup)
        self.assertIsNotNone(self.analyzer.text_content)
        
        # Try with a bad URL
        analyzer2 = DocumentationAnalyzer()
        result = analyzer2.fetch_article("https://invalid-url-that-does-not-exist.com")
        self.assertFalse(result)
    
    def test_readability_analysis(self):
        """Check that readability analysis actually works"""
        # Grab an article first
        self.analyzer.fetch_article(self.test_url)
        
        # Run readability analysis
        readability = self.analyzer.analyze_readability()
        
        # Make sure we get the right structure back
        self.assertIn('assessment', readability)
        self.assertIn('explanation', readability)
        self.assertIn('suggestions', readability)
        
        # Check that assessment has all the scores we expect
        assessment = readability['assessment']
        self.assertIn('flesch_reading_ease', assessment)
        self.assertIn('gunning_fog_index', assessment)
        self.assertIn('average_sentence_length', assessment)
        self.assertIn('readability_level', assessment)
        self.assertIn('technical_terms_count', assessment)
        
        # Make sure the data types are right
        self.assertIsInstance(assessment['flesch_reading_ease'], (int, float))
        self.assertIsInstance(assessment['gunning_fog_index'], (int, float))
        self.assertIsInstance(assessment['average_sentence_length'], (int, float))
        self.assertIsInstance(assessment['readability_level'], str)
        self.assertIsInstance(assessment['technical_terms_count'], int)
        
        # Suggestions should be a list
        self.assertIsInstance(readability['suggestions'], list)
    
    def test_structure_analysis(self):
        """Test structure analysis functionality"""
        # Grab an article first
        self.analyzer.fetch_article(self.test_url)
        
        # Check structure
        structure = self.analyzer.analyze_structure()
        
        # Basic structure check
        self.assertIn('assessment', structure)
        self.assertIn('suggestions', structure)
        
        # Make sure we're counting everything we should
        assessment = structure['assessment']
        self.assertIn('headings_count', assessment)
        self.assertIn('paragraphs_count', assessment)
        self.assertIn('lists_count', assessment)
        self.assertIn('code_blocks_count', assessment)
        self.assertIn('images_count', assessment)
        self.assertIn('average_paragraph_length', assessment)
        self.assertIn('heading_hierarchy', assessment)
        
        # Type checking
        self.assertIsInstance(assessment['headings_count'], int)
        self.assertIsInstance(assessment['paragraphs_count'], int)
        self.assertIsInstance(assessment['lists_count'], int)
        self.assertIsInstance(assessment['code_blocks_count'], int)
        self.assertIsInstance(assessment['images_count'], int)
        self.assertIsInstance(assessment['average_paragraph_length'], (int, float))
        self.assertIsInstance(assessment['heading_hierarchy'], dict)
        
        # Suggestions should be a list
        self.assertIsInstance(structure['suggestions'], list)
    
    def test_completeness_analysis(self):
        """Make sure completeness analysis works"""
        # Grab an article first
        self.analyzer.fetch_article(self.test_url)
        
        # Check completeness
        completeness = self.analyzer.analyze_completeness()
        
        # Basic structure
        self.assertIn('assessment', completeness)
        self.assertIn('suggestions', completeness)
        
        # Should count examples, images, etc.
        assessment = completeness['assessment']
        self.assertIn('code_examples_count', assessment)
        self.assertIn('images_count', assessment)
        self.assertIn('example_mentions', assessment)
        self.assertIn('has_step_by_step', assessment)
        self.assertIn('alerts_count', assessment)
        
        # Type checking
        self.assertIsInstance(assessment['code_examples_count'], int)
        self.assertIsInstance(assessment['images_count'], int)
        self.assertIsInstance(assessment['example_mentions'], int)
        self.assertIsInstance(assessment['has_step_by_step'], bool)
        self.assertIsInstance(assessment['alerts_count'], int)
        
        # Suggestions should be a list
        self.assertIsInstance(completeness['suggestions'], list)
    
    def test_style_guidelines_analysis(self):
        """Test the Microsoft Style Guide checking"""
        # Grab an article first
        self.analyzer.fetch_article(self.test_url)
        
        # Check style
        style = self.analyzer.analyze_style_guidelines()
        
        # Basic structure
        self.assertIn('assessment', style)
        self.assertIn('suggestions', style)
        
        # Should analyze voice, clarity, action orientation
        assessment = style['assessment']
        self.assertIn('voice_tone', assessment)
        self.assertIn('clarity', assessment)
        self.assertIn('action_orientation', assessment)
        
        # Voice and tone checks
        voice_tone = assessment['voice_tone']
        self.assertIn('passive_voice_percentage', voice_tone)
        self.assertIn('passive_examples', voice_tone)
        self.assertIn('first_person_count', voice_tone)
        
        # Action orientation checks
        action = assessment['action_orientation']
        self.assertIn('weak_verbs_count', action)
        self.assertIn('weak_verb_examples', action)
        self.assertIn('has_clear_actions', action)
        
        # Suggestions should be a list
        self.assertIsInstance(style['suggestions'], list)
    
    def test_generate_report(self):
        """Test the full end-to-end report generation"""
        # Grab an article first
        self.analyzer.fetch_article(self.test_url)
        
        # Generate the complete report
        report = self.analyzer.generate_report()
        
        # Should have all the main sections
        self.assertIn('url', report)
        self.assertIn('analysis_timestamp', report)
        self.assertIn('readability', report)
        self.assertIn('structure', report)
        self.assertIn('completeness', report)
        self.assertIn('style_guidelines', report)
        self.assertIn('overall_recommendations', report)
        
        # URL should match what we passed in
        self.assertEqual(report['url'], self.test_url)
        
        # Overall recommendations should be a list
        self.assertIsInstance(report['overall_recommendations'], list)
        
        # Make sure we can serialize it to JSON (important for web interface)
        try:
            json_str = json.dumps(report)
            self.assertIsInstance(json_str, str)
        except Exception as e:
            self.fail(f"Report is not JSON serializable: {e}")


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