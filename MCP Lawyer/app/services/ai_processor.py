from openai import AsyncOpenAI
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.config import settings

class AIProcessor:
    """Service for processing AI requests using OpenAI API"""
    
    def __init__(self):
        """Initialize the AI processor"""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response using the OpenAI API
        
        Args:
            system_prompt: The system prompt to use
            user_prompt: The user prompt to use
            
        Returns:
            The generated response
        """
        try:
            # Log the prompts for debugging
            print("\n--- AI Request Debugging ---")
            print("System Prompt:")
            print(system_prompt)
            print("\nUser Prompt:")
            print(user_prompt)
            print("--- End of Prompts ---\n")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500,  # Increased to allow more detailed response
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract and log the response
            full_response = response.choices[0].message
            generated_text = full_response.content.strip() if full_response.content else ""
            
            print("\n--- AI Response Debugging ---")
            print("Full Response Object:")
            print(repr(full_response))
            print("\nGenerated Text:")
            print(generated_text)
            print("--- End of Response ---\n")
            
            # Validate the response has some content
            if not generated_text:
                raise ValueError("Generated response is empty")
            
            return generated_text
        except Exception as e:
            # Comprehensive error handling and logging
            error_message = f"Error generating response: {str(e)}"
            print("\n--- AI Error Debugging ---")
            print(error_message)
            
            # Log additional context if possible
            import traceback
            traceback.print_exc()
            print("--- End of Error ---\n")
            
            # Return a structured error response
            return f"""Case Summary: Unable to generate analysis
Outcome Prediction:
- Favorable Percentage: 50
- Confidence Level: Low
- Rationale: AI analysis failed due to technical error.

Error Details: {error_message}

Disclaimer: This is a fallback response. Please consult with a legal professional for accurate advice."""
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create an embedding vector for the given text
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
        """
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            # In a production environment, add proper error handling and logging
            print(f"Error creating embedding: {e}")
            return []
    
    async def process_prompt(self, prompt: str) -> str:
        """Process a prompt using the OpenAI API
        
        Args:
            prompt: The prompt to process
            
        Returns:
            The generated response
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a legal assistant that specializes in drafting legal clauses for Canadian jurisdictions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            # In a production environment, add proper error handling and logging
            print(f"Error processing prompt: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing prompt: {str(e)}")
