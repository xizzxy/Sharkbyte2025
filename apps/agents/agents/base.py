"""
Base agent class using Google Generative AI (Gemini)
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class BaseAgent(ABC):
    """Base class for all CareerPilot agents"""

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.2,
        system_prompt_file: Optional[str] = None
    ):
        """
        Initialize agent with Google Generative AI

        Args:
            model_name: Gemini model name
            temperature: Generation temperature (lower = more consistent)
            system_prompt_file: Path to system prompt file
        """
        # Initialize Google Generative AI with API key
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment")

        genai.configure(api_key=api_key)

        self.model_name = model_name
        self.temperature = temperature
        self.model = genai.GenerativeModel(model_name)

        # Load system prompt
        self.system_prompt = self._load_system_prompt(system_prompt_file)

    def _load_system_prompt(self, file_path: Optional[str]) -> str:
        """Load system prompt from file"""
        if not file_path:
            return ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: System prompt file not found: {file_path}")
            return ""

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response from Gemini

        Args:
            prompt: User prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        # Combine system prompt with user prompt
        full_prompt = f"{self.system_prompt}\n\n{prompt}" if self.system_prompt else prompt

        generation_config = {
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", 0.95),
            "top_k": kwargs.get("top_k", 40),
            "max_output_tokens": kwargs.get("max_output_tokens", 8192),
        }

        response = self.model.generate_content(
            full_prompt,
            generation_config=generation_config
        )

        return response.text

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent logic - must be implemented by subclasses

        Args:
            input_data: Input data for the agent

        Returns:
            Agent output
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"
