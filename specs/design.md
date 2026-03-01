# System Design: Prachar.ai - The AI Creative Director

## Document Metadata

**Project:** Prachar.ai - Autonomous AI Creative Director  
**Hackathon:** AWS "AI for Bharat" - Student Track  
**Track:** Media, Content & Creativity  
**Development Methodology:** Kiro Spec-Driven Development  
**Version:** 2.0 (with Cognito Authentication)  
**Last Updated:** 2026-02-14

## Kiro Spec-Driven Development

This design document is part of Kiro's structured development methodology:

**Specification Artifacts:**
1. ✅ `requirements.md` - Functional requirements with acceptance criteria
2. ✅ `design.md` - This document - System architecture and component design
3. ✅ `COGNITO_AUTHENTICATION.md` - Authentication implementation guide
4. ✅ `HACKATHON_CRITERIA_REVIEW.md` - Hackathon alignment verification

**Development Process:**
1. **Requirements Phase**: Define user stories and acceptance criteria
2. **Design Phase**: Architect system components and data flows
3. **Implementation Phase**: Code against specifications
4. **Testing Phase**: Validate against acceptance criteria
5. **Documentation Phase**: Maintain living documentation

**Quality Assurance:**
- All requirements mapped to design components
- All design components mapped to implementation files
- All acceptance criteria mapped to test cases
- Complete traceability from requirement to code

## 1. Overview

Prachar.ai is an autonomous AI Creative Director for Indian students and creators, built using serverless AWS architecture and agentic AI workflows. The system uses the Strands SDK to orchestrate a multi-step reasoning agent that autonomously plans campaigns, retrieves brand context via RAG, generates Hinglish copy using Claude 3.5 Sonnet, and creates posters using Titan Image Generator—all while enforcing responsible AI guardrails.

The core innovation is the **agentic workflow**: users provide a high-level goal, and the Creative Director Agent autonomously decomposes it into tasks, retrieves brand context, executes generation tools, and validates outputs—without requiring step-by-step user guidance.

## 2. Architecture Style

**Serverless Event-Driven Agentic Architecture** using AWS Lambda, Bedrock, and Strands SDK.

**Key Architectural Principles:**
- **Agentic Autonomy**: Agent reasons about goals and autonomously plans execution steps
- **RAG-First Generation**: All content generation is grounded in retrieved brand guidelines
- **Serverless Execution**: Zero infrastructure management, pay-per-use pricing
- **Responsible AI**: Guardrails applied at every generation step
- **Stateless Functions**: Lambda functions are stateless; state stored in DynamoDB

## 3. Tech Stack (Strict Constraints)

### Backend
- **Orchestration**: Strands SDK (Python) for agentic workflow management
- **Compute**: AWS Lambda (Python 3.11 runtime)
- **AI Reasoning**: Amazon Bedrock - `anthropic.claude-3-5-sonnet-20240620-v1:0`
- **AI Vision**: Amazon Bedrock - `amazon.titan-image-generator-v1`
- **RAG**: Amazon Bedrock Knowledge Bases (OpenSearch Serverless backend)
- **Guardrails**: Amazon Bedrock Guardrails (hate speech, PII filtering)
- **Database**: Amazon DynamoDB (campaign storage)
- **Storage**: Amazon S3 (generated images, brand PDFs)
- **Authentication**: Amazon Cognito User Pools (merchant sign-ups, JWT-based authorization)

### Frontend
- **Framework**: Next.js 14 (React) with App Router
- **Styling**: Tailwind CSS
- **Hosting**: AWS Amplify
- **API**: REST API via API Gateway + Lambda

### Infrastructure
- **IaC**: AWS CDK (Python) or CloudFormation
- **Monitoring**: CloudWatch Logs and Metrics
- **CI/CD**: AWS Amplify (frontend), Lambda deployment via CDK

## 4. AI Model Specifics

