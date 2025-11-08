"""
Base class for all AI model integrations
Eliminates code duplication across OpenAI-using classes
"""
from openai import OpenAI
from anthropic import Anthropic
import os
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class AIModelBase(ABC):
    """
    Base class for AI model integrations
    
    Provides:
    - OpenAI client initialization
    - Anthropic client initialization
    - Error handling
    - Retry logic
    - Logging
    """
    
    def __init__(self, provider: str = 'openai'):
        """
        Initialize AI model client
        
        Args:
            provider: 'openai' or 'anthropic'
        """
        self.provider = provider
        self.openai_client = None
        self.anthropic_client = None
        
        if provider == 'openai':
            self.openai_client = self._init_openai_client()
        elif provider == 'anthropic':
            self.anthropic_client = self._init_anthropic_client()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _init_openai_client(self) -> OpenAI:
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Get your key from: https://platform.openai.com/api-keys"
            )
        
        logger.info("Initialized OpenAI client")
        return OpenAI(api_key=api_key)
    
    def _init_anthropic_client(self) -> Anthropic:
        """Initialize Anthropic Claude client"""
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            raise ValueError(
                "CLAUDE_API_KEY environment variable is required. "
                "Get your key from: https://console.anthropic.com/"
            )
        
        logger.info("Initialized Anthropic client")
        return Anthropic(api_key=api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Universal chat completion with retry logic
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: gpt-4 or claude-3-opus)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == 'openai':
                return self._openai_chat(messages, model, temperature, max_tokens, **kwargs)
            elif self.provider == 'anthropic':
                return self._anthropic_chat(messages, model, temperature, max_tokens, **kwargs)
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}", exc_info=True)
            raise
    
    def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """OpenAI-specific chat completion"""
        if model is None:
            model = 'gpt-4'
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    def _anthropic_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Anthropic-specific chat completion"""
        if model is None:
            model = 'claude-3-opus-20240229'
        
        # Convert OpenAI-style messages to Anthropic format
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                conversation_messages.append(msg)
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=conversation_messages,
            **kwargs
        )
        
        return response.content[0].text
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_embedding(self, text: str, model: str = 'text-embedding-ada-002') -> List[float]:
        """
        Generate embedding vector for text (OpenAI only)
        
        Args:
            text: Input text
            model: Embedding model name
            
        Returns:
            Embedding vector
        """
        if self.provider != 'openai':
            raise NotImplementedError("Embeddings only supported for OpenAI")
        
        try:
            response = self.openai_client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}", exc_info=True)
            raise
    
    def validate_response(self, response: str, min_length: int = 10) -> bool:
        """
        Validate AI response
        
        Args:
            response: Generated response
            min_length: Minimum acceptable length
            
        Returns:
            True if valid
        """
        if not response:
            logger.warning("Empty response received")
            return False
        
        if len(response) < min_length:
            logger.warning(f"Response too short: {len(response)} chars")
            return False
        
        return True
    
    def extract_code_from_markdown(self, response: str, language: str = '') -> str:
        """
        Extract code from markdown code blocks
        
        Args:
            response: Response potentially containing markdown
            language: Expected language (e.g., 'python', 'javascript')
            
        Returns:
            Extracted code
        """
        import re
        
        # Try to find code block with language specifier
        if language:
            pattern = f"```{language}\\n(.*?)```"
        else:
            pattern = r"```(?:\w+)?\n(.*?)```"
        
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Try without language specifier
        matches = re.findall(r"```\n(.*?)```", response, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        # Return original if no code blocks found
        return response.strip()
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """
        Abstract method to be implemented by subclasses
        Each subclass should implement its specific logic here
        """
        pass


class AIModelConfig:
    """Configuration for AI model parameters"""
    
    # Model mappings
    MODELS = {
        'openai': {
            'fast': 'gpt-3.5-turbo',
            'balanced': 'gpt-4',
            'best': 'gpt-4-turbo-preview'
        },
        'anthropic': {
            'fast': 'claude-3-haiku-20240307',
            'balanced': 'claude-3-sonnet-20240229',
            'best': 'claude-3-opus-20240229'
        }
    }
    
    # Default temperatures by task type
    TEMPERATURES = {
        'code_review': 0.2,
        'creative': 0.7,
        'documentation': 0.3,
        'chat': 0.4
    }
    
    # Token limits by model
    TOKEN_LIMITS = {
        'gpt-3.5-turbo': 4096,
        'gpt-4': 8192,
        'gpt-4-turbo-preview': 128000,
        'claude-3-haiku-20240307': 200000,
        'claude-3-sonnet-20240229': 200000,
        'claude-3-opus-20240229': 200000
    }
    
    @classmethod
    def get_model(cls, provider: str, quality: str = 'balanced') -> str:
        """Get model name by provider and quality"""
        return cls.MODELS.get(provider, {}).get(quality, 'gpt-4')
    
    @classmethod
    def get_temperature(cls, task_type: str) -> float:
        """Get temperature by task type"""
        return cls.TEMPERATURES.get(task_type, 0.2)
    
    @classmethod
    def get_token_limit(cls, model: str) -> int:
        """Get token limit for model"""
        return cls.TOKEN_LIMITS.get(model, 4096)