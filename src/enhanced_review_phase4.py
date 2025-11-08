from interactive.chat_interface import InteractiveChatbot
from testing.test_generator import TestGenerator
from documentation.doc_generator import DocumentationGenerator
from performance.profiler import PerformanceProfiler
from quality.smell_detector import CodeSmellDetector
from search.semantic_search import SemanticCodeSearch

class EnhancedReviewPhase4:
    """Phase 4 advanced features"""
    
    def __init__(self):
        self.chatbot = InteractiveChatbot()
        self.test_gen = TestGenerator()
        self.doc_gen = DocumentationGenerator()
        self.profiler = PerformanceProfiler()
        self.smell_detector = CodeSmellDetector()
        self.semantic_search = SemanticCodeSearch()
    
    def comprehensive_review(self, code: str, language: str, file_path: str) -> Dict:
        """Run comprehensive Phase 4 review"""
        
        results = {}
        
        # Performance analysis
        results['performance'] = self.profiler.analyze_performance(code, language)
        
        # Code smell detection
        results['code_smells'] = self.smell_detector.run_all_detections(code)
        
        # Generate tests
        results['suggested_tests'] = self.test_gen.generate_tests(code, language)
        
        # Generate documentation
        results['documentation'] = self.doc_gen.generate_docstring(code, language)
        
        # Detect duplicates
        self.semantic_search.index_codebase({file_path: code})
        results['duplicates'] = self.semantic_search.detect_duplicate_logic()
        
        return results
    
    def interactive_session(self, code: str, issue: str) -> str:
        """Start interactive Q&A session"""
        self.chatbot.start_conversation(code, issue)
        return "Interactive session started. Use ask_question() method."

if __name__ == "__main__":
    reviewer = EnhancedReviewPhase4()
    print("Phase 4 Advanced Features Ready")