### Claude 3.5 Sonnet (Text Generation)
- **Model ID**: `anthropic.claude-3-5-sonnet-20240620-v1:0`
- **Use Cases**: 
  - Campaign planning and reasoning
  - Hinglish copywriting
  - Brand guideline interpretation
- **Why**: Best-in-class reasoning, excellent with Indian languages and cultural nuance
- **Configuration**:
  - Max tokens: 1024
  - Temperature: 0.7 (creative but controlled)
  - Top-p: 0.9

### Titan Image Generator v1 (Visual Generation)
- **Model ID**: `amazon.titan-image-generator-v1`
- **Use Cases**:
  - Campaign poster creation
  - Brand-aligned visual assets
- **Why**: Native AWS integration, good text rendering on images
- **Configuration**:
  - Image size: 1024x1024
  - Quality: premium
  - Negative prompts: "blurry, low quality, distorted text"

### Titan Embeddings (RAG)
- **Model ID**: `amazon.titan-embed-text-v1`
- **Use Cases**:
  - Embedding brand guideline PDFs
  - Semantic search for relevant brand context
- **Why**: Optimized for Bedrock Knowledge Bases

## 5. Agentic Workflow Architecture

### 5.1 Strands Agent Structure

```
Creative_Director_Agent (Supervisor)
├── Reasoning Loop (Claude 3.5 Sonnet)
│   ├── Analyze user goal
│   ├── Retrieve brand context (RAG)
│   └── Generate campaign plan
├── Tool: generate_copy
│   ├── Input: campaign_plan, brand_context
│   ├── Model: Claude 3.5 Sonnet
│   ├── Guardrails: Applied
│   └── Output: 3 Hinglish captions
├── Tool: generate_image
│   ├── Input: selected_caption, brand_colors
│   ├── Model: Titan Image Generator v1
│   └── Output: S3 URL
└── Validation Loop
    ├── Check guardrail compliance
    ├── Verify brand alignment
    └── Return final campaign
```

### 5.2 Execution Flow

1. **User Input**: User submits `campaign_goal` (e.g., "Hype my college fest")
2. **Agent Initialization**: Lambda invokes `CreativeDirector` agent with Strands SDK
3. **Reasoning Phase**:
   - Agent uses Claude to analyze goal
   - Agent queries Bedrock Knowledge Base for brand guidelines
   - Agent generates structured `Campaign_Plan` (hook, offer, CTA)
4. **Execution Phase**:
   - Agent calls `generate_copy` tool with plan + brand context
   - Claude generates 3 Hinglish caption variations
   - Guardrails filter outputs
5. **Visual Phase**:
   - Agent calls `generate_image` tool with selected caption
   - Titan generates poster with brand colors
   - Image uploaded to S3, URL returned
6. **Storage Phase**:
   - Agent stores campaign in DynamoDB
   - Returns final result to user

## 6. Component Design

### 6.1 Creative Director Agent (Strands SDK)

**File**: `backend/agent.py`

**Responsibilities**:
- Orchestrate multi-step campaign generation workflow
- Reason about user goals and plan execution
- Call tools autonomously based on plan
- Validate outputs against brand guidelines

**Strands Configuration**:
```python
from strands import Agent, Tool

agent = Agent(
    name="CreativeDirector",
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    instructions="""You are Prachar.ai, an expert Indian marketing creative director.
    Your job is to autonomously plan and execute social media campaigns for Indian students.
    Always retrieve brand guidelines before generating content.
    Generate copy in Hinglish (Hindi-English mix) with cultural relevance.""",
    tools=[generate_copy_tool, generate_image_tool],
    knowledge_base_id="<BEDROCK_KB_ID>"
)
```

**Key Methods**:
- `plan_campaign(goal: str) -> CampaignPlan`
- `execute_plan(plan: CampaignPlan) -> Campaign`
- `validate_output(campaign: Campaign) -> bool`

