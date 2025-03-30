from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import uuid
import os
from pathlib import Path
from fastapi import HTTPException
from ..models.client_intake_models import (
    IntakeForm, 
    IntakeFormSubmission, 
    AIInterviewSession,
    AIInterviewQuestion,
    AIInterviewResponse,
    CaseAssessment
)
from ..services.openai_service import OpenAIService

class ClientIntakeService:
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.forms_directory = Path("data/intake_forms")
        self.submissions_directory = Path("data/form_submissions")
        self.interviews_directory = Path("data/interview_sessions")
        
        # Create directories if they don't exist
        os.makedirs(self.forms_directory, exist_ok=True)
        os.makedirs(self.submissions_directory, exist_ok=True)
        os.makedirs(self.interviews_directory, exist_ok=True)
        
        # Initialize forms from local storage
        self.forms = self._load_forms()
    
    def _load_forms(self) -> Dict[str, IntakeForm]:
        """Load all intake forms from storage"""
        forms = {}
        if not self.forms_directory.exists():
            return forms
            
        for file_path in self.forms_directory.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    form_data = json.load(f)
                    form = IntakeForm(**form_data)
                    forms[form.id] = form
            except Exception as e:
                print(f"Error loading form {file_path}: {e}")
        
        return forms
    
    def get_forms_by_practice_area(self, practice_area: str) -> List[IntakeForm]:
        """Get all forms for a specific practice area"""
        return [form for form in self.forms.values() if form.practiceArea.lower() == practice_area.lower()]
    
    def get_form_by_id(self, form_id: str) -> IntakeForm:
        """Get a specific form by ID"""
        if form_id not in self.forms:
            raise HTTPException(status_code=404, detail=f"Form with ID {form_id} not found")
        return self.forms[form_id]
    
    def create_form(self, form_data: Dict[str, Any]) -> IntakeForm:
        """Create a new intake form"""
        # Generate a unique ID if not provided
        if 'id' not in form_data:
            form_data['id'] = f"form_{uuid.uuid4().hex}"
        
        # Set timestamps
        now = datetime.now().isoformat()
        form_data['createdAt'] = now
        form_data['updatedAt'] = now
        
        # Create and validate the form
        form = IntakeForm(**form_data)
        
        # Save to storage
        file_path = self.forms_directory / f"{form.id}.json"
        with open(file_path, 'w') as f:
            f.write(form.json())
        
        # Add to in-memory store
        self.forms[form.id] = form
        
        return form
    
    def update_form(self, form_id: str, form_data: Dict[str, Any]) -> IntakeForm:
        """Update an existing form"""
        if form_id not in self.forms:
            raise HTTPException(status_code=404, detail=f"Form with ID {form_id} not found")
        
        # Get existing form and update its fields
        existing_form = self.forms[form_id].dict()
        existing_form.update(form_data)
        
        # Update timestamp
        existing_form['updatedAt'] = datetime.now().isoformat()
        
        # Create and validate the updated form
        updated_form = IntakeForm(**existing_form)
        
        # Save to storage
        file_path = self.forms_directory / f"{updated_form.id}.json"
        with open(file_path, 'w') as f:
            f.write(updated_form.json())
        
        # Update in-memory store
        self.forms[form_id] = updated_form
        
        return updated_form
    
    def delete_form(self, form_id: str) -> Dict[str, Any]:
        """Delete a form"""
        if form_id not in self.forms:
            raise HTTPException(status_code=404, detail=f"Form with ID {form_id} not found")
        
        # Remove from storage
        file_path = self.forms_directory / f"{form_id}.json"
        if file_path.exists():
            os.remove(file_path)
        
        # Remove from in-memory store
        del self.forms[form_id]
        
        return {"status": "success", "message": f"Form {form_id} deleted successfully"}
    
    def submit_form(self, submission_data: Dict[str, Any]) -> IntakeFormSubmission:
        """Submit a completed intake form"""
        form_id = submission_data.get('formId')
        if not form_id or form_id not in self.forms:
            raise HTTPException(status_code=404, detail=f"Form with ID {form_id} not found")
        
        # Create submission ID if not provided
        if 'id' not in submission_data:
            submission_data['id'] = f"submission_{uuid.uuid4().hex}"
        
        # Set submission timestamp
        submission_data['submittedAt'] = datetime.now().isoformat()
        
        # Create and validate submission
        submission = IntakeFormSubmission(**submission_data)
        
        # Save to storage
        file_path = self.submissions_directory / f"{submission.formId}_{submission_data['id']}.json"
        with open(file_path, 'w') as f:
            f.write(submission.json())
        
        return submission
    
    async def generate_case_assessment(self, submission_id: str) -> CaseAssessment:
        """Generate a preliminary case assessment based on form submission"""
        # Find the submission
        submission_path = None
        for file_path in self.submissions_directory.glob(f"*_{submission_id}.json"):
            submission_path = file_path
            break
        
        if not submission_path:
            raise HTTPException(status_code=404, detail=f"Submission with ID {submission_id} not found")
        
        # Load submission data
        with open(submission_path, 'r') as f:
            submission_data = json.load(f)
            submission = IntakeFormSubmission(**submission_data)
        
        # Get the form definition
        form = self.get_form_by_id(submission.formId)
        
        # Prepare context for the AI
        context = {
            "form_title": form.title,
            "practice_area": form.practiceArea,
            "client_data": submission.data
        }
        
        # Generate the assessment using OpenAI
        prompt = f"""As an experienced lawyer, perform a preliminary case assessment based on the following client intake information:

Practice Area: {context['practice_area']}
Form: {context['form_title']}

Client Information:
{json.dumps(context['client_data'], indent=2)}

Provide a structured assessment including:
1. Case strengths
2. Case weaknesses
3. Key legal issues
4. Recommended actions
5. Risk assessment
6. Estimated timeframe (if possible)
7. Estimated costs (if possible)
8. Additional notes

Format your response as a valid JSON object that matches the CaseAssessment model.
"""
        
        # Call OpenAI
        response = await self.openai_service.generate_completion(prompt)
        
        try:
            # Parse the JSON response
            assessment_data = json.loads(response)
            assessment = CaseAssessment(**assessment_data)
            return assessment
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate case assessment: {str(e)}")
    
    async def create_interview_session(self, practice_area: str, case_type: Optional[str] = None) -> AIInterviewSession:
        """Create a new AI interview session"""
        try:
            session_id = f"interview_{uuid.uuid4().hex}"
            
            # Initialize with standard first questions based on practice area
            initial_questions = self._get_initial_questions(practice_area, case_type)
            
            session = AIInterviewSession(
                sessionId=session_id,
                practiceArea=practice_area,
                caseType=case_type,
                questions=initial_questions,
                responses=[]
            )
            
            # Save to storage
            file_path = self.interviews_directory / f"{session_id}.json"
            os.makedirs(self.interviews_directory, exist_ok=True)  # Ensure directory exists
            with open(file_path, 'w') as f:
                f.write(session.json())
            
            return session
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create interview session: {str(e)}")
    
    def _get_initial_questions(self, practice_area: str, case_type: Optional[str] = None) -> List[AIInterviewQuestion]:
        """Get initial questions based on practice area and case type"""
        # Basic questions that apply to most practice areas
        basic_questions = [
            AIInterviewQuestion(
                id=f"q_{uuid.uuid4().hex}",
                question="Could you please describe your legal issue in your own words?",
                intent="Understanding the client's perspective and main concerns"
            ),
            AIInterviewQuestion(
                id=f"q_{uuid.uuid4().hex}",
                question="When did this issue first arise?",
                intent="Establishing timeline and potential limitations issues"
            )
        ]
        
        # Additional questions can be added based on practice area and case type
        # This would be expanded with a more comprehensive question bank
        
        return basic_questions
    
    async def process_interview_response(self, session_id: str, question_id: str, response_text: str) -> AIInterviewResponse:
        """Process a response in an interview session and generate follow-up questions"""
        # Find the session
        session_path = self.interviews_directory / f"{session_id}.json"
        if not session_path.exists():
            raise HTTPException(status_code=404, detail=f"Interview session {session_id} not found")
        
        # Load session data
        with open(session_path, 'r') as f:
            session_data = json.load(f)
            session = AIInterviewSession(**session_data)
        
        # Find the question
        question = None
        for q in session.questions:
            if q.id == question_id:
                question = q
                break
        
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {question_id} not found in session")
        
        # Create response object
        interview_response = AIInterviewResponse(
            questionId=question_id,
            response=response_text
        )
        
        # Get previous context
        context = []
        for i, q in enumerate(session.questions):
            # Find corresponding response if any
            resp = next((r for r in session.responses if r.questionId == q.id), None)
            if resp:
                context.append({
                    "question": q.question,
                    "response": resp.response
                })
        
        # Use AI to analyze the response and generate follow-up questions
        prompt = f"""As an experienced legal interviewer, analyze the following client response in a legal consultation:

Practice Area: {session.practiceArea}
{f'Case Type: {session.caseType}' if session.caseType else ''}

Current Question: {question.question}
Client Response: {response_text}

Previous Context:
{json.dumps(context, indent=2)}

Please:
1. Extract key entities (people, dates, amounts, etc.)
2. Analyze sentiment and identify any emotional concerns
3. Generate 2-3 relevant follow-up questions based on the response

Format your response as JSON that matches the expected response format.
"""
        
        try:
            # Call OpenAI and await the response
            ai_response = await self.openai_service.generate_completion(prompt)
            print(f"DEBUG - AI Response received: {ai_response[:100]}...")
            
            # Clean up the AI response before parsing
            # Sometimes the AI returns JSON in a markdown code block
            cleaned_response = ai_response
            
            # Remove markdown code block formatting if present
            if cleaned_response.startswith('```'):
                # Find the first and last code block markers
                first_marker_end = cleaned_response.find('\n', 3)  # Skip the first 3 chars (```)
                if first_marker_end != -1:
                    # Find the last marker
                    last_marker = cleaned_response.rfind('```')
                    if last_marker > first_marker_end:
                        # Extract content between markers
                        cleaned_response = cleaned_response[first_marker_end+1:last_marker].strip()
                    else:
                        # Just remove the first marker if no closing marker
                        cleaned_response = cleaned_response[first_marker_end+1:].strip()
            
            print(f"Cleaned response for JSON parsing: {cleaned_response[:100]}...")
            
            # Parse the cleaned response as JSON
            analysis = json.loads(cleaned_response)
            
            # Update interview response with AI analysis
            interview_response.sentimentAnalysis = analysis.get("sentimentAnalysis")
            interview_response.extractedEntities = analysis.get("extractedEntities")
            
            # Convert AI-suggested questions to AIInterviewQuestion objects
            next_questions = []
            for q in analysis.get("nextQuestions", []):
                next_question = AIInterviewQuestion(
                    id=f"q_{uuid.uuid4().hex}",
                    question=q["question"],
                    intent=q["intent"],
                    followUpQuestions=q.get("followUpQuestions"),
                    relatedTopics=q.get("relatedTopics")
                )
                next_questions.append(next_question)
            
            interview_response.nextQuestions = next_questions
            
            # Add new questions to the session
            session.questions.extend(next_questions)
            
            # Add response to the session
            session.responses.append(interview_response)
            
            # Update session timestamp
            session.lastUpdatedAt = datetime.now().isoformat()
            
            # Save updated session
            with open(session_path, 'w') as f:
                f.write(session.json())
            
            return interview_response
            
        except json.JSONDecodeError as e:
            # Log the error with more details
            print(f"Error parsing AI response as JSON: {e}")
            print(f"AI response content: {ai_response}")
            raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            # Log any other errors
            print(f"Error processing interview response: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to process interview response: {str(e)}")
    
    async def complete_interview(self, session_id: str) -> Dict[str, Any]:
        """Complete an interview session and generate a case assessment"""
        # Find the session
        session_path = self.interviews_directory / f"{session_id}.json"
        if not session_path.exists():
            raise HTTPException(status_code=404, detail=f"Interview session {session_id} not found")
        
        # Load session data
        with open(session_path, 'r') as f:
            session_data = json.load(f)
            session = AIInterviewSession(**session_data)
        
        # Generate a summary of the interview
        interview_data = []
        for question in session.questions:
            response = next((r for r in session.responses if r.questionId == question.id), None)
            if response:
                interview_data.append({
                    "question": question.question,
                    "response": response.response
                })
        
        prompt = f"""As an experienced legal professional, summarize the following client interview:

Practice Area: {session.practiceArea}
{f'Case Type: {session.caseType}' if session.caseType else ''}

Interview Transcript:
{json.dumps(interview_data, indent=2)}

Please provide:
1. A concise summary of the client's situation
2. A preliminary case assessment including strengths, weaknesses, and key legal issues
3. Recommended next steps

Format your response as a valid JSON object with the following structure:
{{
  "summary": "String summarizing the client's situation",
  "caseAssessment": {{
    "strengths": ["List of case strengths"],
    "weaknesses": ["List of case weaknesses"],
    "legalIssues": ["List of legal issues"],
    "recommendedActions": ["List of recommended actions"],
    "riskAssessment": "Overall risk assessment",
    "estimatedTimeframe": "Estimated timeframe for resolution",
    "estimatedCosts": {{
      "range": "Estimated cost range",
      "factors": ["Factors affecting cost"]
    }},
    "additionalNotes": "Any additional notes"
  }}
}}
"""
        
        try:
            # Call OpenAI and await the response
            ai_response = await self.openai_service.generate_completion(prompt)
            print(f"DEBUG - AI Response received: {ai_response[:100]}...")
            
            # Clean up the AI response before parsing
            # Sometimes the AI returns JSON in a markdown code block
            cleaned_response = ai_response
            
            # Remove markdown code block formatting if present
            if cleaned_response.startswith('```'):
                # Find the first and last code block markers
                first_marker_end = cleaned_response.find('\n', 3)  # Skip the first 3 chars (```)
                if first_marker_end != -1:
                    # Find the last marker
                    last_marker = cleaned_response.rfind('```')
                    if last_marker > first_marker_end:
                        # Extract content between markers
                        cleaned_response = cleaned_response[first_marker_end+1:last_marker].strip()
                    else:
                        # Just remove the first marker if no closing marker
                        cleaned_response = cleaned_response[first_marker_end+1:].strip()
            
            print(f"Cleaned response for JSON parsing: {cleaned_response[:100]}...")
            
            # Parse the cleaned response as JSON
            analysis = json.loads(cleaned_response)
            
            # Update session with summary and assessment
            session.summary = analysis.get("summary")
            session.caseAssessment = CaseAssessment(**analysis.get("caseAssessment"))
            session.isComplete = True
            session.lastUpdatedAt = datetime.now().isoformat()
            
            # Save updated session
            with open(session_path, 'w') as f:
                f.write(session.json())
            
            return {
                "sessionId": session.sessionId,
                "summary": session.summary,
                "caseAssessment": session.caseAssessment
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to complete interview: {str(e)}")
