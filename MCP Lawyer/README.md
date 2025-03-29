# Pathways Law Practice Management

*By Danial Whittal*

A comprehensive Canadian law practice management system that combines AI-powered legal expertise with document automation, deadline tracking, and client management tools. Built with FastAPI, React, and OpenAI integration.

![Pathways Law Practice Management](https://via.placeholder.com/800x400?text=Pathways+Law+Practice+Management)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Server Setup](#server-setup)
  - [Client Setup](#client-setup)
  - [Environment Configuration](#environment-configuration)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Starting the Client](#starting-the-client)
  - [API Documentation](#api-documentation)
- [Core Components](#core-components)
  - [Legal Experts](#legal-experts)
  - [Document Management](#document-management)
  - [Legal Tools](#legal-tools)
  - [Client Intake](#client-intake)
- [Client Interface](#client-interface)
  - [Expert Management](#expert-management)
  - [Legal Assistant](#legal-assistant)
  - [Document Generation](#document-generation)
  - [Deadline Calculator](#deadline-calculator)
- [Canadian Law Features](#canadian-law-features)
  - [Provincial Jurisdictions](#provincial-jurisdictions)
  - [Legal Document Templates](#legal-document-templates)
  - [Limitation Periods](#limitation-periods)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Adding New Features](#adding-new-features)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

Pathways Law Practice Management is a comprehensive solution designed specifically for Canadian law firms. It combines AI-powered legal expertise with practical tools for document automation, deadline tracking, and client management. The system streamlines common legal workflows while providing jurisdiction-specific guidance across various practice areas.

This application enables legal professionals to:

1. Access specialized Canadian legal expertise across multiple practice areas and jurisdictions
2. Generate customized legal documents based on Canadian law with automated templates
3. Calculate important legal deadlines based on provincial rules and limitation periods
4. Streamline client intake with practice-specific forms and validation
5. Analyze legal issues with AI assistance tailored to Canadian legal frameworks
3. Process queries through OpenAI's GPT models with dynamically constructed, contextually relevant prompts
4. Interact with AI roles through a modern React client interface

## Features

### Legal Expertise
- **Specialized Legal Experts**: Access AI-powered legal expertise across various Canadian practice areas
- **Jurisdiction-Specific Guidance**: Get advice tailored to provincial and federal Canadian law
- **Legal Research Assistance**: Search and analyze Canadian legal resources and case law

### Document Management
- **Document Templates**: Access a library of Canadian legal document templates
- **Document Generation**: Create customized legal documents with AI assistance
- **Document Export**: Download documents in markdown format or copy to clipboard

### Legal Tools
- **Deadline Calculator**: Calculate legal deadlines based on Canadian court rules and limitation periods
- **Calendar Integration**: Export deadlines to calendar applications with .ics files
- **Legal Issue Analysis**: Get AI-powered analysis of legal issues under Canadian law
- **Legal Research Tool**: Search legal databases for relevant case law and legislation
- **Citation Formatter**: Format legal citations according to Canadian citation standards
- **Document Comparison**: Compare different versions of legal documents with highlighted differences
- **Legal Fee Calculator**: Estimate legal fees based on matter type, complexity, and service structure
- **Court Filing Assistant**: Generate checklists and instructions for court filings across jurisdictions

### Practice Management
- **Client Intake Forms**: Streamlined client onboarding with practice-specific forms
- **Form Validation**: Ensure all required client information is collected properly
- **Progress Tracking**: Monitor completion status of client intake forms

### Technical Implementation
- **Modern Stack**: Built with React, TypeScript, TailwindCSS, and shadcn/ui components
- **AI Integration**: Seamless integration with OpenAI's GPT-4o-mini model
- **Responsive Design**: Works on desktop and mobile devices with dark/light mode support
- **State Management**: Efficient data handling with React Query for API interactions
- **Enhanced UX**: Contextual tooltips and improved placeholder text for better user guidance

## Architecture

### System Architecture

The MCP Server follows a clean, modular architecture:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  React      │     │  FastAPI    │     │  OpenAI     │
│  Client     │────▶│  Server     │────▶│  API        │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  In-Memory  │
                    │  Database   │
                    └─────────────┘
```

- **Client Layer**: React application for user interaction
- **API Layer**: FastAPI server handling requests and business logic
- **Service Layer**: Core services for role management, memory handling, and AI processing
- **Data Layer**: In-memory storage for roles and memories

### Data Flow

1. User creates roles and interacts with them through the React client
2. Client sends API requests to the FastAPI server
3. Server processes requests, manages roles and memories
4. For query processing, the server:
   - Retrieves the specified role
   - Fetches relevant memories
   - Constructs a context-aware prompt
   - Sends the prompt to OpenAI's API
   - Returns the response to the client

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- OpenAI API key
- Git (for cloning the repository)

### Server Setup

1. Clone the repository:

```bash
git clone https://github.com/Chris-June/MCP-GPT-Builder.git
cd MCP-GPT-Builder
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install server dependencies:

```bash
pip install -r requirements.txt
```

### Client Setup

1. Navigate to the client directory:

```bash
cd client
```

2. Install client dependencies:

```bash
npm install
```

### Environment Configuration

1. Create a `.env` file in the root directory based on the example:

```bash
cp .env.example .env
```

2. Open the `.env` file and configure the following variables:

```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini  # The model to use for AI processing
SERVER_HOST=0.0.0.0  # Host to bind the server to
SERVER_PORT=8000  # Port to run the server on
```

## Usage

### Starting the Server

1. From the root directory, with the virtual environment activated:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at http://localhost:8000.

2. Access the API documentation at http://localhost:8000/docs to explore available endpoints.

### Starting the Client

1. From the client directory, in a separate terminal:

```bash
npm run dev
```

The client will be available at http://localhost:5173.

### API Documentation

The MCP Server provides a comprehensive API for managing roles, memories, and processing queries:

#### Role Management

- `GET /api/v1/roles` - List all roles
- `GET /api/v1/roles/{role_id}` - Get a specific role
- `POST /api/v1/roles` - Create a new role
- `PUT /api/v1/roles/{role_id}` - Update a role
- `DELETE /api/v1/roles/{role_id}` - Delete a role

#### Memory Management

- `GET /api/v1/memories/{role_id}` - Get memories for a role
- `POST /api/v1/memories` - Create a new memory
- `DELETE /api/v1/memories/{role_id}` - Clear all memories for a role

#### Query Processing

- `POST /api/v1/roles/process` - Process a query with role-specific context

## Core Concepts

### Roles

Roles are the foundation of the MCP Server. Each role represents a specialized AI assistant with specific expertise, personality traits, and behavior guidelines.

#### Role Properties

- **id**: Unique identifier for the role
- **name**: Display name for the role
- **description**: Brief description of the role's purpose
- **instructions**: Specific guidelines for how the role should behave
- **domains**: Areas of expertise (e.g., Finance, Marketing, Technical Support)
- **tone**: Communication style (professional, casual, friendly, technical, formal)
- **system_prompt**: Advanced configuration for the AI model
- **is_default**: Whether this is a default role

#### Creating Effective Roles

When creating roles, consider the following best practices:

1. **Be Specific**: Clearly define the role's expertise and limitations
2. **Set Clear Guidelines**: Provide detailed instructions on how the role should respond
3. **Define Tone**: Choose a tone that matches the role's purpose
4. **Craft System Prompts**: Use system prompts to fine-tune behavior

### Memories

Memories provide context for AI roles, allowing them to maintain information across conversations.

#### Memory Properties

- **id**: Unique identifier for the memory
- **role_id**: The role this memory belongs to
- **content**: The actual memory content
- **type**: Type of memory (e.g., conversation, fact, preference)
- **importance**: Importance level (affects retrieval priority)
- **embedding**: Vector representation for semantic search
- **created_at**: Timestamp when the memory was created

### Query Processing

Query processing combines roles, memories, and user input to generate contextually relevant responses.

#### Processing Flow

1. User sends a query for a specific role
2. Server retrieves the role configuration
3. Server fetches relevant memories for context
4. Server constructs a prompt with role instructions, tone, and memories
5. Server sends the prompt to OpenAI's API
6. Server returns the AI-generated response to the client

## Client Interface

### Role Management

The client provides a user-friendly interface for managing AI roles:

#### Role List

The Roles page displays all available roles with options to:
- View role details
- Edit existing roles
- Delete roles
- Create new roles

#### Role Creation

The role creation form allows you to define all aspects of a new AI role:

1. **Basic Information**:
   - Name: A descriptive name for the role
   - Description: Brief summary of the role's purpose

2. **Expertise Configuration**:
   - Domains: Areas of expertise for the role
   - Tone: Communication style

3. **Behavior Guidelines**:
   - Instructions: Specific guidelines for how the role should behave
   - System Prompt: Advanced configuration for the AI model

### Chat Interface

The Chat page provides an interactive interface for conversing with AI roles:

1. **Role Selection**: Choose from available roles
2. **Conversation**: Send messages and receive AI responses
3. **Context Awareness**: The AI maintains context throughout the conversation

## Examples

### Creating a Financial Advisor Role

```json
{
  "id": "financial-advisor",
  "name": "Financial Advisor",
  "description": "Expert in personal finance and investment strategies",
  "instructions": "You are a financial advisor with expertise in retirement planning. Always provide balanced advice considering both short-term and long-term financial goals. Explain concepts in simple terms and avoid financial jargon when possible.",
  "domains": ["Finance", "Investment", "Retirement", "Tax Planning"],
  "tone": "professional",
  "system_prompt": "You are FinanceGPT, an AI assistant specialized in personal finance and investment strategies. You have extensive knowledge of retirement accounts, tax optimization, debt management, and investment vehicles. When providing advice, always consider risk tolerance, time horizon, and tax implications. Format your responses with clear sections and bullet points when appropriate."
}
```

### Creating a Technical Support Role

```json
{
  "id": "tech-support",
  "name": "Technical Support Specialist",
  "description": "Expert in troubleshooting software and hardware issues",
  "instructions": "You are a technical support specialist. Always start by understanding the user's problem before suggesting solutions. Ask clarifying questions if needed. Provide step-by-step instructions that are easy to follow.",
  "domains": ["Software", "Hardware", "Networking", "Troubleshooting"],
  "tone": "friendly",
  "system_prompt": "You are TechGPT, an AI assistant specialized in technical support and troubleshooting. You have extensive knowledge of common software issues, hardware problems, and networking configurations. When helping users, first diagnose the problem by understanding the symptoms, then provide clear, step-by-step solutions. Use numbered lists for instructions and explain technical concepts in simple terms."
}
```

### Sample Conversations

#### Financial Advisor Conversation

**User**: I'm 35 and want to start saving for retirement. What should I do?

**AI**: Great question! Starting to save for retirement at 35 is still plenty of time to build a solid nest egg. Here's a balanced approach to get you started:

**First Steps:**
* **Establish an emergency fund** of 3-6 months of expenses before focusing heavily on retirement
* **Take advantage of employer matching** if your workplace offers a 401(k) match - this is essentially free money

**Retirement Account Options:**
* **401(k)/403(b)**: Try to contribute at least enough to get the full employer match
* **Roth IRA**: Consider opening one if you're eligible - contributions grow tax-free
* **Traditional IRA**: Another option with potential tax advantages now

**Investment Strategy:**
* At 35, you can still have a relatively aggressive portfolio (e.g., 70-80% stocks, 20-30% bonds)
* Consider low-cost index funds for diversification

Would you like me to explain any of these options in more detail?

#### Technical Support Conversation

**User**: My laptop keeps freezing randomly. What could be wrong?

**AI**: I'm sorry to hear about your laptop freezing issues! Let's figure this out together. 

**Possible Causes & Solutions:**

1. **Overheating**
   * Check if your laptop feels hot when it freezes
   * Ensure vents aren't blocked and consider using a cooling pad
   * Clean dust from internal fans (if you're comfortable opening it or get professional help)

2. **Resource-intensive applications**
   * Check Task Manager (Ctrl+Shift+Esc) to see what's using resources
   * Close unnecessary applications and browser tabs

3. **Outdated drivers or software**
   * Update your operating system
   * Update graphics and other device drivers

4. **Insufficient RAM or storage**
   * Check available storage space (aim for at least 10% free)
   * Consider upgrading RAM if your system is consistently using near 100%

Could you tell me a bit more about when the freezing happens? Does it occur during specific activities or at random times?

## Advanced Configuration

### Customizing System Prompts

System prompts are powerful tools for fine-tuning AI behavior. Here are some tips for crafting effective system prompts:

1. **Define Identity**: Clearly state who the AI is and its expertise
2. **Set Boundaries**: Define what the AI should and shouldn't do
3. **Specify Format**: Indicate how responses should be structured
4. **Include Examples**: Provide examples of ideal responses

### Fine-tuning Role Behavior

To fine-tune role behavior:

1. **Adjust Instructions**: Modify the role's instructions to guide behavior
2. **Change Tone**: Select a different tone to alter communication style
3. **Add Memories**: Create memories with important information
4. **Refine Domains**: Update expertise domains to focus the role's knowledge

## Development

### Project Structure

```
/
├── app/                    # Server application
│   ├── models/            # Data models
│   ├── routes/            # API endpoints
│   └── services/          # Business logic
├── client/                # React client
│   ├── src/               # Source code
│   │   ├── components/    # UI components
│   │   ├── lib/           # Utilities
│   │   ├── pages/         # Page components
│   │   └── types/         # TypeScript types
├── .env.example           # Example environment variables
├── requirements.txt       # Python dependencies
└── server.py              # Server entry point
```

### Adding New Features

#### Adding a New API Endpoint

1. Create a new route file in `app/routes/`
2. Define the endpoint and handlers
3. Register the route in `app/main.py`

#### Adding a New Client Feature

1. Create new components in `client/src/components/`
2. Add new pages in `client/src/pages/` if needed
3. Update API client in `client/src/lib/api.ts` if needed

## Troubleshooting

### Common Issues

#### Server Won't Start

- Check if the port is already in use
- Verify that all dependencies are installed
- Ensure the `.env` file is properly configured

#### Client Can't Connect to Server

- Verify the server is running
- Check CORS configuration in the server
- Ensure the API base URL is correct in the client

#### OpenAI API Errors

- Verify your API key is valid
- Check your OpenAI account has sufficient credits
- Ensure the model specified in `.env` is available to your account

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Upcoming Canadian Law Firm Enhancements

The following enhancements are planned for future releases to provide comprehensive support for Canadian law firms:

### Document Automation and Assembly
- **Clause Library**: Searchable database of standard clauses that can be dynamically inserted into documents
- **Precedent Management**: System for saving successful documents as precedents with metadata for easy retrieval
- **Version Control**: Track changes and maintain document history with the ability to revert to previous versions

### Client Relationship Management
- **Client Portal**: Secure client-facing portal for case status, document uploads, and communications
- **Automated Updates**: Scheduled notifications to clients about case progress and deadlines
- **Intake Analytics**: AI analysis of intake forms to identify potential legal issues not explicitly mentioned

### Legal Research Augmentation
- **CanLII Integration**: Connection to Canadian legal databases for real-time case law research
- **Jurisdiction Research**: Enhanced research capabilities focused on provincial differences in law
- **Predictive Case Outcome Analysis**: AI-powered analysis using GPT-4o-mini to predict case outcomes based on similar precedents, jurisdiction-specific factors, and SWOT analysis with confidence scoring

### Compliance and Regulatory Tools
- **AML Compliance**: Automated verification processes for client onboarding
- **Law Society Compliance**: Monitor and ensure compliance with provincial law society requirements
- **Conflict Checking**: Enhanced conflict checking against a comprehensive database

### Billing and Financial Management
- **Time Tracking**: Automated time capture based on document work and client communications
- **Fee Arrangement Calculator**: Tools for fixed fee, contingency, or hybrid billing models
- **Trust Accounting**: Automated checks for trust account compliance with provincial regulations

### Court and Administrative Automation
- **Court Filing**: Direct electronic filing with compatible court systems across Canada
- **Hearing Scheduling**: Calendar integration with court schedules and conflict detection
- **Limitation Alerts**: Proactive notification system for approaching limitation periods

### Canadian-Specific Legal AI
- **Bilingual Processing**: Enhanced support for both English and French legal documents
- **Provincial Variations**: Tools to compare how similar legal issues are treated across provinces
- **Indigenous Law**: Resources and guidance related to Indigenous legal considerations

### Security and Privacy Enhancements
- **Enhanced Client Data Protection**: Additional security measures compliant with Canadian privacy laws
- **Ethical Wall Management**: Digital implementation of information barriers between firm departments
- **Secure Document Sharing**: End-to-end encrypted document sharing with clients and opposing counsel

### Analytics and Business Intelligence
- **Practice Performance Metrics**: Dashboard showing key performance indicators by practice area
- **Case Outcome Analysis**: Historical analysis of case outcomes to inform strategy on new matters
- **Client Satisfaction Tracking**: Automated feedback collection and analysis

## Example API Usage

### Create a Custom Role

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/roles' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "tech-writer",
  "name": "Technical Writer",
  "description": "Specializes in clear, concise technical documentation",
  "instructions": "Create documentation that is accessible to both technical and non-technical audiences",
  "domains": ["technical-writing", "documentation", "tutorials"],
  "tone": "technical",
  "system_prompt": "You are an experienced technical writer with expertise in creating clear, concise documentation for complex systems."
}'
```

### Process a Query

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/roles/process' \
  -H 'Content-Type: application/json' \
  -d '{
  "role_id": "marketing-expert",
  "query": "How can I improve my social media engagement?",
  "custom_instructions": "Focus on B2B strategies"
}'
```

### Store a Memory

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/memories' \
  -H 'Content-Type: application/json' \
  -d '{
  "role_id": "marketing-expert",
  "content": "The user prefers Instagram over TikTok for their business",
  "type": "user",
  "importance": "medium"
}'
```

## Docker Deployment

Build and run the container:

```bash
docker build -t role-specific-mcp .
docker run -p 8000:8000 --env-file .env role-specific-mcp
```

## Future Roadmap

### Core Platform Enhancements
- Vector database integration (ChromaDB, Supabase) for semantic memory retrieval
- Real-time context switching based on triggers
- Multi-modal context support
- Support for LangGraph agents and RAG pipelines
- Enhanced authentication and security features

### Advanced Memory Architecture
- Shared memory collections accessible across multiple AI agents
- Hierarchical memory access control system
- Role-based memory inheritance mechanisms
- Configurable memory sharing permissions
- Cross-role semantic search capabilities
- Memory embedding and similarity scoring
- Memory tagging and categorization system

---

## About

This documentation and software is authored by **IntelliSync Solutions**  
Written by: Chris June  
Last Updated: March 29, 2025

© 2025 Pathways Law. All rights reserved. Owned by Danial Whittal.
