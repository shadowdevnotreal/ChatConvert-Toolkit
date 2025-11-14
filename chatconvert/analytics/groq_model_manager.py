"""
Groq Model Manager - Intelligent model selection for different analysis tasks.

Automatically selects the best Groq model based on task requirements:
- Context length needed
- Speed vs quality trade-offs
- Task-specific capabilities
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import logging


class AnalysisTask(Enum):
    """Types of analysis tasks."""
    SENTIMENT = "sentiment"
    TOPIC_EXTRACTION = "topic_extraction"
    HATE_SPEECH = "hate_speech"
    STATEMENT_ANALYSIS = "statement_analysis"
    GENERAL_ANALYSIS = "general_analysis"
    QUICK_SUMMARY = "quick_summary"
    LONG_CONTEXT = "long_context"


class GroqModelManager:
    """
    Manage Groq model selection based on task requirements.

    Available Groq production models:
    - llama-3.3-70b-versatile: Best reasoning, general purpose (128k context)
    - llama-3.1-70b-versatile: Alternative 70B model (128k context)
    - llama-3.1-8b-instant: Fast, lightweight (128k context)
    - mixtral-8x7b-32768: Good for long context (32k context)
    - gemma2-9b-it: Efficient, good for analysis (8k context)
    """

    # Model specifications
    MODELS = {
        'llama-3.3-70b-versatile': {
            'context_window': 128000,
            'speed': 'medium',
            'quality': 'excellent',
            'specialties': ['reasoning', 'hate_speech', 'complex_analysis']
        },
        'llama-3.1-70b-versatile': {
            'context_window': 128000,
            'speed': 'medium',
            'quality': 'excellent',
            'specialties': ['reasoning', 'general_analysis']
        },
        'llama-3.1-8b-instant': {
            'context_window': 128000,
            'speed': 'very_fast',
            'quality': 'good',
            'specialties': ['quick_tasks', 'sentiment']
        },
        'mixtral-8x7b-32768': {
            'context_window': 32768,
            'speed': 'fast',
            'quality': 'very_good',
            'specialties': ['long_context', 'general_analysis']
        },
        'gemma2-9b-it': {
            'context_window': 8192,
            'speed': 'fast',
            'quality': 'good',
            'specialties': ['efficient_analysis', 'topic_extraction']
        }
    }

    # Task to model mapping
    TASK_MODEL_MAP = {
        AnalysisTask.SENTIMENT: 'llama-3.1-8b-instant',  # Fast sentiment
        AnalysisTask.TOPIC_EXTRACTION: 'gemma2-9b-it',  # Good at extraction
        AnalysisTask.HATE_SPEECH: 'llama-3.3-70b-versatile',  # Best reasoning
        AnalysisTask.STATEMENT_ANALYSIS: 'llama-3.3-70b-versatile',  # Complex understanding
        AnalysisTask.GENERAL_ANALYSIS: 'llama-3.3-70b-versatile',  # Best all-around
        AnalysisTask.QUICK_SUMMARY: 'llama-3.1-8b-instant',  # Speed priority
        AnalysisTask.LONG_CONTEXT: 'mixtral-8x7b-32768'  # Large context
    }

    def __init__(self, default_model: Optional[str] = None):
        """
        Initialize model manager.

        Args:
            default_model: Default model to use if task-based selection fails
        """
        self.logger = logging.getLogger(__name__)
        self.default_model = default_model or 'llama-3.3-70b-versatile'

    def select_model(
        self,
        task: AnalysisTask,
        estimated_tokens: Optional[int] = None,
        priority_speed: bool = False
    ) -> str:
        """
        Select best model for a given task.

        Args:
            task: Type of analysis task
            estimated_tokens: Estimated input tokens (for context window check)
            priority_speed: Prioritize speed over quality

        Returns:
            Model name to use
        """
        # Start with task-based selection
        model = self.TASK_MODEL_MAP.get(task, self.default_model)

        # Check context window if tokens provided
        if estimated_tokens:
            model_info = self.MODELS[model]
            if estimated_tokens > model_info['context_window'] * 0.8:  # 80% threshold
                self.logger.warning(
                    f"Estimated tokens ({estimated_tokens}) near limit for {model}. "
                    f"Switching to larger context model."
                )
                # Switch to model with larger context
                model = self._find_larger_context_model(estimated_tokens)

        # Override for speed priority
        if priority_speed:
            model_info = self.MODELS[model]
            if model_info['speed'] not in ['fast', 'very_fast']:
                self.logger.info(f"Speed prioritized. Switching from {model} to faster model.")
                model = 'llama-3.1-8b-instant'  # Fastest model

        self.logger.info(f"Selected model: {model} for task: {task.value}")
        return model

    def _find_larger_context_model(self, required_tokens: int) -> str:
        """Find model with sufficient context window."""
        suitable_models = [
            (name, info['context_window'])
            for name, info in self.MODELS.items()
            if info['context_window'] >= required_tokens
        ]

        if not suitable_models:
            self.logger.error(f"No model found with sufficient context for {required_tokens} tokens")
            return self.default_model

        # Return model with smallest sufficient context (most efficient)
        suitable_models.sort(key=lambda x: x[1])
        return suitable_models[0][0]

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        return self.MODELS.get(model_name, {})

    def list_models(self) -> List[str]:
        """List all available models."""
        return list(self.MODELS.keys())

    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of tokens in text.

        Uses simple heuristic: ~4 characters per token (average for English).

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def recommend_model(
        self,
        text: str,
        task: AnalysisTask,
        priority_speed: bool = False
    ) -> Dict[str, Any]:
        """
        Get model recommendation with explanation.

        Args:
            text: Input text to analyze
            task: Type of analysis task
            priority_speed: Prioritize speed

        Returns:
            Dict with model recommendation and reasoning
        """
        estimated_tokens = self.estimate_tokens(text)
        selected_model = self.select_model(task, estimated_tokens, priority_speed)
        model_info = self.get_model_info(selected_model)

        reasoning = []
        reasoning.append(f"Task type: {task.value}")
        reasoning.append(f"Estimated tokens: {estimated_tokens}")

        if priority_speed:
            reasoning.append("Speed prioritized")

        if estimated_tokens > 10000:
            reasoning.append(f"Large input requires {model_info['context_window']:,} token context")

        reasoning.append(f"Model specialties: {', '.join(model_info['specialties'])}")

        return {
            'model': selected_model,
            'reasoning': reasoning,
            'model_info': model_info,
            'estimated_tokens': estimated_tokens
        }
