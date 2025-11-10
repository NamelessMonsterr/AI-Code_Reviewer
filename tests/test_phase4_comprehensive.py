"""
Comprehensive tests for Phase 4 features:
- Interactive Chatbot
- Test Generator
- Documentation Generator
- Performance Profiler
- Code Smell Detector
- Semantic Search
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.interactive.chat_interface import InteractiveChatbot
from src.testing.test_generator import TestGenerator
from src.documentation.doc_generator import DocumentationGenerator
from src.performance.profiler import PerformanceProfiler
from src.quality.smell_detector import CodeSmellDetector
from src.search.semantic_search import SemanticCodeSearch


class TestInteractiveChatbot:
    """Tests for Interactive Chatbot"""

    @pytest.fixture
    def chatbot(self):
        with patch("src.interactive.chat_interface.OpenAI"):
            return InteractiveChatbot()

    def test_initialization(self, chatbot):
        """Test chatbot initialization"""
        assert chatbot.conversation_history == []

    def test_start_conversation(self, chatbot):
        """Test conversation initialization"""
        code = "def test(): pass"
        issue = "Missing docstring"

        chatbot.start_conversation(code, issue)

        assert len(chatbot.conversation_history) == 2
        assert chatbot.conversation_history[0]["role"] == "system"
        assert code in chatbot.conversation_history[1]["content"]

    @patch("src.interactive.chat_interface.OpenAI")
    def test_ask_question(self, mock_openai):
        """Test asking questions"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test answer"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        chatbot = InteractiveChatbot()
        chatbot.start_conversation("code", "issue")

        answer = chatbot.ask_question("Why is this wrong?")

        assert answer == "Test answer"
        assert len(chatbot.conversation_history) == 4  # system + context + question + answer

    @patch("src.interactive.chat_interface.OpenAI")
    def test_explain_issue(self, mock_openai):
        """Test detailed issue explanation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Detailed explanation"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        chatbot = InteractiveChatbot()
        explanation = chatbot.explain_issue("security issue", "code snippet")

        assert explanation == "Detailed explanation"
        mock_openai.return_value.chat.completions.create.assert_called_once()


class TestTestGenerator:
    """Tests for Test Generator"""

    @pytest.fixture
    def generator(self):
        with patch("src.testing.test_generator.OpenAI"):
            return TestGenerator()

    @patch("src.testing.test_generator.OpenAI")
    def test_generate_tests(self, mock_openai):
        """Test unit test generation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="def test_function(): assert True"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        generator = TestGenerator()
        tests = generator.generate_tests("def add(a, b): return a + b", "python")

        assert "test_function" in tests
        assert "assert" in tests

    def test_get_default_framework(self, generator):
        """Test framework selection"""
        assert generator._get_default_framework("python") == "pytest"
        assert generator._get_default_framework("javascript") == "jest"
        assert generator._get_default_framework("java") == "JUnit 5"

    @patch("src.testing.test_generator.OpenAI")
    def test_generate_integration_tests(self, mock_openai):
        """Test integration test generation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="integration tests"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        generator = TestGenerator()
        api_spec = {"endpoint": "/api/test", "method": "GET"}
        tests = generator.generate_integration_tests("endpoint code", api_spec)

        assert tests == "integration tests"


class TestDocumentationGenerator:
    """Tests for Documentation Generator"""

    @pytest.fixture
    def generator(self):
        with patch("src.documentation.doc_generator.OpenAI"):
            return DocumentationGenerator()

    @patch("src.documentation.doc_generator.OpenAI")
    def test_generate_docstring(self, mock_openai):
        """Test docstring generation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='"""Generated docstring"""'))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        generator = DocumentationGenerator()
        docstring = generator.generate_docstring("def func(): pass", "python")

        assert '"""Generated docstring"""' in docstring

    @patch("src.documentation.doc_generator.OpenAI")
    def test_generate_readme(self, mock_openai):
        """Test README generation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="# Project README"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        generator = DocumentationGenerator()
        readme = generator.generate_readme({"src": ["main.py"]}, ["main.py"])

        assert "# Project README" in readme

    def test_doc_style_selection(self, generator):
        """Test documentation style selection"""
        assert "Google-style" in generator._get_doc_style("python")
        assert "JSDoc" in generator._get_doc_style("javascript")


class TestPerformanceProfiler:
    """Tests for Performance Profiler"""

    @pytest.fixture
    def profiler(self):
        with patch("src.performance.profiler.OpenAI"):
            return PerformanceProfiler()

    @patch("src.performance.profiler.OpenAI")
    def test_analyze_performance(self, mock_openai):
        """Test performance analysis"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="O(n^2) complexity detected"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        profiler = PerformanceProfiler()
        analysis = profiler.analyze_performance(
            "for i in range(n): for j in range(n): pass", "python"
        )

        assert "analysis" in analysis
        assert "O(n^2)" in analysis["analysis"]

    def test_detect_antipatterns(self, profiler):
        """Test anti-pattern detection"""
        code = """
        result = ""
        for item in items:
            result = result + item  # String concatenation in loop
        """

        antipatterns = profiler.detect_antipatterns(code, "python")

        assert len(antipatterns) > 0
        assert any("concatenation" in p.lower() for p in antipatterns)


