"""
Comprehensive tests for Phase 5 features:
- Model Fine-tuning
- Bug Pattern Learning
- Pattern Recognition
- Severity Scoring
- Knowledge Base
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
from src.training.model_finetuner import ModelFineTuner
from src.intelligence.bug_pattern_learner import BugPatternLearner
from src.intelligence.pattern_recognizer import CodingPatternRecognizer
from src.intelligence.severity_scorer import SeverityScorer
from src.intelligence.knowledge_base import KnowledgeBase


class TestModelFineTuner:
    """Tests for Model Fine-tuning"""
    
    @pytest.fixture
    def finetuner(self):
        with patch('src.training.model_finetuner.OpenAI'):
            return ModelFineTuner()
    
    def test_initialization(self, finetuner):
        """Test fine-tuner initialization"""
        assert finetuner.training_data == []
    
    def test_collect_training_data(self, finetuner):
        """Test training data collection"""
        review = {
            'code': 'def test(): pass',
            'review_comments': 'Add docstring'
        }
        
        finetuner.collect_training_data(review)
        
        assert len(finetuner.training_data) == 1
        assert finetuner.training_data[0]['messages'][1]['content'].startswith('Review this code')
    
    def test_prepare_training_file(self, finetuner, tmp_path):
        """Test training file preparation"""
        finetuner.training_data = [
            {'messages': [{'role': 'user', 'content': 'test'}]}
        ]
        
        output_file = tmp_path / "training.jsonl"
        result = finetuner.prepare_training_file(str(output_file))
        
        assert output_file.exists()
        with open(output_file, 'r') as f:
            line = f.readline()
            data = json.loads(line)
            assert 'messages' in data
    
    @patch('src.training.model_finetuner.OpenAI')
    def test_upload_training_file(self, mock_openai, tmp_path):
        """Test training file upload"""
        mock_response = Mock(id='file-123')
        mock_openai.return_value.files.create.return_value = mock_response
        
        # Create test file
        test_file = tmp_path / "test.jsonl"
        test_file.write_text('{"test": "data"}')
        
        finetuner = ModelFineTuner()
        file_id = finetuner.upload_training_file(str(test_file))
        
        assert file_id == 'file-123'
    
    @patch('src.training.model_finetuner.OpenAI')
    def test_start_fine_tuning(self, mock_openai):
        """Test starting fine-tuning job"""
        mock_response = Mock(id='job-123')
        mock_openai.return_value.fine_tuning.jobs.create.return_value = mock_response
        
        finetuner = ModelFineTuner()
        job_id = finetuner.start_fine_tuning('file-123')
        
        assert job_id == 'job-123'
    
    @patch('src.training.model_finetuner.OpenAI')
    def test_check_fine_tuning_status(self, mock_openai):
        """Test checking fine-tuning status"""
        mock_response = Mock(
            status='succeeded',
            trained_tokens=1000,
            fine_tuned_model='ft-model-123'
        )
        mock_openai.return_value.fine_tuning.jobs.retrieve.return_value = mock_response
        
        finetuner = ModelFineTuner()
        status = finetuner.check_fine_tuning_status('job-123')
        
        assert status['status'] == 'succeeded'
        assert status['trained_tokens'] == 1000
    
    @patch('src.training.model_finetuner.OpenAI')
    def test_evaluate_model_performance(self, mock_openai):
        """Test model evaluation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Fix the issue"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        finetuner = ModelFineTuner()
        test_cases = [
            {'code': 'buggy code', 'expected_review': 'Fix the issue'}
        ]
        
        results = finetuner.evaluate_model_performance('ft-model-123', test_cases)
        
        assert results['total'] == 1
        assert results['accuracy'] >= 0


class TestBugPatternLearner:
    """Tests for Bug Pattern Learning"""
    
    @pytest.fixture
    def learner(self):
        return BugPatternLearner()
    
    def test_record_bug(self, learner):
        """Test bug recording"""
        bug = {
            'type': 'null_pointer',
            'severity': 0.8,
            'fix_pattern': 'Add null check',
            'time_to_fix': 30,
            'file_extension': 'py',
            'function_type': 'method'
        }
        
        learner.record_bug(bug)
        
        pattern_key = 'null_pointer:py:method'
        assert pattern_key in learner.bug_patterns
        assert learner.bug_patterns[pattern_key]['count'] == 1
    
    def test_predict_bug_probability(self, learner):
        """Test bug prediction"""
        # Record multiple bugs
        for _ in range(5):
            learner.record_bug({
                'type': 'memory_leak',
                'severity': 0.9,
                'fix_pattern': 'Close resources',
                'time_to_fix': 60,
                'file_extension': 'py',
                'function_type': 'function'
            })
        
        code = "def process(): file = open('test.txt')"
        predictions = learner.predict_bug_probability(code, 'test.py')
        
        assert 'predictions' in predictions
        assert 'risk_score' in predictions
    
    def test_load_save_patterns(self, learner, tmp_path):
        """Test pattern persistence"""
        learner.bug_history_file = tmp_path / 'bugs.json'
        
        bug = {
            'type': 'test_bug',
            'severity': 0.5,
            'fix_pattern': 'fix',
            'time_to_fix': 10,
            'file_extension': 'py',
            'function_type': 'func'
        }
        learner.record_bug(bug)
        
        # Create new learner and load patterns
        new_learner = BugPatternLearner()
        new_learner.bug_history_file = learner.bug_history_file
        new_learner.load_patterns()
        
        assert 'test_bug:py:func' in new_learner.bug_patterns


