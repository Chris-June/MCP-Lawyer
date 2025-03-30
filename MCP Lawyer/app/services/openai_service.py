import os
import json
import aiohttp
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException, Request

class OpenAIService:
    """Service for interacting with the OpenAI API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def generate_completion(self, 
                                messages_or_prompt: Union[List[Dict[str, str]], str], 
                                temperature: float = 0.7,
                                max_tokens: Optional[int] = None,
                                stream: bool = False) -> str:
        """Generate a completion from the OpenAI API
        
        Args:
            messages_or_prompt: Either a list of message objects or a string prompt
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate (None = model default)
            stream: Whether to stream the response
            
        Returns:
            The generated text response as a string
        """
        url = f"{self.api_base}/chat/completions"
        
        # Convert string prompt to messages format if needed
        if isinstance(messages_or_prompt, str):
            messages = [
                {"role": "user", "content": messages_or_prompt}
            ]
            print(f"DEBUG: Converting string prompt to messages format: {messages}")
        else:
            messages = messages_or_prompt
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status != 200:
                        error_message = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"OpenAI API error: {error_message}"
                        )
                    
                    # Handle streaming response if stream=True
                    if stream:
                        return response
                    else:
                        response_json = await response.json()
                        # Extract the text content from the response
                        return await self.extract_text_from_completion(response_json)
            except aiohttp.ClientError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to OpenAI API: {str(e)}"
                )
    
    async def extract_text_from_completion(self, completion: Dict[str, Any]) -> str:
        """Extract the generated text from a completion response
        
        Args:
            completion: The completion response from the API
            
        Returns:
            The generated text
        """
        try:
            return completion.get("choices", [{}])[0].get("message", {}).get("content", "")
        except (KeyError, IndexError):
            return ""
    
    def create_system_message(self, content: str) -> Dict[str, str]:
        """Create a system message"""
        return {"role": "system", "content": content}
    
    def create_user_message(self, content: str) -> Dict[str, str]:
        """Create a user message"""
        return {"role": "user", "content": content}
    
    def create_assistant_message(self, content: str) -> Dict[str, str]:
        """Create an assistant message"""
        return {"role": "assistant", "content": content}


async def get_openai_service() -> OpenAIService:
    """Dependency for getting the OpenAI service"""
    return OpenAIService()
