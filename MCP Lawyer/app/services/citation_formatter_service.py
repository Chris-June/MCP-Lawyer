from typing import Dict, Any, List, Optional
import re
from fastapi import HTTPException
from app.services.ai_processor import AIProcessor

class CitationFormatterService:
    """Service for formatting legal citations according to Canadian standards"""
    
    def __init__(self, ai_processor: AIProcessor):
        """Initialize the citation formatter service
        
        Args:
            ai_processor: Service for processing AI requests
        """
        self.ai_processor = ai_processor
        self.citation_styles = self._initialize_citation_styles()
    
    def _initialize_citation_styles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize citation styles
        
        Returns:
            Dictionary of citation styles
        """
        return {
            "mcgill": {
                "name": "McGill Guide",
                "description": "Canadian Guide to Uniform Legal Citation (McGill Guide)",
                "version": "9th Edition",
                "is_default": True
            },
            "bluebook": {
                "name": "Bluebook",
                "description": "The Bluebook: A Uniform System of Citation",
                "version": "21st Edition",
                "is_default": False
            },
            "apa": {
                "name": "APA",
                "description": "American Psychological Association Style",
                "version": "7th Edition",
                "is_default": False
            }
        }
    
    async def format_case_citation(self, case_info: Dict[str, str], style: Optional[str] = None) -> Dict[str, Any]:
        """Format a case citation according to the specified style
        
        Args:
            case_info: Information about the case
            style: Citation style to use (default: McGill Guide)
            
        Returns:
            Formatted citation
        """
        # Validate citation style
        if style and style not in self.citation_styles:
            raise HTTPException(status_code=404, detail=f"Citation style '{style}' not found")
        
        # Use default style if not specified
        style_to_use = style if style else "mcgill"
        style_info = self.citation_styles[style_to_use]
        
        # Validate required case information
        required_fields = ["case_name", "year", "volume", "reporter", "page"]
        missing_fields = [field for field in required_fields if field not in case_info or not case_info[field]]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required case information: {', '.join(missing_fields)}"
            )
        
        # Create a prompt for the AI to format the citation
        system_prompt = f"""You are a legal citation expert specializing in the {style_info['name']} ({style_info['version']}).
        Format the provided case information according to the {style_info['name']} citation style.
        Provide only the formatted citation without any additional text or explanation.
        """
        
        user_prompt = f"""Please format the following case information according to the {style_info['name']} citation style:
        
        Case Name: {case_info['case_name']}
        Year: {case_info['year']}
        Volume: {case_info['volume']}
        Reporter: {case_info['reporter']}
        Page: {case_info['page']}
        {f'Court: {case_info["court"]}' if 'court' in case_info else ''}
        {f'Jurisdiction: {case_info["jurisdiction"]}' if 'jurisdiction' in case_info else ''}
        
        Provide only the formatted citation without any additional text.
        """
        
        # Process the prompt through the AI processor
        formatted_citation = await self.ai_processor.generate_response(system_prompt, user_prompt)
        
        # Clean up the formatted citation (remove any extra text the AI might have added)
        formatted_citation = formatted_citation.strip()
        if formatted_citation.startswith('"') and formatted_citation.endswith('"'):
            formatted_citation = formatted_citation[1:-1]
        
        return {
            "case_info": case_info,
            "style": {
                "id": style_to_use,
                "name": style_info["name"],
                "version": style_info["version"]
            },
            "formatted_citation": formatted_citation
        }
    
    async def format_legislation_citation(self, legislation_info: Dict[str, str], style: Optional[str] = None) -> Dict[str, Any]:
        """Format a legislation citation according to the specified style
        
        Args:
            legislation_info: Information about the legislation
            style: Citation style to use (default: McGill Guide)
            
        Returns:
            Formatted citation
        """
        # Validate citation style
        if style and style not in self.citation_styles:
            raise HTTPException(status_code=404, detail=f"Citation style '{style}' not found")
        
        # Use default style if not specified
        style_to_use = style if style else "mcgill"
        style_info = self.citation_styles[style_to_use]
        
        # Validate required legislation information
        required_fields = ["title", "jurisdiction", "year", "chapter"]
        missing_fields = [field for field in required_fields if field not in legislation_info or not legislation_info[field]]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required legislation information: {', '.join(missing_fields)}"
            )
        
        # Create a prompt for the AI to format the citation
        system_prompt = f"""You are a legal citation expert specializing in the {style_info['name']} ({style_info['version']}).
        Format the provided legislation information according to the {style_info['name']} citation style.
        Provide only the formatted citation without any additional text or explanation.
        """
        
        user_prompt = f"""Please format the following legislation information according to the {style_info['name']} citation style:
        
        Title: {legislation_info['title']}
        Jurisdiction: {legislation_info['jurisdiction']}
        Year: {legislation_info['year']}
        Chapter: {legislation_info['chapter']}
        {f'Statute Volume: {legislation_info["statute_volume"]}' if 'statute_volume' in legislation_info else ''}
        {f'Sections: {legislation_info["sections"]}' if 'sections' in legislation_info else ''}
        
        Provide only the formatted citation without any additional text.
        """
        
        # Process the prompt through the AI processor
        formatted_citation = await self.ai_processor.generate_response(system_prompt, user_prompt)
        
        # Clean up the formatted citation (remove any extra text the AI might have added)
        formatted_citation = formatted_citation.strip()
        if formatted_citation.startswith('"') and formatted_citation.endswith('"'):
            formatted_citation = formatted_citation[1:-1]
        
        return {
            "legislation_info": legislation_info,
            "style": {
                "id": style_to_use,
                "name": style_info["name"],
                "version": style_info["version"]
            },
            "formatted_citation": formatted_citation
        }
    
    async def parse_citation(self, citation_text: str) -> Dict[str, Any]:
        """Parse a citation into its components
        
        Args:
            citation_text: The citation text to parse
            
        Returns:
            Parsed citation components
        """
        # Create a prompt for the AI to parse the citation
        system_prompt = """You are a legal citation expert.
        Parse the provided citation into its components.
        Identify whether it's a case citation or legislation citation.
        Extract all relevant components and return them in a structured format.
        """
        
        user_prompt = f"""Please parse the following citation into its components:
        
        Citation: {citation_text}
        
        First, determine if this is a case citation or legislation citation.
        
        If it's a case citation, extract:
        - Case name
        - Year
        - Volume (if applicable)
        - Reporter
        - Page
        - Court (if included)
        - Jurisdiction (if included)
        
        If it's legislation, extract:
        - Title of the act/regulation
        - Jurisdiction
        - Year
        - Chapter
        - Statute volume (if applicable)
        - Sections (if specified)
        
        Format your response as a structured analysis of the citation components.
        """
        
        # Process the prompt through the AI processor
        parsed_result = await self.ai_processor.generate_response(system_prompt, user_prompt)
        
        return {
            "original_citation": citation_text,
            "parsed_result": parsed_result
        }
    
    async def get_citation_styles(self) -> List[Dict[str, Any]]:
        """Get all available citation styles
        
        Returns:
            List of citation styles
        """
        styles = []
        for style_id, style_info in self.citation_styles.items():
            styles.append({
                "id": style_id,
                **style_info
            })
        return styles