class TestCodingPatternRecognizer:
    """Tests for Pattern Recognition"""
    
    @pytest.fixture
    def recognizer(self):
        return CodingPatternRecognizer()
    
    def test_extract_naming_patterns(self, recognizer):
        """Test naming pattern extraction"""
        code = """
class MyClass:
    def my_function(self):
        pass
"""
        
        recognizer._extract_naming_patterns(code)
        
        assert recognizer.patterns['naming_conventions']['PascalCase_classes'] > 0
        assert recognizer.patterns['naming_conventions']['snake_case_functions'] > 0
    
    def test_extract_structure_patterns(self, recognizer):
        """Test code structure pattern extraction"""
        code = '''
def func(x: int) -> str:
    """Docstring"""
    return str(x)
'''
        
        recognizer._extract_structure_patterns(code)
        
        assert recognizer.patterns['code_structure']['uses_type_hints'] > 0
        assert recognizer.patterns['code_structure']['has_docstrings'] > 0
    
    def test_extract_import_patterns(self, recognizer):
        """Test import pattern extraction"""
        code = """
import os
import sys
from typing import List
"""
        
        recognizer._extract_import_patterns(code)
        
        assert recognizer.patterns['common_imports']['os'] > 0
        assert recognizer.patterns['common_imports']['typing'] > 0
    
    def test_get_team_preferences(self, recognizer):
        """Test team preference extraction"""
        code = """
class Test:
    def method(self):
        pass
"""
        recognizer.learn_from_codebase({'test.py': code})
        
        preferences = recognizer.get_team_preferences()
        
        assert 'naming_conventions' in preferences
        assert 'code_structure' in preferences
    
    def test_check_consistency(self, recognizer):
        """Test consistency checking"""
        # Learn from examples
        examples = {
            'file1.py': 'class PascalCase: pass',
            'file2.py': 'class AnotherClass: pass'
        }
        recognizer.learn_from_codebase(examples)
        
        # Check inconsistent code
        violations = recognizer.check_consistency('class lowercase: pass')
        
        assert len(violations) > 0


class TestSeverityScorer:
    """Tests for Severity Scoring"""
    
    @pytest.fixture
    def scorer(self):
        return SeverityScorer()
    
    def test_calculate_severity_security(self, scorer):
        """Test severity calculation for security issues"""
        issue = {
            'category': 'security',
            'description': 'SQL injection vulnerability',
            'file_path': '/app/auth/login.py',
            'type': 'security_vuln'
        }
        
        result = scorer.calculate_severity(issue)
        
        assert result['severity_level'] in ['CRITICAL', 'HIGH']
        assert result['severity_score'] > 7.0
    
    def test_calculate_severity_style(self, scorer):
        """Test severity calculation for style issues"""
        issue = {
            'category': 'style',
            'description': 'Line too long',
            'file_path': '/app/utils/helpers.py',
            'type': 'style_issue'
        }
        
        result = scorer.calculate_severity(issue)
        
        assert result['severity_level'] in ['LOW', 'INFO']
        assert result['severity_score'] < 5.0
    
    def test_context_multiplier(self, scorer):
        """Test context-based multiplier"""
        critical_issue = {
            'category': 'security',
            'description': 'test',
            'file_path': '/app/auth/security.py'
        }
        
        test_issue = {
            'category': 'security',
            'description': 'test',
            'file_path': '/tests/test_auth.py'
        }
        
        critical_result = scorer.calculate_severity(critical_issue)
        test_result = scorer.calculate_severity(test_issue)
        
        assert critical_result['severity_score'] > test_result['severity_score']
    
    def test_learn_from_feedback(self, scorer):
        """Test learning from user feedback"""
        issue = {
            'category': 'performance',
            'description': 'Slow query',
            'file_path': '/app/db/queries.py',
            'type': 'perf_issue'
        }
        
        scorer.learn_from_feedback(issue, 'CRITICAL')
        
        assert len(scorer.historical_scores) == 1


