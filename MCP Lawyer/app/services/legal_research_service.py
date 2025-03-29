from typing import List, Dict, Any, Optional
import json
import re
from fastapi import HTTPException
from app.services.ai_processor import AIProcessor

class LegalResearchService:
    """Service for legal research and case law retrieval"""
    
    def __init__(self, ai_processor: AIProcessor):
        """Initialize the legal research service
        
        Args:
            ai_processor: Service for processing AI requests
        """
        self.ai_processor = ai_processor
        self.case_law_databases = self._initialize_case_law_databases()
        self.legislation_databases = self._initialize_legislation_databases()
        
    def _initialize_case_law_databases(self) -> Dict[str, Dict[str, Any]]:
        """Initialize case law database references
        
        Returns:
            Dictionary of case law databases
        """
        return {
            "canlii": {
                "name": "CanLII",
                "description": "Canadian Legal Information Institute",
                "url": "https://www.canlii.org/",
                "search_url": "https://www.canlii.org/en/#search/type=decision&text=",
                "jurisdictions": ["federal", "all_provinces"],
                "content_types": ["cases"]
            },
            "westlaw": {
                "name": "Westlaw Canada",
                "description": "Comprehensive legal research database",
                "url": "https://www.westlaw.com/",
                "search_url": "https://www.westlaw.com/search/results/",
                "jurisdictions": ["federal", "all_provinces"],
                "content_types": ["cases", "commentary"]
            },
            "lexisnexis": {
                "name": "LexisNexis Quicklaw",
                "description": "Comprehensive legal research database",
                "url": "https://www.lexisnexis.ca/",
                "search_url": "https://www.lexisnexis.ca/search/",
                "jurisdictions": ["federal", "all_provinces"],
                "content_types": ["cases", "commentary"]
            }
        }
    
    def _initialize_legislation_databases(self) -> Dict[str, Dict[str, Any]]:
        """Initialize legislation database references
        
        Returns:
            Dictionary of legislation databases
        """
        return {
            "canlii_legislation": {
                "name": "CanLII Legislation",
                "description": "Canadian Legal Information Institute - Legislation",
                "url": "https://www.canlii.org/",
                "search_url": "https://www.canlii.org/en/#search/type=legislation&text=",
                "jurisdictions": ["federal", "all_provinces"],
                "content_types": ["statutes", "regulations"]
            },
            "justice_laws": {
                "name": "Justice Laws Website",
                "description": "Official source for federal laws and regulations",
                "url": "https://laws-lois.justice.gc.ca/",
                "search_url": "https://laws-lois.justice.gc.ca/Search/",
                "jurisdictions": ["federal"],
                "content_types": ["statutes", "regulations"]
            }
        }
    
    async def search_case_law(self, query: str, jurisdiction: Optional[str] = None, database: Optional[str] = None) -> Dict[str, Any]:
        """Search for relevant case law based on query
        
        Args:
            query: Search query
            jurisdiction: Optional jurisdiction filter
            database: Optional database to search
            
        Returns:
            Search results with relevant cases
        """
        # Determine which database to use
        if database and database not in self.case_law_databases:
            raise HTTPException(status_code=404, detail=f"Case law database '{database}' not found")
        
        # Use CanLII as default if not specified
        db_to_use = database if database else "canlii"
        db_info = self.case_law_databases[db_to_use]
        
        # Create a prompt for the AI to generate search results
        system_prompt = f"""You are a legal research assistant specializing in Canadian case law.
        Based on the search query, provide relevant case law results that would be found in {db_info['name']}.
        Focus on the most relevant and recent cases that address the legal issue.
        If a jurisdiction is specified, prioritize cases from that jurisdiction.
        Format each case with proper citation, a brief summary, and key holdings.
        Provide at least 3-5 relevant cases if available.
        """
        
        user_prompt = f"""Please find relevant Canadian case law for the following query:
        
        Query: {query}
        {f'Jurisdiction: {jurisdiction}' if jurisdiction else ''}
        
        For each case, provide:
        1. Case name and citation
        2. Year of decision
        3. Court/jurisdiction
        4. Brief summary (2-3 sentences)
        5. Key holdings or principles established
        6. Relevance to the query (1-2 sentences)
        """
        
        # Process the prompt through the AI processor
        results = await self.ai_processor.generate_response(system_prompt, user_prompt)
        
        # Create a structured response
        search_url = f"{db_info['search_url']}{query.replace(' ', '%20')}"
        
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "database": {
                "id": db_to_use,
                "name": db_info["name"],
                "description": db_info["description"],
                "url": db_info["url"],
                "search_url": search_url
            },
            "results": results,
            "disclaimer": "These results are AI-generated and should be verified through proper legal research."
        }
    
    async def search_legislation(self, query: str, jurisdiction: Optional[str] = None, database: Optional[str] = None) -> Dict[str, Any]:
        """Search for relevant legislation based on query
        
        Args:
            query: Search query
            jurisdiction: Optional jurisdiction filter
            database: Optional database to search
            
        Returns:
            Search results with relevant legislation
        """
        # Determine which database to use
        if database and database not in self.legislation_databases:
            raise HTTPException(status_code=404, detail=f"Legislation database '{database}' not found")
        
        # Use CanLII as default if not specified
        db_to_use = database if database else "canlii_legislation"
        db_info = self.legislation_databases[db_to_use]
        
        # Create a prompt for the AI to generate search results
        system_prompt = f"""You are a legal research assistant specializing in Canadian legislation.
        Based on the search query, provide relevant legislative results that would be found in {db_info['name']}.
        Focus on the most relevant and current legislation that addresses the legal issue.
        If a jurisdiction is specified, prioritize legislation from that jurisdiction.
        Format each result with proper citation, relevant sections, and a brief explanation.
        Provide at least 2-4 relevant legislative references if available.
        """
        
        user_prompt = f"""Please find relevant Canadian legislation for the following query:
        
        Query: {query}
        {f'Jurisdiction: {jurisdiction}' if jurisdiction else ''}
        
        For each legislative reference, provide:
        1. Name of the act or regulation and citation
        2. Jurisdiction
        3. Relevant sections or provisions
        4. Brief explanation of how it relates to the query
        5. Any notable amendments or changes
        """
        
        # Process the prompt through the AI processor
        results = await self.ai_processor.generate_response(system_prompt, user_prompt)
        
        # Create a structured response
        search_url = f"{db_info['search_url']}{query.replace(' ', '%20')}"
        
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "database": {
                "id": db_to_use,
                "name": db_info["name"],
                "description": db_info["description"],
                "url": db_info["url"],
                "search_url": search_url
            },
            "results": results,
            "disclaimer": "These results are AI-generated and should be verified through proper legal research."
        }
    
    async def get_case_brief(self, case_citation: str) -> Dict[str, Any]:
        """Generate a case brief for a given case citation
        
        Args:
            case_citation: Citation of the case to brief
            
        Returns:
            Case brief with key information
        """
        # Create a prompt for the AI to generate a case brief
        system_prompt = """You are a legal research assistant specializing in Canadian case law.
        Create a comprehensive case brief for the given citation.
        Follow the standard case briefing format used in Canadian law schools and practice.
        Be thorough but concise in your analysis.
        """
        
        user_prompt = f"""Please create a detailed case brief for the following case:
        
        Citation: {case_citation}
        
        Include the following sections in your brief:
        1. Case Name and Citation
        2. Court and Year
        3. Judges
        4. Facts (concise summary)
        5. Issues (legal questions presented)
        6. Holding (court's decision on each issue)
        7. Reasoning (court's analysis and rationale)
        8. Significant Principles Established
        9. Dissenting Opinions (if any)
        10. Subsequent Treatment (if significant)
        """
        
        # Process the prompt through the AI processor
        brief = await self.ai_processor.generate_response(system_prompt, user_prompt)
        
        return {
            "citation": case_citation,
            "brief": brief,
            "disclaimer": "This case brief is AI-generated and should be verified through proper legal research."
        }