### 6.2 RAG Integration (Bedrock Knowledge Base)

**Responsibilities**:
- Store user-uploaded brand guideline PDFs
- Embed documents using Titan Embeddings
- Perform semantic search during generation
- Return top-k relevant chunks to agent

**Architecture**:
```
User uploads PDF → S3 Bucket → Bedrock KB ingestion
                                    ↓
                            OpenSearch Serverless (vectors)
                                    ↓
Agent query → Bedrock KB API → Semantic search → Top 3 chunks
```

**API Integration**:
```python
import boto3

bedrock_agent = boto3.client('bedrock-agent-runtime')

def retrieve_brand_context(query: str, kb_id: str) -> list[str]:
    response = bedrock_agent.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={'text': query},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 3
            }
        }
    )
    return [r['content']['text'] for r in response['retrievalResults']]
```

### 6.3 Content Generation Tool

**Tool Name**: `generate_copy`

**Inputs**:
- `campaign_plan`: Structured plan with hook, offer, CTA
- `brand_context`: Retrieved brand guidelines (RAG)
- `language`: Target language (default: "hinglish")

**Process**:
1. Construct prompt with plan + brand context
2. Call Bedrock Claude with guardrails enabled
3. Parse response to extract 3 caption variations
4. Return captions as structured JSON

**Implementation**:
```python
def generate_copy(campaign_plan: dict, brand_context: str) -> list[str]:
    prompt = f"""You are Prachar.ai. Generate 3 Hinglish social media captions.
    
    Campaign Plan:
    - Hook: {campaign_plan['hook']}
    - Offer: {campaign_plan['offer']}
    - CTA: {campaign_plan['cta']}
    
    Brand Guidelines:
    {brand_context}
    
    Requirements:
    - Mix Hindi and English naturally
    - Use emojis suitable for Indian youth
    - Keep each caption under 280 characters
    - Make it energetic and culturally relevant
    
    Output format: Return exactly 3 captions, numbered 1-3."""
    
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": prompt}]
        }),
        guardrailIdentifier="<GUARDRAIL_ID>",
        guardrailVersion="DRAFT"
    )
    
    result = json.loads(response['body'].read())
    return parse_captions(result['content'][0]['text'])
```

### 6.4 Visual Generation Tool

**Tool Name**: `generate_image`

**Inputs**:
- `caption`: Selected caption text
- `brand_colors`: Hex color codes from brand guidelines
- `style`: Visual style (default: "modern poster")

**Process**:
1. Construct image prompt with caption + brand colors
2. Call Bedrock Titan Image Generator
3. Decode base64 image response
4. Upload to S3 with public-read ACL
5. Return S3 URL

**Implementation**:
```python
def generate_image(caption: str, brand_colors: list[str]) -> str:
    prompt = f"""Create a vibrant social media poster for Indian audience.
    
    Text to include: "{caption}"
    Brand colors: {', '.join(brand_colors)}
    Style: Modern, energetic, youth-focused
    
    Requirements:
    - Use specified brand colors prominently
    - Make text readable and bold
    - Include subtle Indian cultural elements
    - High quality, professional design"""
    
    response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-image-generator-v1",
        body=json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                "negativeText": "blurry, low quality, distorted text"
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "premium",
                "height": 1024,
                "width": 1024,
                "cfgScale": 8.0
            }
        })
    )
    
    result = json.loads(response['body'].read())
    image_data = base64.b64decode(result['images'][0])
    
    # Upload to S3
    s3_key = f"campaigns/{uuid.uuid4()}.png"
    s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=image_data)
    
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
```

### 6.5 Guardrails Integration

**Configuration**:
```python
# Guardrail policies
guardrail_config = {
    "name": "PracharAIGuardrail",
    "contentPolicyConfig": {
        "filtersConfig": [
            {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "VIOLENCE", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"},
            {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"}
        ]
    },
    "sensitiveInformationPolicyConfig": {
        "piiEntitiesConfig": [
            {"type": "EMAIL", "action": "BLOCK"},
            {"type": "PHONE", "action": "BLOCK"},
            {"type": "NAME", "action": "ANONYMIZE"}
        ]
    }
}
```

