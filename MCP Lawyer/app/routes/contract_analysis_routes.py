from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..models.contract_analysis_models import (
    ContractAnalysisRequest,
    ContractAnalysisResult,
    ContractComparisonRequest,
    ContractComparisonResult,
    StandardTemplate
)
from ..services.contract_analysis_service import ContractAnalysisService
from ..services.ai_processor import AIProcessor
from ..dependencies.services import get_ai_processor

# Create a router for contract analysis endpoints
router = APIRouter(
    prefix="/contract-analysis",
    tags=["contract-analysis"],
    responses={404: {"description": "Not found"}},
)

# Service dependency
def get_contract_analysis_service(ai_processor: AIProcessor = Depends(get_ai_processor)):
    return ContractAnalysisService(ai_processor)


@router.post("/analyze", response_model=ContractAnalysisResult, status_code=status.HTTP_200_OK)
async def analyze_contract(request: ContractAnalysisRequest, 
                          service: ContractAnalysisService = Depends(get_contract_analysis_service)):
    """Analyze a contract for risks, clauses, and recommendations"""
    try:
        result = await service.analyze_contract(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing contract: {str(e)}"
        )


@router.post("/compare", response_model=ContractComparisonResult, status_code=status.HTTP_200_OK)
async def compare_contracts(request: ContractComparisonRequest, 
                           service: ContractAnalysisService = Depends(get_contract_analysis_service)):
    """Compare two contracts and identify differences"""
    try:
        result = await service.compare_contracts(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing contracts: {str(e)}"
        )


@router.post("/templates", response_model=str, status_code=status.HTTP_201_CREATED)
async def add_template(template: StandardTemplate, 
                      service: ContractAnalysisService = Depends(get_contract_analysis_service)):
    """Add a standard template for comparison"""
    try:
        template_id = await service.add_template(template)
        return template_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding template: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=StandardTemplate, status_code=status.HTTP_200_OK)
async def get_template(template_id: str, 
                      service: ContractAnalysisService = Depends(get_contract_analysis_service)):
    """Retrieve a standard template by ID"""
    try:
        template = await service.get_template(template_id)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {template_id} not found"
            )
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving template: {str(e)}"
        )
