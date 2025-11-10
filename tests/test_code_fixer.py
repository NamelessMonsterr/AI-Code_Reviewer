import pytest
from unittest.mock import Mock, patch
from src.autofix.code_fixer import CodeFixer


class TestCodeFixer:

    @pytest.fixture
    def fixer(self):
        """Create CodeFixer instance with mocked OpenAI"""
        with patch("src.autofix.code_fixer.OpenAI"):
            return CodeFixer()

    def test_initialization(self):
        """Test CodeFixer initialization"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            fixer = CodeFixer()
            assert fixer.api_key == "test_key"

    def test_missing_api_key(self):
        """Test error when API key is missing"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                CodeFixer()

    @patch("src.autofix.code_fixer.OpenAI")
    def test_generate_fix_success(self, mock_openai):
        """Test successful code fix generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="def fixed_code(): pass"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        fixer = CodeFixer()
        result = fixer.generate_fix(
            code="def buggy_code(): error", issue="Syntax error", lang="python"
        )

        assert result is not None
        assert "fixed_code" in result

    @patch("src.autofix.code_fixer.OpenAI")
    def test_generate_fix_with_markdown(self, mock_openai):
        """Test code extraction from markdown response"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="```python\ndef fixed(): pass\n```"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        fixer = CodeFixer()
        result = fixer.generate_fix("code", "issue", "python")

        assert "def fixed(): pass" in result
        assert "```" not in result

    @patch("src.autofix.code_fixer.OpenAI")
    def test_generate_alternative_fixes(self, mock_openai):
        """Test generation of alternative fixes"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="alternative_fix"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        fixer = CodeFixer()
        alternatives = fixer.suggest_alternative_fixes(
            code="buggy", issue="error", lang="python", num_alternatives=3
        )

        assert len(alternatives) == 3