**Application**:
- Applied to all Claude invocations via `guardrailIdentifier` parameter
- Violations logged to CloudWatch
- Blocked outputs trigger automatic regeneration with safer prompts

## 7. Data Models

### 7.1 Campaign (DynamoDB)

```python
{
    "campaign_id": "uuid",
    "user_id": "cognito_user_id",
    "goal": "Hype my college fest",
    "plan": {
        "hook": "Festival season is here!",
        "offer": "Early bird tickets at 50% off",
        "cta": "Register now at link.com"
    },
    "captions": [
        "Caption 1 in Hinglish...",
        "Caption 2 in Hinglish...",
        "Caption 3 in Hinglish..."
    ],
    "selected_caption": "Caption 1 in Hinglish...",
    "image_url": "https://s3.amazonaws.com/...",
    "brand_context": "Retrieved brand guidelines...",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "guardrail_logs": [
        {"step": "copy_generation", "action": "ALLOWED", "confidence": 0.95}
    ]
}
```

### 7.2 Brand Profile (DynamoDB)

```python
{
    "user_id": "cognito_user_id",
    "brand_name": "TechFest IIT Delhi",
    "brand_colors": ["#FF5733", "#3498DB"],
    "tone": "energetic, youthful, tech-savvy",
    "guidelines_s3_key": "brands/user123/guidelines.pdf",
    "kb_ingestion_status": "completed",
    "created_at": "2024-01-10T08:00:00Z"
}
```

### 7.3 Audit Log (DynamoDB)

```python
{
    "log_id": "uuid",
    "user_id": "cognito_user_id",
    "campaign_id": "uuid",
    "event_type": "guardrail_violation",
    "details": {
        "violation_type": "PII_DETECTED",
        "blocked_content": "[REDACTED]",
        "action_taken": "regenerate"
    },
    "timestamp": "2024-01-15T10:32:15Z"
}
```

## 8. Authentication & Authorization

### 8.1 Amazon Cognito User Pool

**Purpose**: Secure merchant sign-ups and authentication for Prachar.ai platform

**Configuration**:
```json
{
    "UserPoolName": "prachar-ai-merchants",
    "Policies": {
        "PasswordPolicy": {
            "MinimumLength": 8,
            "RequireUppercase": true,
            "RequireLowercase": true,
            "RequireNumbers": true,
            "RequireSymbols": true
        }
    },
    "AutoVerifiedAttributes": ["email"],
    "MfaConfiguration": "OPTIONAL",
    "Schema": [
        {
            "Name": "email",
            "AttributeDataType": "String",
            "Required": true,
            "Mutable": false
        },
        {
            "Name": "brand_name",
            "AttributeDataType": "String",
            "Required": false,
            "Mutable": true
        },
        {
            "Name": "organization",
            "AttributeDataType": "String",
            "Required": false,
            "Mutable": true
        }
    ]
}
```

**User Attributes**:
- `sub`: Unique user identifier (UUID)
- `email`: Merchant email (verified)
- `brand_name`: Merchant's brand/organization name
- `organization`: Organization type (e.g., "College Club", "Startup", "Creator")
- `email_verified`: Boolean flag for email verification status

### 8.2 JWT-Based Authorization Flow

**Authentication Flow**:

```
1. User Sign-Up/Sign-In
   ↓
Frontend (Next.js) → Cognito User Pool
   ↓
Cognito returns JWT tokens:
   - ID Token (user identity)
   - Access Token (API authorization)
   - Refresh Token (token renewal)
   ↓
2. API Request
   ↓
Frontend → API Gateway (with Authorization header)
   ↓
API Gateway validates JWT with Cognito
   ↓
3. Lambda Invocation
   ↓
Lambda receives validated user context
   ↓
Lambda extracts user_id from JWT claims
   ↓
4. Bedrock API Call
   ↓
Lambda invokes Bedrock with user_id for audit trail
```

