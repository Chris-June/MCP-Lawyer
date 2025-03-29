from typing import List, Dict, Any, Optional
import json
from fastapi import HTTPException
from app.services.ai_processor import AIProcessor

class PredictiveAnalysisService:
    """Service for predictive case outcome analysis"""
    
    def __init__(self, ai_processor: AIProcessor):
        """Initialize the predictive analysis service
        
        Args:
            ai_processor: Service for processing AI requests
        """
        self.ai_processor = ai_processor
    
    async def analyze_case_outcome(self, 
                                 case_facts: str, 
                                 legal_issues: List[str], 
                                 jurisdiction: str,
                                 relevant_statutes: Optional[List[str]] = None,
                                 similar_cases: Optional[List[str]] = None,
                                 client_position: str = "",
                                 opposing_arguments: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a case and predict potential outcomes
        
        Args:
            case_facts: Facts of the case
            legal_issues: List of legal issues involved
            jurisdiction: Jurisdiction for the case
            relevant_statutes: Optional list of relevant statutes
            similar_cases: Optional list of similar case citations
            client_position: Client's position or argument
            opposing_arguments: Optional opposing party's arguments
            
        Returns:
            Predictive analysis with outcome probabilities and recommendations
        """
        # Create a prompt for the AI to generate predictive analysis
        system_prompt = f"""You are a legal expert specializing in Canadian case outcome prediction.
        Based on the provided case details, predict the likely outcome using similar precedents.
        Analyze the strengths and weaknesses of the case from a legal perspective.
        Consider the jurisdiction, relevant statutes, and similar cases in your analysis.
        Provide a balanced assessment with probability estimates and confidence levels.
        Use a SWOT framework (Strengths, Weaknesses, Opportunities, Threats) for part of your analysis.
        Your analysis should be data-driven, citing relevant precedents and their outcomes.
        """
        
        # Format the legal issues as a string
        legal_issues_str = "\n".join([f"- {issue}" for issue in legal_issues])
        
        # Format relevant statutes if provided
        statutes_str = ""
        if relevant_statutes and len(relevant_statutes) > 0:
            statutes_str = "\nRelevant Statutes:\n" + "\n".join([f"- {statute}" for statute in relevant_statutes])
        
        # Format similar cases if provided
        cases_str = ""
        if similar_cases and len(similar_cases) > 0:
            cases_str = "\nSimilar Cases:\n" + "\n".join([f"- {case}" for case in similar_cases])
        
        # Format opposing arguments if provided
        opposing_str = ""
        if opposing_arguments:
            opposing_str = f"\nOpposing Arguments:\n{opposing_arguments}"
        
        user_prompt = f"""Please analyze the following case and predict the likely outcome:
        
        Case Facts:
        {case_facts}
        
        Legal Issues:
        {legal_issues_str}
        
        Jurisdiction: {jurisdiction}{statutes_str}{cases_str}
        
        Client Position:
        {client_position}{opposing_str}
        
        Please provide:
        1. A brief summary of the case
        2. Outcome prediction with percentage of favorable outcome and confidence level
        3. Similar precedents that influence your prediction
        4. SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
        5. Recommended legal strategies
        6. Alternative outcomes with their probabilities
        
        Format your response in a structured way that can be parsed into sections.
        """
        
        # Process the prompt through the AI processor
        analysis_text = await self.ai_processor.generate_response(system_prompt, user_prompt)
        
        # Parse the AI response to extract structured data
        # This is a simplified parsing approach - in a real system, we would use more robust parsing
        try:
            # Extract outcome prediction
            favorable_outcome_percentage = self._extract_percentage(analysis_text)
            confidence_level = self._extract_confidence_level(analysis_text)
            prediction_rationale = self._extract_section(analysis_text, "Outcome prediction", "Similar precedents")
            
            # Extract similar precedents
            similar_precedents = self._extract_precedents(analysis_text)
            
            # Extract SWOT analysis
            strengths = self._extract_bullet_points(analysis_text, "Strengths")
            weaknesses = self._extract_bullet_points(analysis_text, "Weaknesses")
            opportunities = self._extract_bullet_points(analysis_text, "Opportunities")
            threats = self._extract_bullet_points(analysis_text, "Threats")
            
            # Extract recommended strategies
            strategies = self._extract_bullet_points(analysis_text, "Recommended legal strategies", "Alternative outcomes")
            
            # Extract alternative outcomes
            alternative_outcomes = self._extract_alternative_outcomes(analysis_text)
            
            # Extract case summary
            case_summary = self._extract_section(analysis_text, "Case summary", "Outcome prediction")
            
            # Create structured response
            return {
                "case_summary": case_summary.strip(),
                "outcome_prediction": {
                    "favorable_outcome_percentage": favorable_outcome_percentage,
                    "confidence_level": confidence_level,
                    "prediction_rationale": prediction_rationale.strip()
                },
                "similar_precedents": similar_precedents,
                "strength_weakness_analysis": {
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "opportunities": opportunities,
                    "threats": threats
                },
                "recommended_strategies": strategies,
                "alternative_outcomes": alternative_outcomes,
                "disclaimer": "This predictive analysis is AI-generated and should not be considered legal advice. Consult with a qualified legal professional for specific legal guidance."
            }
        except Exception as e:
            # If parsing fails, return the raw analysis with a basic structure
            return {
                "case_summary": "Analysis could not be fully structured.",
                "outcome_prediction": {
                    "favorable_outcome_percentage": 50,  # Default to 50%
                    "confidence_level": "medium",
                    "prediction_rationale": "See full analysis for details."
                },
                "similar_precedents": [],
                "strength_weakness_analysis": {
                    "strengths": [],
                    "weaknesses": [],
                    "opportunities": [],
                    "threats": []
                },
                "recommended_strategies": [],
                "alternative_outcomes": [],
                "full_analysis": analysis_text,
                "disclaimer": "This predictive analysis is AI-generated and should not be considered legal advice. Consult with a qualified legal professional for specific legal guidance."
            }
    
    def _extract_percentage(self, text: str) -> int:
        """Extract favorable outcome percentage from text"""
        import re
        # Look for patterns like "70%" or "70 percent" near outcome-related terms
        patterns = [
            r"favorable\s+outcome[^\d]*(\d+)\s*%",
            r"likelihood\s+of\s+success[^\d]*(\d+)\s*%",
            r"probability[^\d]*(\d+)\s*%",
            r"chance\s+of\s+success[^\d]*(\d+)\s*%",
            r"(\d+)\s*%\s*chance",
            r"(\d+)\s*%\s*probability",
            r"(\d+)\s*%\s*likelihood"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                return min(100, max(0, int(matches.group(1))))
        
        # Default to 50% if no percentage found
        return 50
    
    def _extract_confidence_level(self, text: str) -> str:
        """Extract confidence level from text"""
        text_lower = text.lower()
        
        # Check for explicit confidence level mentions
        if "high confidence" in text_lower or "strong confidence" in text_lower:
            return "high"
        elif "low confidence" in text_lower or "weak confidence" in text_lower:
            return "low"
        else:
            return "medium"  # Default to medium confidence
    
    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """Extract a section of text between two markers"""
        import re
        pattern = f"{start_marker}.*?(?={end_marker}|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            # Remove the section header
            section = match.group(0)
            section = re.sub(f"{start_marker}[:\s]*", "", section, flags=re.IGNORECASE)
            return section.strip()
        return ""
    
    def _extract_bullet_points(self, text: str, section_name: str, end_section: str = None) -> List[str]:
        """Extract bullet points from a section"""
        # Get the section text
        if end_section:
            section_text = self._extract_section(text, section_name, end_section)
        else:
            # Try to find the section by looking for the header
            import re
            pattern = f"{section_name}[:\s]*([\s\S]*?)(?=\n\s*\n|$)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                section_text = match.group(1)
            else:
                return []
        
        # Extract bullet points (lines starting with -, *, or numbers)
        bullet_points = []
        for line in section_text.split("\n"):
            line = line.strip()
            if line and (line.startswith("-") or line.startswith("*") or re.match(r"^\d+\.\s", line)):
                # Remove the bullet character and trim
                point = re.sub(r"^[-*]\s*|^\d+\.\s*", "", line).strip()
                if point:
                    bullet_points.append(point)
        
        return bullet_points
    
    def _extract_precedents(self, text: str) -> List[Dict[str, Any]]:
        """Extract similar precedents from the analysis"""
        # Get the precedents section
        precedents_section = self._extract_section(text, "Similar precedents", "SWOT analysis")
        if not precedents_section:
            precedents_section = self._extract_section(text, "Similar precedents", "Strengths")
        
        # Split into individual precedents (assume each starts with a case name or bullet point)
        import re
        precedent_blocks = re.split(r"\n\s*[-*]\s+|\n\s*\d+\.\s+|\n\n", precedents_section)
        
        precedents = []
        for block in precedent_blocks:
            block = block.strip()
            if not block:
                continue
                
            # Try to extract case citation
            citation_match = re.search(r"([\w\s]+v\.?\s+[\w\s]+)\s*\(?(\d{4})\)?|([\w\s]+)\s*\(?(\d{4})\)?\s+[\w\s]*\d+\s*[\w\s]*\d+", block)
            citation = citation_match.group(0) if citation_match else "Unnamed precedent"
            
            # Try to extract outcome
            outcome = ""
            if "ruled in favor" in block.lower() or "found for" in block.lower() or "successful" in block.lower():
                outcome = "Favorable"
            elif "ruled against" in block.lower() or "found against" in block.lower() or "unsuccessful" in block.lower():
                outcome = "Unfavorable"
            else:
                outcome = "Mixed/Unclear"
            
            # Try to extract key factors
            key_factors = []
            factors_match = re.search(r"factors?:([^\n]*(?:\n(?!\n)[^\n]*)*)", block, re.IGNORECASE)
            if factors_match:
                factors_text = factors_match.group(1)
                # Split by commas or bullet points
                for factor in re.split(r"[,;]|\n\s*[-*]\s+", factors_text):
                    factor = factor.strip()
                    if factor:
                        key_factors.append(factor)
            
            # If no explicit factors found, try to extract sentences that might contain factors
            if not key_factors:
                sentences = re.split(r"\. ", block)
                for sentence in sentences[1:]:  # Skip the first sentence (likely the citation)
                    if len(sentence) > 15 and not sentence.startswith("The court") and "ruled" not in sentence.lower():
                        key_factors.append(sentence.strip() + ".")
                        if len(key_factors) >= 2:  # Limit to 2 factors if extracting this way
                            break
            
            # Calculate a simple relevance score (0-100)
            relevance_score = 0
            if "highly relevant" in block.lower() or "directly applicable" in block.lower():
                relevance_score = 90
            elif "relevant" in block.lower() or "similar" in block.lower():
                relevance_score = 75
            elif "somewhat relevant" in block.lower() or "partially applicable" in block.lower():
                relevance_score = 60
            elif "tangentially" in block.lower() or "indirectly" in block.lower():
                relevance_score = 40
            else:
                relevance_score = 50  # Default middle relevance
            
            precedents.append({
                "case_citation": citation,
                "relevance_score": relevance_score,
                "outcome": outcome,
                "key_factors": key_factors if key_factors else ["See full analysis for details"]
            })
        
        return precedents
    
    def _extract_alternative_outcomes(self, text: str) -> List[Dict[str, Any]]:
        """Extract alternative outcomes from the analysis"""
        # Get the alternative outcomes section
        alt_outcomes_section = self._extract_section(text, "Alternative outcomes", "Disclaimer")
        if not alt_outcomes_section:
            alt_outcomes_section = self._extract_section(text, "Alternative outcomes", "$")
        
        # Split into individual outcomes (assume each starts with a bullet point)
        import re
        outcome_blocks = re.split(r"\n\s*[-*]\s+|\n\s*\d+\.\s+", alt_outcomes_section)
        
        outcomes = []
        for block in outcome_blocks:
            block = block.strip()
            if not block:
                continue
                
            # Try to extract scenario description (first sentence or clause)
            scenario_match = re.match(r"([^:.]*)[:.]?", block)
            scenario = scenario_match.group(1).strip() if scenario_match else block
            
            # Try to extract probability
            probability_match = re.search(r"(\d+)\s*%", block)
            probability = int(probability_match.group(1)) if probability_match else 0
            
            # Try to extract impact
            impact = ""
            if "significant" in block.lower() or "severe" in block.lower() or "major" in block.lower():
                impact = "High impact"
            elif "moderate" in block.lower() or "medium" in block.lower():
                impact = "Moderate impact"
            elif "minor" in block.lower() or "minimal" in block.lower() or "small" in block.lower():
                impact = "Low impact"
            else:
                impact = "Undetermined impact"
            
            # Only add if we have a meaningful scenario
            if len(scenario) > 5:
                outcomes.append({
                    "scenario": scenario,
                    "probability": probability,
                    "impact": impact
                })
        
        # If no outcomes were extracted, create a default one
        if not outcomes:
            outcomes.append({
                "scenario": "Alternative resolution through settlement",
                "probability": 30,
                "impact": "Moderate impact"
            })
        
        return outcomes