class TestKnowledgeBase:
    """Tests for Knowledge Base"""
    
    @pytest.fixture
    def kb(self, tmp_path):
        kb = KnowledgeBase()
        kb.kb_file = tmp_path / 'knowledge.json'
        return kb
    
    def test_add_best_practice(self, kb):
        """Test adding best practice"""
        practice = {
            'title': 'Use type hints',
            'description': 'Always use type hints in Python',
            'example': 'def func(x: int) -> str:',
            'category': 'typing'
        }
        
        kb.add_best_practice(practice)
        
        assert len(kb.knowledge['best_practices']) == 1
        assert kb.knowledge['best_practices'][0]['title'] == 'Use type hints'
    
    def test_add_common_mistake(self, kb):
        """Test adding common mistake"""
        mistake = {
            'description': 'Forgetting to close files',
            'occurrences': 5,
            'fix': 'Use context manager',
            'severity': 'medium'
        }
        
        kb.add_common_mistake(mistake)
        
        assert len(kb.knowledge['common_mistakes']) == 1
    
    def test_approve_pattern(self, kb):
        """Test approving coding pattern"""
        pattern = {
            'name': 'Factory Pattern',
            'description': 'Use factory for object creation',
            'template': 'class Factory...',
            'use_cases': ['Object creation', 'Dependency injection']
        }
        
        kb.approve_pattern(pattern)
        
        assert len(kb.knowledge['approved_patterns']) == 1
    
    def test_query_knowledge(self, kb):
        """Test knowledge base query"""
        kb.add_best_practice({
            'title': 'Error handling',
            'description': 'Always handle exceptions',
            'category': 'errors'
        })
        
        results = kb.query_knowledge('error')
        
        assert len(results) > 0
        assert results[0]['category'] == 'best_practices'
    
    def test_get_recommendations(self, kb):
        """Test getting code recommendations"""
        kb.add_common_mistake({
            'description': 'Using eval() function',
            'fix': 'Use ast.literal_eval() instead',
            'severity': 'high'
        })
        
        code = "result = eval(user_input)"
        recommendations = kb.get_recommendations_for_code(code, 'python')
        
        assert len(recommendations) > 0
    
    def test_save_load_knowledge(self, kb):
        """Test knowledge persistence"""
        kb.add_best_practice({
            'title': 'Test practice',
            'description': 'Test description'
        })
        kb.save_knowledge()
        
        # Load in new instance
        new_kb = KnowledgeBase()
        new_kb.kb_file = kb.kb_file
        new_kb.load_knowledge()
        
        assert len(new_kb.knowledge['best_practices']) == 1


# Integration test for Phase 5
@pytest.mark.integration
class TestPhase5Integration:
    """Integration tests for Phase 5 workflow"""
    
    def test_full_learning_workflow(self):
        """Test complete learning and prediction workflow"""
        # Initialize components
        learner = BugPatternLearner()
        recognizer = CodingPatternRecognizer()
        scorer = SeverityScorer()
        kb = KnowledgeBase()
        
        # Simulate learning from historical data
        for _ in range(10):
            learner.record_bug({
                'type': 'null_check',
                'severity': 0.7,
                'fix_pattern': 'Add validation',
                'time_to_fix': 20,
                'file_extension': 'py',
                'function_type': 'method'
            })
        
        # Learn coding patterns
        codebase = {
            'file1.py': 'class MyClass:\n    def method(self): pass',
            'file2.py': 'class Another:\n    def func(self): pass'
        }
        recognizer.learn_from_codebase(codebase)
        
        # Add knowledge
        kb.add_best_practice({
            'title': 'Null checks',
            'description': 'Always validate inputs'
        })
        
        # Test prediction
        new_code = "def process(data): return data.value"
        predictions = learner.predict_bug_probability(new_code, 'new.py')
        
        assert 'predictions' in predictions
        assert 'risk_score' in predictions
        
        # Test pattern recognition
        preferences = recognizer.get_team_preferences()
        assert 'naming_conventions' in preferences
        
        # Test severity scoring
        issue = {
            'category': 'null_check',
            'description': 'Missing validation',
            'file_path': 'new.py',
            'type': 'null_check'
        }
        severity = scorer.calculate_severity(issue)
        assert 'severity_score' in severity
    
    @patch('src.training.model_finetuner.OpenAI')
    def test_model_training_workflow(self, mock_openai):
        """Test model training and evaluation workflow"""
        mock_file_response = Mock(id='file-123')
        mock_job_response = Mock(id='job-123')
        mock_status_response = Mock(
            status='succeeded',
            fine_tuned_model='ft-model-123'
        )
        
        mock_openai.return_value.files.create.return_value = mock_file_response
        mock_openai.return_value.fine_tuning.jobs.create.return_value = mock_job_response
        mock_openai.return_value.fine_tuning.jobs.retrieve.return_value = mock_status_response
        
        # Collect training data
        finetuner = ModelFineTuner()
        for _ in range(5):
            finetuner.collect_training_data({
                'code': 'def test(): pass',
                'review_comments': 'Good code'
            })
        
        assert len(finetuner.training_data) == 5
        
        # Prepare and upload
        training_file = finetuner.prepare_training_file('/tmp/training.jsonl')
        assert training_file