**JWT Token Structure**:

**ID Token Claims**:
```json
{
    "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "merchant@example.com",
    "email_verified": true,
    "cognito:username": "merchant123",
    "custom:brand_name": "TechFest KIIT",
    "custom:organization": "College Club",
    "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_XXXXX",
    "aud": "client_id_here",
    "token_use": "id",
    "auth_time": 1705320000,
    "exp": 1705323600,
    "iat": 1705320000
}
```

**Access Token Claims**:
```json
{
    "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "cognito:groups": ["merchants"],
    "token_use": "access",
    "scope": "aws.cognito.signin.user.admin",
    "auth_time": 1705320000,
    "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_XXXXX",
    "exp": 1705323600,
    "iat": 1705320000,
    "client_id": "client_id_here",
    "username": "merchant123"
}
```

### 8.3 API Gateway Authorizer

**Configuration**:
```python
# API Gateway Cognito Authorizer
authorizer_config = {
    "Name": "CognitoAuthorizer",
    "Type": "COGNITO_USER_POOLS",
    "ProviderARNs": [
        "arn:aws:cognito-idp:us-east-1:ACCOUNT_ID:userpool/us-east-1_XXXXX"
    ],
    "IdentitySource": "method.request.header.Authorization",
    "AuthorizerResultTtlInSeconds": 300
}
```

**Request Flow**:
```
Client Request:
GET /api/campaigns
Headers:
  Authorization: Bearer <JWT_ACCESS_TOKEN>

↓

API Gateway:
1. Extracts JWT from Authorization header
2. Validates JWT signature with Cognito public keys
3. Checks token expiration
4. Verifies token_use = "access"
5. Extracts user context (sub, username, groups)

↓

Lambda Event Context:
{
    "requestContext": {
        "authorizer": {
            "claims": {
                "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "cognito:username": "merchant123",
                "email": "merchant@example.com"
            }
        }
    }
}
```

### 8.4 Securing Bedrock API Calls

**Lambda Authorization Logic**:

```python
import boto3
import json
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Secure Lambda handler with Cognito JWT validation
    """
    
    # Extract user identity from Cognito JWT claims
    try:
        claims = event['requestContext']['authorizer']['claims']
        user_id = claims['sub']  # Cognito user UUID
        user_email = claims.get('email', 'unknown')
        username = claims.get('cognito:username', 'unknown')
    except KeyError:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Unauthorized: Missing authentication'})
        }
    
    # Parse request body
    body = json.loads(event.get('body', '{}'))
    campaign_goal = body.get('goal')
    
    if not campaign_goal:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required field: goal'})
        }
    
    # Initialize Bedrock client with user context
    bedrock_runtime = boto3.client('bedrock-runtime')
    
    # Log API call with user identity for audit trail
    print(f"[AUDIT] User {user_id} ({user_email}) initiating campaign generation")
    print(f"[AUDIT] Goal: {campaign_goal}")
    
    try:
        # Call Bedrock with user-scoped context
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": f"Generate campaign for: {campaign_goal}"
                }],
                # Include user context in metadata for audit
                "metadata": {
                    "user_id": user_id,
                    "username": username
                }
            }),
            guardrailIdentifier=os.getenv('GUARDRAIL_ID'),
            guardrailVersion="DRAFT"
        )
        
        # Log successful Bedrock invocation
        print(f"[AUDIT] Bedrock invocation successful for user {user_id}")
        
        # Store campaign with user_id for data isolation
        campaign_record = {
            'campaign_id': str(uuid.uuid4()),
            'user_id': user_id,  # Ensures data belongs to authenticated user
            'user_email': user_email,
            'goal': campaign_goal,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save to DynamoDB with user_id as partition key
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))
        table.put_item(Item=campaign_record)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(campaign_record)
        }
        
    except Exception as e:
        # Log error with user context
        print(f"[ERROR] Bedrock invocation failed for user {user_id}: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Campaign generation failed',
                'details': str(e)
            })
        }
```