class TestCodeSmellDetector:
    """Tests for Code Smell Detector"""

    @pytest.fixture
    def detector(self):
        return CodeSmellDetector()

    def test_detect_long_method(self, detector):
        """Test long method detection"""
        long_code = "\n".join(["line" for _ in range(60)])
        smells = detector.detect_long_method(long_code)

        assert len(smells) > 0
        assert smells[0]["type"] == "long_method"

    def test_detect_magic_numbers(self, detector):
        """Test magic number detection"""
        code = "threshold = 42"
        smells = detector.detect_magic_numbers(code)

        assert len(smells) > 0
        assert any("42" in str(s["number"]) for s in smells)

    def test_detect_deep_nesting(self, detector):
        """Test deep nesting detection"""
        nested_code = """
                    if True:
                        if True:
                            if True:
                                if True:
                                    if True:
                                        pass
        """

        smells = detector.detect_deep_nesting(nested_code)

        assert len(smells) > 0
        assert smells[0]["type"] == "deep_nesting"

    def test_run_all_detections(self, detector):
        """Test running all detections"""
        code = "x = 123"  # Magic number
        results = detector.run_all_detections(code)

        assert "magic_numbers" in results
        assert "deep_nesting" in results


class TestSemanticCodeSearch:
    """Tests for Semantic Code Search"""

    @pytest.fixture
    def search(self):
        with patch("src.search.semantic_search.OpenAI"):
            return SemanticCodeSearch()

    @patch("src.search.semantic_search.OpenAI")
    def test_generate_embedding(self, mock_openai):
        """Test embedding generation"""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai.return_value.embeddings.create.return_value = mock_response

        search = SemanticCodeSearch()
        embedding = search.generate_embedding("test code")

        assert embedding == [0.1, 0.2, 0.3]

    @patch("src.search.semantic_search.OpenAI")
    def test_index_codebase(self, mock_openai):
        """Test codebase indexing"""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_openai.return_value.embeddings.create.return_value = mock_response

        search = SemanticCodeSearch()
        files = {"file1.py": "def func1(): pass", "file2.py": "def func2(): pass"}

        search.index_codebase(files)

        assert len(search.code_embeddings) == 2
        assert "file1.py" in search.code_embeddings

    @patch("src.search.semantic_search.OpenAI")
    def test_find_similar_code(self, mock_openai):
        """Test finding similar code"""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.5] * 1536)]
        mock_openai.return_value.embeddings.create.return_value = mock_response

        search = SemanticCodeSearch()
        search.code_embeddings = {
            "file1.py": {"code": "code1", "embedding": [0.5] * 1536},
            "file2.py": {"code": "code2", "embedding": [0.1] * 1536},
        }

        results = search.find_similar_code("query code", top_k=1)

        assert len(results) == 1
        assert "similarity" in results[0]

    @patch("src.search.semantic_search.OpenAI")
    def test_detect_duplicate_logic(self, mock_openai):
        """Test duplicate detection"""
        search = SemanticCodeSearch()
        search.code_embeddings = {
            "file1.py": {"code": "code1", "embedding": [0.9] * 1536},
            "file2.py": {"code": "code2", "embedding": [0.9] * 1536},
        }

        duplicates = search.detect_duplicate_logic(threshold=0.85)

        assert len(duplicates) > 0
        assert duplicates[0]["file1"] == "file1.py"


# Integration test for Phase 4
@pytest.mark.integration
class TestPhase4Integration:
    """Integration tests for Phase 4 workflow"""

    @patch("src.testing.test_generator.OpenAI")
    @patch("src.documentation.doc_generator.OpenAI")
    @patch("src.performance.profiler.OpenAI")
    def test_full_phase4_workflow(self, mock_profiler, mock_docs, mock_tests):
        """Test complete Phase 4 workflow"""
        # Mock responses
        mock_test_response = Mock()
        mock_test_response.choices = [Mock(message=Mock(content="def test_func(): pass"))]
        mock_tests.return_value.chat.completions.create.return_value = mock_test_response

        mock_doc_response = Mock()
        mock_doc_response.choices = [Mock(message=Mock(content='"""Docstring"""'))]
        mock_docs.return_value.chat.completions.create.return_value = mock_doc_response

        mock_perf_response = Mock()
        mock_perf_response.choices = [Mock(message=Mock(content="O(n) complexity"))]
        mock_profiler.return_value.chat.completions.create.return_value = mock_perf_response

        # Test workflow
        test_gen = TestGenerator()
        doc_gen = DocumentationGenerator()
        profiler = PerformanceProfiler()
        smell_detector = CodeSmellDetector()

        code = "def add(a, b): return a + b"

        # Generate tests
        tests = test_gen.generate_tests(code, "python")
        assert "test_func" in tests

        # Generate docs
        docs = doc_gen.generate_docstring(code, "python")
        assert "Docstring" in docs

        # Analyze performance
        analysis = profiler.analyze_performance(code, "python")
        assert "analysis" in analysis

        # Detect smells
        smells = smell_detector.run_all_detections(code)
        assert "magic_numbers" in smells
