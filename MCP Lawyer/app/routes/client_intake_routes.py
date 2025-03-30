from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from typing import List, Dict, Any, Optional
from ..services.client_intake_service import ClientIntakeService
from ..services.openai_service import OpenAIService, get_openai_service
from ..models.client_intake_models import (
    IntakeForm, 
    IntakeFormSubmission, 
    AIInterviewSession,
    AIInterviewResponse,
    CaseAssessment
)

router = APIRouter(prefix="/api/client-intake", tags=["client-intake"])

# Dependency to get the client intake service
async def get_client_intake_service():
    openai_service = await get_openai_service()
    return ClientIntakeService(openai_service)

# Form management endpoints
@router.get("/forms", response_model=List[IntakeForm])
async def get_intake_forms(
    practice_area: Optional[str] = Query(None, description="Filter forms by practice area"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Get all intake forms, optionally filtered by practice area"""
    if practice_area:
        return client_intake_service.get_forms_by_practice_area(practice_area)
    return list(client_intake_service.forms.values())

@router.get("/forms/{form_id}", response_model=IntakeForm)
async def get_intake_form(
    form_id: str = Path(..., description="ID of the form to retrieve"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Get a specific intake form by ID"""
    return client_intake_service.get_form_by_id(form_id)

@router.post("/forms", response_model=IntakeForm, status_code=201)
async def create_intake_form(
    form_data: Dict[str, Any] = Body(..., description="Form definition data"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Create a new intake form"""
    return client_intake_service.create_form(form_data)

@router.put("/forms/{form_id}", response_model=IntakeForm)
async def update_intake_form(
    form_id: str = Path(..., description="ID of the form to update"),
    form_data: Dict[str, Any] = Body(..., description="Updated form data"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Update an existing intake form"""
    return client_intake_service.update_form(form_id, form_data)

@router.delete("/forms/{form_id}", response_model=Dict[str, Any])
async def delete_intake_form(
    form_id: str = Path(..., description="ID of the form to delete"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Delete an intake form"""
    return client_intake_service.delete_form(form_id)

# Form submission endpoints
@router.post("/submissions", response_model=IntakeFormSubmission, status_code=201)
async def submit_intake_form(
    submission_data: Dict[str, Any] = Body(..., description="Form submission data"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Submit a completed intake form"""
    return client_intake_service.submit_form(submission_data)

@router.get("/submissions/{submission_id}/assessment", response_model=CaseAssessment)
async def get_case_assessment(
    submission_id: str = Path(..., description="ID of the form submission"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Generate a preliminary case assessment based on a form submission"""
    return await client_intake_service.generate_case_assessment(submission_id)

# AI Interview endpoints
@router.post("/interviews", response_model=AIInterviewSession, status_code=201)
async def create_interview_session(
    practice_area: str = Body(..., description="Practice area for this interview"),
    case_type: Optional[str] = Body(None, description="Type of case"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Create a new AI-powered interview session"""
    return client_intake_service.create_interview_session(practice_area, case_type)

@router.post("/interviews/{session_id}/responses", response_model=AIInterviewResponse)
async def process_interview_response(
    session_id: str = Path(..., description="ID of the interview session"),
    question_id: str = Body(..., description="ID of the question being answered"),
    response_text: str = Body(..., description="Client's response to the question"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Process a response in an interview session and generate follow-up questions"""
    return await client_intake_service.process_interview_response(session_id, question_id, response_text)

@router.post("/interviews/{session_id}/complete", response_model=Dict[str, Any])
async def complete_interview_session(
    session_id: str = Path(..., description="ID of the interview session to complete"),
    client_intake_service: ClientIntakeService = Depends(get_client_intake_service)
):
    """Complete an interview session and generate a case assessment"""
    return await client_intake_service.complete_interview(session_id)
