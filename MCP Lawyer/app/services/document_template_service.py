from typing import List, Dict, Any, Optional
from app.services.ai_processor import AIProcessor
from app.services.memory_service import MemoryService
import uuid
from datetime import datetime

class DocumentTemplateService:
    def __init__(self, memory_service: Optional[MemoryService] = None, ai_processor: Optional[AIProcessor] = None):
        self.memory_service = memory_service
        self.ai_processor = ai_processor
        # In-memory store for templates (would be replaced with a database in production)
        self.templates = {}
        # Template categories for organization
        self.categories = [
            "Contract",
            "Litigation",
            "Corporate",
            "Real Estate",
            "Family Law",
            "Estate Planning",
            "Employment",
            "Intellectual Property"
        ]
        # Initialize with some example templates
        self._initialize_example_templates()
    
    def _initialize_example_templates(self):
        """Initialize with some example templates"""
        example_templates = [
            {
                "id": str(uuid.uuid4()),
                "name": "Retainer Agreement",
                "description": "Standard client retainer agreement",
                "category": "Contract",
                "content": "# RETAINER AGREEMENT\n\nTHIS AGREEMENT made on {{agreement_date}}\n\nBETWEEN:\n\n**{{firm_name}}**\n\n(the \"Firm\")\n\nAND:\n\n**{{client_name}}**\n\n(the \"Client\")\n\n## 1. ENGAGEMENT\n\nThe Client hereby retains the Firm to provide legal services in relation to {{matter_description}}.\n\n## 2. FEES AND DISBURSEMENTS\n\nThe Client agrees to pay to the Firm fees for legal services at the rate of {{hourly_rate}} per hour, plus applicable taxes and disbursements.\n\n## 3. RETAINER\n\nThe Client agrees to provide the Firm with a retainer in the amount of {{retainer_amount}} to be held in the Firm's trust account and to be applied to fees, disbursements, and taxes.\n\n## 4. BILLING\n\nThe Firm will bill the Client on a {{billing_frequency}} basis.\n\n## 5. TERMINATION\n\nEither party may terminate this agreement by providing written notice to the other party.\n\n## 6. GOVERNING LAW\n\nThis Agreement shall be governed by the laws of {{jurisdiction}}.\n\nIN WITNESS WHEREOF the parties have executed this Agreement as of the date first above written.\n\n___________________________\n{{firm_name}}\n\n___________________________\n{{client_name}}",
                "variables": [
                    "agreement_date",
                    "firm_name",
                    "client_name",
                    "matter_description",
                    "hourly_rate",
                    "retainer_amount",
                    "billing_frequency",
                    "jurisdiction"
                ],
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Affidavit",
                "description": "General affidavit template",
                "category": "Litigation",
                "content": "# AFFIDAVIT\n\n**PROVINCE OF {{province}}**\n\n**In the matter of {{matter_description}}**\n\nI, {{deponent_name}}, of the City of {{deponent_city}}, in the Province of {{province}}, {{deponent_occupation}}, MAKE OATH AND SAY:\n\n1. {{affidavit_content}}\n\n2. I make this affidavit in support of {{purpose}} and for no other or improper purpose.\n\nSWORN BEFORE ME at the City of\n{{city}}, in the Province of {{province}},\nthis {{day}} day of {{month}}, {{year}}.\n\n___________________________\nA Commissioner for Oaths in and\nfor the Province of {{province}}\n\n___________________________\n{{deponent_name}}",
                "variables": [
                    "province",
                    "matter_description",
                    "deponent_name",
                    "deponent_city",
                    "deponent_occupation",
                    "affidavit_content",
                    "purpose",
                    "city",
                    "day",
                    "month",
                    "year"
                ],
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        for template in example_templates:
            self.templates[template["id"]] = template
    
    async def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all templates or filter by category"""
        if category:
            return [t for t in self.templates.values() if t["category"] == category]
        return list(self.templates.values())
    
    async def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get a specific template by ID"""
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        return self.templates[template_id]
    
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new template"""
        template_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        template = {
            "id": template_id,
            "name": template_data["name"],
            "description": template_data["description"],
            "category": template_data["category"],
            "content": template_data["content"],
            "variables": template_data.get("variables", []),
            "version": 1,
            "created_at": now,
            "updated_at": now
        }
        
        self.templates[template_id] = template
        return template
    
    async def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing template"""
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        
        current_template = self.templates[template_id]
        
        # Create a new version
        updated_template = {
            **current_template,
            "name": template_data.get("name", current_template["name"]),
            "description": template_data.get("description", current_template["description"]),
            "category": template_data.get("category", current_template["category"]),
            "content": template_data.get("content", current_template["content"]),
            "variables": template_data.get("variables", current_template["variables"]),
            "version": current_template["version"] + 1,
            "updated_at": datetime.now().isoformat()
        }
        
        self.templates[template_id] = updated_template
        return updated_template
    
    async def delete_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a template"""
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        
        template = self.templates.pop(template_id)
        return {"success": True, "deleted_template": template}
    
    async def get_categories(self) -> List[str]:
        """Get all template categories"""
        return self.categories
    
    async def generate_document(self, template_id: str, variables: Dict[str, str]) -> Dict[str, Any]:
        """Generate a document from a template with the provided variables"""
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        
        template = self.templates[template_id]
        content = template["content"]
        
        # Simple template variable replacement
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{{{{var_name}}}}}}", var_value)
        
        # If AI processor is available, use it to enhance the document
        enhanced_content = content
        if self.ai_processor:
            prompt = f"""You are a legal document assistant. Please review and enhance the following document:

{content}

Make sure it maintains proper legal language and formatting, but improve readability and clarity where possible.

Enhanced document:"""
            
            response = await self.ai_processor.process_prompt(prompt)
            if response and response.get("content"):
                enhanced_content = response["content"]
        
        return {
            "template_id": template_id,
            "template_name": template["name"],
            "content": enhanced_content,
            "variables_used": variables,
            "generated_at": datetime.now().isoformat()
        }
    
    async def analyze_template(self, template_id: str) -> Dict[str, Any]:
        """Analyze a template for structure, variables, and suggestions"""
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        
        template = self.templates[template_id]
        
        # Basic analysis
        analysis = {
            "template_id": template_id,
            "template_name": template["name"],
            "word_count": len(template["content"].split()),
            "section_count": template["content"].count("##"),
            "variable_count": len(template["variables"]),
            "variables": template["variables"]
        }
        
        # Enhanced analysis with AI processor if available
        if self.ai_processor:
            prompt = f"""You are a legal document analyst. Please analyze this document template:

{template["content"]}

Provide insights on:
1. Structure and organization
2. Clarity and readability
3. Legal completeness
4. Suggestions for improvement
5. Potential risks or issues

Your analysis:"""
            
            response = await self.ai_processor.process_prompt(prompt)
            if response and response.get("content"):
                analysis["ai_analysis"] = response["content"]
        
        return analysis