**Security Benefits**:

1. **User Identity Verification**: Every Bedrock API call is tied to a verified Cognito user
2. **Audit Trail**: All AI-generated content is traceable to specific merchants
3. **Data Isolation**: Campaigns are stored with `user_id` ensuring users only access their own data
4. **Rate Limiting**: Cognito user identity enables per-user rate limiting
5. **Cost Attribution**: Track Bedrock usage costs per merchant for billing
6. **Compliance**: Meet data privacy requirements by associating all AI operations with authenticated users

### 8.5 Frontend Integration (Next.js)

**AWS Amplify Auth Configuration**:

```typescript
// prachar-ai/src/lib/auth.ts
import { Amplify } from 'aws-amplify';

Amplify.configure({
    Auth: {
        Cognito: {
            userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID!,
            userPoolClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID!,
            identityPoolId: process.env.NEXT_PUBLIC_COGNITO_IDENTITY_POOL_ID,
            loginWith: {
                email: true
            },
            signUpVerificationMethod: 'code',
            userAttributes: {
                email: {
                    required: true
                },
                'custom:brand_name': {
                    required: false
                }
            },
            passwordFormat: {
                minLength: 8,
                requireLowercase: true,
                requireUppercase: true,
                requireNumbers: true,
                requireSpecialCharacters: true
            }
        }
    }
});
```

**Sign-Up Flow**:

```typescript
// prachar-ai/src/components/SignUp.tsx
import { signUp, confirmSignUp } from 'aws-amplify/auth';

async function handleSignUp(email: string, password: string, brandName: string) {
    try {
        const { userId } = await signUp({
            username: email,
            password,
            options: {
                userAttributes: {
                    email,
                    'custom:brand_name': brandName
                },
                autoSignIn: true
            }
        });
        
        console.log('Sign up successful:', userId);
        // Redirect to email verification page
        
    } catch (error) {
        console.error('Sign up error:', error);
    }
}

async function handleConfirmSignUp(email: string, code: string) {
    try {
        await confirmSignUp({
            username: email,
            confirmationCode: code
        });
        
        console.log('Email verified successfully');
        // Redirect to dashboard
        
    } catch (error) {
        console.error('Verification error:', error);
    }
}
```

**API Request with JWT**:

```typescript
// prachar-ai/src/lib/api.ts
import { fetchAuthSession } from 'aws-amplify/auth';

async function generateCampaign(goal: string) {
    try {
        // Get current user's JWT tokens
        const session = await fetchAuthSession();
        const accessToken = session.tokens?.accessToken?.toString();
        
        if (!accessToken) {
            throw new Error('User not authenticated');
        }
        
        // Make API request with Authorization header
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`  // JWT token
            },
            body: JSON.stringify({ goal })
        });
        
        if (!response.ok) {
            throw new Error('Campaign generation failed');
        }
        
        return await response.json();
        
    } catch (error) {
        console.error('API error:', error);
        throw error;
    }
}
```

### 8.6 DynamoDB Data Model with User Isolation

**Updated Campaign Schema**:

```python
{
    "campaign_id": "uuid",  # Sort key
    "user_id": "cognito_sub",  # Partition key (ensures data isolation)
    "user_email": "merchant@example.com",
    "goal": "Hype my college fest",
    "plan": {
        "hook": "Festival season is here!",
        "offer": "Early bird tickets at 50% off",
        "cta": "Register now"
    },
    "captions": ["Caption 1...", "Caption 2...", "Caption 3..."],
    "image_url": "https://s3.amazonaws.com/...",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "bedrock_invocation_id": "uuid",  # For audit trail
    "guardrail_logs": [
        {
            "step": "copy_generation",
            "action": "ALLOWED",
            "user_id": "cognito_sub"
        }
    ]
}
```

**Query Pattern**:
```python
# Get all campaigns for authenticated user
response = table.query(
    KeyConditionExpression=Key('user_id').eq(user_id)
)
```

### 8.7 IAM Permissions for Cognito Integration

**Updated Lambda Execution Role**:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:Retrieve",
                "bedrock:ApplyGuardrail"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "us-east-1"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "cognito-idp:GetUser",
                "cognito-idp:ListUsers"
            ],
            "Resource": "arn:aws:cognito-idp:us-east-1:ACCOUNT_ID:userpool/us-east-1_XXXXX"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::prachar-ai-assets/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/prachar-campaigns"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

## 9. API Design

### 9.1 Generate Campaign (Protected)

**Endpoint**: `POST /api/campaigns/generate`

**Authentication**: Required (Cognito JWT)

**Headers**:
```
Authorization: Bearer <JWT_ACCESS_TOKEN>
Content-Type: application/json
```

**Request**:
```json
{
    "goal": "Hype my college fest"
}
```

**Response**:
```json
{
    "campaign_id": "uuid",
    "user_id": "cognito_sub",
    "plan": {
        "hook": "Festival season is here!",
        "offer": "Early bird tickets at 50% off",
        "cta": "Register now"
    },
    "captions": ["Caption 1...", "Caption 2...", "Caption 3..."],
    "image_url": "https://s3.amazonaws.com/...",
    "status": "completed"
}
```

**Error Responses**:
```json
// 401 Unauthorized
{
    "error": "Unauthorized: Missing or invalid authentication token"
}

// 403 Forbidden
{
    "error": "Forbidden: Token expired or user not verified"
}
```

### 9.2 Upload Brand Guidelines (Protected)

**Endpoint**: `POST /api/brands/upload`

**Authentication**: Required (Cognito JWT)

**Headers**:
```
Authorization: Bearer <JWT_ACCESS_TOKEN>
Content-Type: multipart/form-data
```

**Request**: Multipart form data with PDF file

**Response**:
```json
{
    "brand_id": "uuid",
    "user_id": "cognito_sub",
    "kb_ingestion_status": "processing",
    "estimated_completion": "2024-01-15T10:35:00Z"
}
```

### 9.3 Get Campaign History (Protected)

**Endpoint**: `GET /api/campaigns`

**Authentication**: Required (Cognito JWT)

**Headers**:
```
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

**Query Parameters**: None (user_id extracted from JWT)

**Response**:
```json
{
    "campaigns": [
        {
            "campaign_id": "uuid",
            "goal": "Hype my college fest",
            "image_url": "https://s3.amazonaws.com/...",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "user_id": "cognito_sub"
}
```

### 9.4 User Profile (Protected)

**Endpoint**: `GET /api/user/profile`

**Authentication**: Required (Cognito JWT)

**Headers**:
```
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

**Response**:
```json
{
    "user_id": "cognito_sub",
    "email": "merchant@example.com",
    "email_verified": true,
    "brand_name": "TechFest KIIT",
    "organization": "College Club",
    "created_at": "2024-01-10T08:00:00Z",
    "total_campaigns": 15,
    "subscription_tier": "free"
}
```

## 10. Deployment Architecture

```
User (Browser)
    ↓
AWS Amplify (Next.js Frontend)
    ↓
Amazon Cognito User Pool (Authentication)
    ↓ (JWT Token)
API Gateway (REST API + Cognito Authorizer)
    ↓ (Validated User Context)
Lambda (agent.py with Strands SDK)
    ↓
