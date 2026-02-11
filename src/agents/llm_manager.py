"""
LLM wrapper and utilities
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Optional, Dict, Any
import time

from src.utils.config import settings
from src.utils.logger import app_logger


class LLMManager:
    """Manages LLM initialization and interactions"""

    def __init__(self):
        """Initialize LLM"""
        self.llm = self._initialize_llm()
        self.parser = StrOutputParser()

    def _initialize_llm(self) -> ChatGroq:
        """Initialize the Groq LLM"""
        try:
            llm = ChatGroq(
                temperature=settings.llm_temperature,
                groq_api_key=settings.groq_api_key,
                model_name=settings.llm_model,
                max_tokens=settings.llm_max_tokens,
            )
            app_logger.info(f"LLM initialized: {settings.llm_model}")
            return llm
        except Exception as e:
            app_logger.error(f"Error initializing LLM: {e}")
            raise

    def invoke_with_retry(
        self,
        prompt: ChatPromptTemplate,
        input_data: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> str:
        """
        Invoke LLM with retry logic

        Args:
            prompt: Chat prompt template
            input_data: Input variables for the prompt
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            LLM response as string
        """
        chain = prompt | self.llm | self.parser

        for attempt in range(max_retries):
            try:
                response = chain.invoke(input_data)
                return response.strip()

            except Exception as e:
                app_logger.warning(f"LLM invocation attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    app_logger.error(f"All LLM invocation attempts failed: {e}")
                    raise

    def get_llm(self) -> ChatGroq:
        """Get the LLM instance"""
        return self.llm


# Global LLM manager instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get or create LLM manager singleton"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager
