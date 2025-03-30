from typing import List, Dict, Optional, Union, Any, Tuple
from datetime import datetime
import re
import uuid

from ..models.contract_analysis_models import (
    ContractClause,
    ClauseCategory,
    RiskLevel,
    ClauseAnalysis,
    ContractSummary,
    ContractAnalysisRequest,
    ContractAnalysisResult,
    ContractComparisonRequest,
    ClauseDifference,
    ContractComparisonResult,
    StandardTemplate,
    TemplateMatch,
    RiskAssessmentSettings
)

from .ai_processor import AIProcessor


class ContractAnalysisService:
    """Service for analyzing legal contracts, extracting clauses, and assessing risks"""
    
    def __init__(self, ai_processor: AIProcessor):
        self.ai_processor = ai_processor
        # This would typically connect to a database for templates and settings
        self.standard_templates: Dict[str, StandardTemplate] = {}
        self.default_risk_settings = RiskAssessmentSettings(
            jurisdiction="Canada",
            risk_weights={
                ClauseCategory.INDEMNIFICATION: 1.5,
                ClauseCategory.LIABILITY: 1.5,
                ClauseCategory.TERMINATION: 1.2,
                ClauseCategory.CONFIDENTIALITY: 1.0,
                ClauseCategory.INTELLECTUAL_PROPERTY: 1.3,
                # Other categories would have default weights
            }
        )
    
    async def analyze_contract(self, request: ContractAnalysisRequest) -> ContractAnalysisResult:
        """Analyze a contract and return a detailed analysis result"""
        # Extract clauses from the contract text
        clauses = await self._extract_clauses(request.contract_text)
        
        # Analyze each clause for risks and other insights
        clause_analyses = []
        for clause in clauses:
            analysis = await self._analyze_clause(clause, request.jurisdiction)
            clause_analyses.append(analysis)
            
            # If template comparison is requested, add that information
            if request.comparison_template_ids:
                template_matches = await self._compare_to_templates(
                    clause, request.comparison_template_ids
                )
                analysis.template_matches = template_matches
        
        # Generate an overall summary and risk assessment
        summary = await self._generate_summary(request, clauses)
        overall_risk, explanation, score = await self._assess_overall_risk(clause_analyses)
        recommendations = await self._generate_recommendations(clause_analyses, summary)
        
        # Assemble the final result
        result = ContractAnalysisResult(
            summary=summary,
            clauses=clause_analyses,
            overall_risk_level=overall_risk,
            overall_risk_explanation=explanation,
            overall_score=score,
            recommendations=recommendations,
            metadata={
                "contract_type": request.contract_type or "Unknown",
                "jurisdiction": request.jurisdiction or "Unknown",
                "analysis_version": "1.0"
            }
        )
        
        return result
    
    async def compare_contracts(self, request: ContractComparisonRequest) -> ContractComparisonResult:
        """Compare two contracts and identify significant differences"""
        # Extract clauses from both contracts
        clauses_a = await self._extract_clauses(request.contract_a_text)
        clauses_b = await self._extract_clauses(request.contract_b_text)
        
        # Group clauses by category for easier comparison
        grouped_a = self._group_clauses_by_category(clauses_a)
        grouped_b = self._group_clauses_by_category(clauses_b)
        
        # Identify common and unique categories
        categories_a = set(grouped_a.keys())
        categories_b = set(grouped_b.keys())
        common_categories = list(categories_a.intersection(categories_b))
        unique_to_a = list(categories_a - categories_b)
        unique_to_b = list(categories_b - categories_a)
        
        # Analyze differences between common categories
        differences = []
        for category in common_categories:
            if request.focus_categories and category not in request.focus_categories:
                continue
                
            clause_a = grouped_a[category]
            clause_b = grouped_b[category]
            
            if clause_a.text != clause_b.text:
                diff = await self._analyze_difference(clause_a, clause_b)
                differences.append(diff)
        
        # Generate a recommendation based on the differences
        recommendation = await self._generate_comparison_recommendation(
            differences, unique_to_a, unique_to_b
        )
        
        # Assemble the final comparison result
        result = ContractComparisonResult(
            contract_a_name=request.contract_a_name or "Contract A",
            contract_b_name=request.contract_b_name or "Contract B",
            common_clauses=common_categories,
            unique_to_a=unique_to_a,
            unique_to_b=unique_to_b,
            differences=differences,
            recommendation=recommendation
        )
        
        return result
        
    async def _extract_clauses(self, contract_text: str) -> List[ContractClause]:
        """Extract and categorize clauses from contract text using AI"""
        prompt = f"""
You are a legal expert specializing in contract analysis. Extract all clauses from the following contract.
For each clause:
1. Identify a descriptive title
2. Categorize the clause into one of these categories: {', '.join([c.value for c in ClauseCategory])}
3. Determine the risk level: no_risk, low_risk, medium_risk, high_risk, critical_risk
4. Provide a brief explanation for the risk assessment

Contract text:
{contract_text}

Output a JSON list of clauses, with each clause having: title, text, category, risk_level, and risk_explanation.
"""

        result = await self.ai_processor.process_text(prompt, model="gpt-4o-mini")
        
        # Parse the JSON response - in a real implementation, would add more robust error handling
        import json
        try:
            clauses_data = json.loads(result)
            clauses = []
            
            for idx, clause_data in enumerate(clauses_data):
                clause = ContractClause(
                    title=clause_data.get("title", f"Clause {idx+1}"),
                    text=clause_data.get("text", ""),
                    category=clause_data.get("category", ClauseCategory.OTHER),
                    risk_level=clause_data.get("risk_level", RiskLevel.LOW_RISK),
                    risk_explanation=clause_data.get("risk_explanation", ""),
                    position={"start": contract_text.find(clause_data.get("text", "")), "end": 0}
                )
                
                # Calculate the end position if the text was found
                if clause.position["start"] >= 0:
                    clause.position["end"] = clause.position["start"] + len(clause.text)
                    
                clauses.append(clause)
                
            return clauses
            
        except json.JSONDecodeError:
            # Fallback behavior: create a single clause for the entire contract
            return [
                ContractClause(
                    title="Full Contract",
                    text=contract_text[:1000] + ("..." if len(contract_text) > 1000 else ""),
                    category=ClauseCategory.OTHER,
                    risk_level=RiskLevel.MEDIUM_RISK,
                    risk_explanation="Unable to parse contract into clauses. Manual review recommended."
                )
            ]

    async def _analyze_clause(self, clause: ContractClause, jurisdiction: Optional[str] = None) -> ClauseAnalysis:
        """Analyze a specific contract clause for risks and alternative wording"""
        jurisdiction_text = f" in {jurisdiction}" if jurisdiction else ""
        
        prompt = f"""
As a legal expert, analyze this {clause.category.value} clause{jurisdiction_text}:

{clause.text}

Provide:
1. Alternative wording that might be more favorable (if applicable)
2. Provincial differences to consider for Canadian jurisdictions (if applicable)
3. Key legal concerns with this clause (bullet points)
"""

        result = await self.ai_processor.process_text(prompt, model="gpt-4o-mini")
        
        # Parse the results - in a real implementation would use more structured parsing
        alternative_wording = None
        provincial_differences = None
        legal_concerns = []
        
        # Simple parsing of the AI response
        if "Alternative wording" in result or "Alternative Wording" in result:
            parts = result.split("\n\n")
            for part in parts:
                if part.startswith("Alternative wording") or part.startswith("Alternative Wording"):
                    alternative_wording = part.split(":\n", 1)[1] if ":\n" in part else part
                elif part.startswith("Provincial differences") or part.startswith("Provincial Differences"):
                    prov_text = part.split(":\n", 1)[1] if ":\n" in part else part
                    provincial_differences = {"general": prov_text}
                elif part.startswith("Legal concerns") or part.startswith("Key legal concerns"):
                    concerns_text = part.split(":\n", 1)[1] if ":\n" in part else part
                    legal_concerns = [line.strip().strip('-').strip() for line in concerns_text.split("\n") if line.strip()]
        
        return ClauseAnalysis(
            clause=clause,
            alternative_wording=alternative_wording,
            provincial_differences=provincial_differences,
            legal_concerns=legal_concerns
        )
    
    async def _compare_to_templates(self, clause: ContractClause, template_ids: List[str]) -> List[TemplateMatch]:
        """Compare a clause to standard templates"""
        matches = []
        
        for template_id in template_ids:
            if template_id not in self.standard_templates:
                continue
                
            template = self.standard_templates[template_id]
            
            # Only compare if the template has a clause of the same category
            if clause.category not in template.clauses:
                continue
                
            template_clause_text = template.clauses[clause.category]
            
            # Use AI to compare the clauses and generate a similarity score
            prompt = f"""
            Compare these two {clause.category.value} clauses and determine their similarity on a scale of 0.0 to 1.0:
            
            Clause 1:
            {clause.text}
            
            Standard Template Clause:
            {template_clause_text}
            
            Provide:
            1. A similarity score between 0.0 and 1.0 (where 1.0 is identical)
            2. A brief explanation of key differences
            """
            
            result = await self.ai_processor.process_text(prompt, model="gpt-4o-mini")
            
            # Parse the similarity score - in a production environment, would use more robust parsing
            similarity_score = 0.5  # Default if parsing fails
            differences = "Unknown differences"
            
            # Attempt to extract the similarity score using regex
            score_match = re.search(r'similarity score[:\s]*([0-9]\.[0-9])', result, re.IGNORECASE)
            if score_match:
                try:
                    similarity_score = float(score_match.group(1))
                except ValueError:
                    pass
            
            # Extract differences explanation
            if "differences" in result.lower():
                parts = result.split("\n\n")
                for part in parts:
                    if "differences" in part.lower():
                        differences = part
                        break
            
            matches.append(TemplateMatch(
                template_id=template_id,
                template_name=template.name,
                similarity_score=similarity_score,
                differences=differences
            ))
        
        return matches
    
    async def _generate_summary(self, request: ContractAnalysisRequest, clauses: List[ContractClause]) -> ContractSummary:
        """Generate a summary of the contract"""
        contract_text = request.contract_text
        
        # Use AI to extract summary information
        prompt = f"""
        As a legal expert, provide a summary of this contract:
        
        {contract_text[:5000]}...  # Truncated for API limits
        
        Extract:
        1. Contract title/type
        2. All parties involved
        3. Effective date (if available)
        4. Termination date (if available)
        5. 3-5 key points of the agreement
        6. Any important clauses that appear to be missing
        """
        
        result = await self.ai_processor.process_text(prompt, model="gpt-4o-mini")
        
        # Parse the summary information - in a production environment, would use more structured parsing
        title = request.contract_name or "Unnamed Contract"
        contract_type = request.contract_type or "General Contract"
        parties = []
        effective_date = None
        termination_date = None
        key_points = []
        missing_clauses = []
        
        # Simple parsing of the AI response
        if "Contract title" in result or "Title" in result:
            parts = result.split("\n\n")
            for part in parts:
                if "Contract title" in part or "Title" in part:
                    title_line = next((line for line in part.split("\n") if ":" in line), None)
                    if title_line:
                        title = title_line.split(":", 1)[1].strip()
                
                if "Contract type" in part or "Type" in part:
                    type_line = next((line for line in part.split("\n") if ":" in line), None)
                    if type_line:
                        contract_type = type_line.split(":", 1)[1].strip()
                
                if "Parties" in part:
                    parties_text = part.split("Parties:", 1)[1].strip() if "Parties:" in part else ""
                    parties = [p.strip() for p in parties_text.split("\n") if p.strip()]
                
                if "Key points" in part:
                    key_points_text = part.split("Key points:", 1)[1].strip() if "Key points:" in part else ""
                    key_points = [p.strip().strip('-').strip() for p in key_points_text.split("\n") if p.strip()]
                
                if "Missing clauses" in part:
                    missing_text = part.split("Missing clauses:", 1)[1].strip() if "Missing clauses:" in part else ""
                    missing_clauses = [p.strip().strip('-').strip() for p in missing_text.split("\n") if p.strip()]
        
        # Attempt to parse dates
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+ \d{1,2},? \d{4})\b'
        if "Effective date" in result:
            effective_dates = re.findall(date_pattern, result.split("Effective date", 1)[1].split("\n", 1)[0])
            if effective_dates:
                try:
                    # In a real implementation, would use a proper date parser
                    effective_date = datetime.now()  # Placeholder
                except:
                    pass
        
        if "Termination date" in result:
            termination_dates = re.findall(date_pattern, result.split("Termination date", 1)[1].split("\n", 1)[0])
            if termination_dates:
                try:
                    # In a real implementation, would use a proper date parser
                    termination_date = datetime.now()  # Placeholder
                except:
                    pass
        
        return ContractSummary(
            title=title,
            contract_type=contract_type,
            parties=parties if parties else ["Unknown"],
            effective_date=effective_date,
            termination_date=termination_date,
            key_points=key_points,
            missing_clauses=missing_clauses
        )
        
    async def _assess_overall_risk(self, clause_analyses: List[ClauseAnalysis]) -> Tuple[RiskLevel, str, int]:
        """Assess the overall risk level of a contract based on its clauses"""
        # Count the occurrences of each risk level
        risk_counts = {
            RiskLevel.NO_RISK: 0,
            RiskLevel.LOW_RISK: 0,
            RiskLevel.MEDIUM_RISK: 0,
            RiskLevel.HIGH_RISK: 0,
            RiskLevel.CRITICAL_RISK: 0
        }
        
        # Weighted risk factors for different categories
        category_weights = self.default_risk_settings.risk_weights
        
        for analysis in clause_analyses:
            clause = analysis.clause
            weight = category_weights.get(clause.category, 1.0)
            risk_counts[clause.risk_level] += 1 * weight
        
        # Calculate a weighted risk score (0-100 scale)
        max_possible_score = sum(category_weights.values()) * 4 if category_weights else len(clause_analyses) * 4
        current_score = (
            risk_counts[RiskLevel.NO_RISK] * 0 +
            risk_counts[RiskLevel.LOW_RISK] * 1 +
            risk_counts[RiskLevel.MEDIUM_RISK] * 2 +
            risk_counts[RiskLevel.HIGH_RISK] * 3 +
            risk_counts[RiskLevel.CRITICAL_RISK] * 4
        )
        
        normalized_score = 100 - int((current_score / max_possible_score) * 100) if max_possible_score > 0 else 50
        normalized_score = max(0, min(100, normalized_score))  # Ensure score is between 0-100
        
        # Determine overall risk level based on presence of high/critical risks
        # and overall normalized score
        overall_risk = RiskLevel.LOW_RISK  # Default
        
        if risk_counts[RiskLevel.CRITICAL_RISK] > 0:
            overall_risk = RiskLevel.CRITICAL_RISK
        elif risk_counts[RiskLevel.HIGH_RISK] > 1:
            overall_risk = RiskLevel.HIGH_RISK
        elif risk_counts[RiskLevel.MEDIUM_RISK] > 2 or risk_counts[RiskLevel.HIGH_RISK] == 1:
            overall_risk = RiskLevel.MEDIUM_RISK
        
        # Generate explanation
        high_risk_clauses = [analysis.clause.title for analysis in clause_analyses 
                            if analysis.clause.risk_level in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL_RISK]]
        
        if high_risk_clauses:
            explanation = f"This contract has {len(high_risk_clauses)} high or critical risk clauses that require attention: {', '.join(high_risk_clauses)}. "
        else:
            explanation = "This contract has no high or critical risk clauses. "
            
        explanation += f"Overall contract risk score: {normalized_score}/100. "
        
        return overall_risk, explanation, normalized_score
    
    async def _generate_recommendations(self, clause_analyses: List[ClauseAnalysis], summary: ContractSummary) -> List[str]:
        """Generate recommendations for improving the contract"""
        recommendations = []
        
        # Add recommendations for high-risk clauses
        for analysis in clause_analyses:
            if analysis.clause.risk_level in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL_RISK]:
                if analysis.alternative_wording:
                    recommendations.append(f"Revise the {analysis.clause.title} clause with more favorable language.")
                else:
                    recommendations.append(f"Review and potentially renegotiate the {analysis.clause.title} clause.")
        
        # Add recommendations for missing clauses
        for missing in summary.missing_clauses:
            recommendations.append(f"Add a missing {missing} clause to the contract.")
        
        # If there are no specific recommendations, add a general one
        if not recommendations:
            recommendations.append("This contract appears to have reasonable terms, but a thorough review by qualified legal counsel is always recommended.")
        
        return recommendations
    
    def _group_clauses_by_category(self, clauses: List[ContractClause]) -> Dict[ClauseCategory, ContractClause]:
        """Group clauses by their category for easier comparison"""
        result = {}
        for clause in clauses:
            # If multiple clauses have the same category, keep the last one for simplicity
            # In a real implementation, might want to merge them or handle differently
            result[clause.category] = clause
        return result
    
    async def _analyze_difference(self, clause_a: ContractClause, clause_b: ContractClause) -> ClauseDifference:
        """Analyze the difference between two clauses"""
        prompt = f"""
        Compare these two {clause_a.category.value} clauses and explain the significance of their differences:
        
        Clause A:
        {clause_a.text}
        
        Clause B:
        {clause_b.text}
        
        Provide:
        1. Significance level (no_risk, low_risk, medium_risk, high_risk, critical_risk)
        2. Brief explanation of the legal implications of these differences
        """
        
        result = await self.ai_processor.process_text(prompt, model="gpt-4o-mini")
        
        # Default values
        significance = RiskLevel.MEDIUM_RISK
        explanation = "There are notable differences between these clauses that may affect legal rights and obligations."
        
        # Attempt to extract significance level
        for risk_level in RiskLevel:
            if risk_level.value in result.lower():
                significance = risk_level
                break
        
        # Extract explanation
        explanation_parts = result.split("\n\n")
        for part in explanation_parts:
            if "implication" in part.lower() or "explanation" in part.lower():
                explanation = part
                break
        
        return ClauseDifference(
            category=clause_a.category,
            title=clause_a.title,
            contract_a_text=clause_a.text,
            contract_b_text=clause_b.text,
            significance=significance,
            explanation=explanation
        )
    
    async def _generate_comparison_recommendation(self, differences: List[ClauseDifference], 
                                               unique_to_a: List[ClauseCategory], 
                                               unique_to_b: List[ClauseCategory]) -> str:
        """Generate overall recommendation based on contract comparison"""
        high_risk_differences = [d for d in differences if d.significance in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL_RISK]]
        
        recommendation_parts = []
        
        if high_risk_differences:
            high_risk_categories = [d.category.value for d in high_risk_differences]
            recommendation_parts.append(f"Pay close attention to significant differences in the following clauses: {', '.join(high_risk_categories)}.")
        
        if unique_to_a:
            unique_a_values = [c.value for c in unique_to_a]
            recommendation_parts.append(f"Contract A contains these clauses not found in Contract B: {', '.join(unique_a_values)}.")
            
        if unique_to_b:
            unique_b_values = [c.value for c in unique_to_b]
            recommendation_parts.append(f"Contract B contains these clauses not found in Contract A: {', '.join(unique_b_values)}.")
        
        if not recommendation_parts:
            recommendation_parts.append("Both contracts are substantially similar in their legal provisions.")
            
        recommendation_parts.append("For a complete legal assessment, consult with qualified legal counsel in the relevant jurisdiction.")
        
        return " ".join(recommendation_parts)
    
    async def add_template(self, template: StandardTemplate) -> str:
        """Add a standard template for comparison"""
        self.standard_templates[template.id] = template
        return template.id
    
    async def get_template(self, template_id: str) -> Optional[StandardTemplate]:
        """Retrieve a standard template by ID"""
        return self.standard_templates.get(template_id)