├── Amazon Bedrock (Claude + Titan) [Secured with user_id]
├── Bedrock Knowledge Base (RAG)
├── Bedrock Guardrails
├── DynamoDB (campaigns, brands, logs) [Partitioned by user_id]
└── S3 (images, PDFs)
```

### Lambda Configuration
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 5 minutes
- **Environment Variables**:
  - `COGNITO_USER_POOL_ID`: Cognito User Pool ID
  - `BEDROCK_KB_ID`: Knowledge Base ID
  - `GUARDRAIL_ID`: Guardrail ID
  - `S3_BUCKET`: Image storage bucket
  - `DYNAMODB_TABLE`: Campaign table name

### IAM Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:Retrieve",
                "bedrock:ApplyGuardrail"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cognito-idp:GetUser",
                "cognito-idp:ListUsers"
            ],
            "Resource": "arn:aws:cognito-idp:*:*:userpool/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::prachar-ai-assets/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/prachar-campaigns"
        }
    ]
}
```

## 11. Error Handling

### 11.1 Bedrock Model Errors
- **Scenario**: Claude or Titan returns error
- **Handling**: Retry with exponential backoff (3 attempts), fallback to cached templates

### 11.2 Guardrail Violations
- **Scenario**: Content blocked by guardrails
- **Handling**: Regenerate with safer prompts, log violation, notify user if persistent

### 11.3 RAG Retrieval Failures
- **Scenario**: Knowledge Base unavailable
- **Handling**: Use default brand guidelines, degrade gracefully

### 11.4 Lambda Timeout
- **Scenario**: Agent execution exceeds 5 minutes
- **Handling**: Return partial results, allow user to retry

### 11.5 Authentication Errors
- **Scenario**: Invalid or expired JWT token
- **Handling**: Return 401 Unauthorized, prompt user to re-authenticate

### 11.6 Authorization Errors
- **Scenario**: User attempts to access another user's campaigns
- **Handling**: Return 403 Forbidden, log security event

## 12. Testing Strategy

### 12.1 Unit Tests
- Test individual tools (`generate_copy`, `generate_image`)
- Mock Bedrock API responses
- Validate guardrail integration
- Test JWT token validation logic
- Test user_id extraction from Cognito claims

### 12.2 Integration Tests
- Test end-to-end campaign generation with real Bedrock calls
- Validate RAG retrieval accuracy
- Test Lambda deployment
- Test Cognito authentication flow
- Verify API Gateway authorizer configuration

### 12.3 Security Tests
- Test expired JWT token rejection
- Test invalid JWT signature rejection
- Verify user data isolation (user A cannot access user B's campaigns)
- Test rate limiting per user
- Validate audit trail completeness

### 12.4 Property-Based Tests
- **Property 1**: All generated captions must be in Hinglish format
- **Property 2**: All images must include brand colors
- **Property 3**: Guardrails must block PII in 100% of test cases
- **Property 4**: All Bedrock API calls must have valid user_id in audit logs
- **Property 5**: All DynamoDB queries must filter by authenticated user_id

## 13. Success Metrics

### Hackathon Judging Criteria
- **Creativity**: Autonomous agentic workflow, Hinglish generation
- **Technical Excellence**: Strands SDK orchestration, RAG integration, guardrails, Cognito authentication
- **Security**: JWT-based authorization, user data isolation, audit trails
- **Usability**: One-click campaign generation, mobile-responsive UI, secure sign-up flow
- **AWS Service Usage**: Bedrock (Claude + Titan), Knowledge Bases, Guardrails, Lambda, DynamoDB, Cognito

### Performance Targets
- Campaign generation: < 60 seconds
- Guardrail compliance: 100%
- Authentication latency: < 500ms
- User satisfaction: > 4.5/5 stars

### Security Targets
- JWT validation success rate: 100%
- Unauthorized access attempts blocked: 100%
- Audit trail completeness: 100% of Bedrock calls logged with user_id
- Data isolation: Zero cross-user data leaks
