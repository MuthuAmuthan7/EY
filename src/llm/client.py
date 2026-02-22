"""LLM client abstraction for unified LLM interactions using Google Gemini."""

import json
import logging
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from google import genai 

from ..config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified client for LLM interactions using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize LLM client.
        
        Args:
            api_key: Google API key (defaults to settings)
            model: Model name (defaults to settings)
        """
        self.api_key = api_key or settings.google_api_key
        self.model_name = model or settings.llm_model

        # Configure Gemini client
        self.client = genai.Client()
        
        logger.info(f"Initialized LLM client with model: {self.model_name}")
    
    def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Get chat completion from LLM.
        
        Args:
            system_prompt: System instruction
            user_prompt: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            tools: Optional function calling tools (not used with Gemini currently)
            
        Returns:
            LLM response text
        """
        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate response using new API format
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens or 8192,
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"LLM completion error: {e}")
            raise
    
    def structured_output(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[BaseModel],
        temperature: float = 0.7,
    ) -> BaseModel:
        """Get structured output from LLM matching a Pydantic schema.
        
        Args:
            system_prompt: System instruction
            user_prompt: User message
            schema: Pydantic model class for response structure
            temperature: Sampling temperature
            
        Returns:
            Instance of the schema class
        """
        # Add JSON schema instruction to system prompt
        json_schema = schema.model_json_schema()
        enhanced_system_prompt = f"""{system_prompt}

You must respond with valid JSON matching this exact schema:
{json.dumps(json_schema, indent=2)}

Return ONLY the JSON object, no additional text or markdown formatting."""
        
        try:
            response_text = self.chat_completion(
                system_prompt=enhanced_system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )
            
            # Parse JSON response
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            data = json.loads(response_text)
            return schema(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            raise
        except Exception as e:
            logger.error(f"Structured output error: {e}")
            raise
    
    def summarize(
        self,
        text: str,
        max_length: int = 200,
        focus: Optional[str] = None,
    ) -> str:
        """Generate a summary of the given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in words
            focus: Optional focus area for summary
            
        Returns:
            Summary text
        """
        focus_instruction = f" Focus on: {focus}." if focus else ""
        
        system_prompt = f"""You are a concise summarization assistant.
Create clear, informative summaries in approximately {max_length} words.{focus_instruction}"""
        
        user_prompt = f"Summarize the following text:\n\n{text}"
        
        return self.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5,
        )
