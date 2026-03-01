"""
AWS Lambda Handler for Prachar.ai - Enterprise-Grade Campaign Generation

This module serves as the entry point for AWS Lambda, handling API Gateway requests
and orchestrating the autonomous AI Creative Director workflow.

Phase 1: Infrastructure Skeleton
- AWS service initialization (Bedrock, DynamoDB, S3)
- API Gateway integration with CORS support
- CloudWatch logging configuration
- Error handling and request validation

Phase 2: Bedrock AI Tools
- generate_copy_impl: Claude 3.5 Sonnet for Hinglish copywriting
- generate_image_impl: Titan Image Generator for campaign posters

Author: Team NEONX
Project: Prachar.ai - AI for Bharat Hackathon
"""

import json
import os
import logging
import base64
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from strands import Agent, Tool


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ============================================================================
# GLOBAL INITIALIZATION (Cold-Start Optimization)
# ============================================================================

# Initialize AWS clients outside handler for connection reuse across invocations
try:
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    logger.info("AWS clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AWS clients: {str(e)}")
    raise


# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'prachar-ai-campaigns')
S3_BUCKET = os.environ.get('S3_BUCKET', 'prachar-ai-assets')
GUARDRAIL_ID = os.environ.get('GUARDRAIL_ID', '')
GUARDRAIL_VERSION = os.environ.get('GUARDRAIL_VERSION', 'DRAFT')

logger.info(f"Environment configuration loaded: DynamoDB={DYNAMODB_TABLE}, S3={S3_BUCKET}")


# ============================================================================
# CORS HEADERS
# ============================================================================

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Content-Type': 'application/json'
}


# ============================================================================
# BEDROCK AI TOOLS (Phase 2)
# ============================================================================

def generate_copy_impl(campaign_plan: Dict[str, str], brand_context: str) -> List[str]:
    """
    Generate 3 Hinglish social media captions using Claude 3.5 Sonnet.
    
    This function constructs a prompt based on the campaign plan (hook, offer, CTA)
    and brand context, then invokes Amazon Bedrock's Claude 3.5 Sonnet model to
    generate culturally relevant Hinglish captions for Indian youth audiences.
    
    Args:
        campaign_plan: Dict containing 'hook', 'offer', and 'cta' keys
        brand_context: String containing brand guidelines and context
    
    Returns:
        List of 3 Hinglish caption strings, or fallback error message on failure
    """
    try:
        # Construct the prompt for Hinglish copywriting
        prompt = f"""You are Prachar.ai, an expert AI Creative Director specializing in Hinglish social media content for Indian students and creators.

Campaign Plan:
- Hook: {campaign_plan.get('hook', 'Attention-grabbing opening')}
- Offer: {campaign_plan.get('offer', 'Value proposition')}
- Call-to-Action: {campaign_plan.get('cta', 'Action to take')}

Brand Context:
{brand_context if brand_context else 'No specific brand guidelines provided. Use general youth-friendly tone.'}

Task: Generate exactly 3 unique Hinglish social media captions (150-200 characters each) that:
1. Mix Hindi and English naturally (like Indian youth speak)
2. Include relevant emojis
3. Are culturally authentic (references to chai, coding, college life, etc.)
4. Follow the campaign plan structure (hook → offer → CTA)
5. Are engaging and shareable

Format: Return ONLY the 3 captions, separated by newlines, no numbering or extra text."""

        # Prepare the request body for Claude 3.5 Sonnet
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Prepare invoke_model kwargs
        invoke_kwargs = {
            "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "body": json.dumps(request_body)
        }
        
        # Add Guardrails if configured
        if GUARDRAIL_ID:
            invoke_kwargs["guardrailIdentifier"] = GUARDRAIL_ID
            invoke_kwargs["guardrailVersion"] = GUARDRAIL_VERSION
            logger.info(f"Applying Bedrock Guardrails: {GUARDRAIL_ID} (version: {GUARDRAIL_VERSION})")
        
        # Invoke Bedrock Claude 3.5 Sonnet
        logger.info("Invoking Claude 3.5 Sonnet for Hinglish copy generation")
        response = bedrock_runtime.invoke_model(**invoke_kwargs)
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        generated_text = response_body['content'][0]['text']
        
        # Split into list of captions (expecting 3 captions separated by newlines)
        captions = [caption.strip() for caption in generated_text.strip().split('\n') if caption.strip()]
        
        # Ensure we have exactly 3 captions
        if len(captions) < 3:
            logger.warning(f"Generated only {len(captions)} captions, expected 3")
            # Pad with generic captions if needed
            while len(captions) < 3:
                captions.append("🚀 Yeh opportunity miss mat karo! Join us today! 🎯")
        
        captions = captions[:3]  # Take only first 3
        
        logger.info(f"Successfully generated {len(captions)} Hinglish captions")
        return captions
    
    except ClientError as e:
        logger.error(f"AWS Bedrock ClientError in generate_copy_impl: {str(e)}", exc_info=True)
        return ["Error generating copy. Please try again."]
    
    except Exception as e:
        logger.error(f"Unexpected error in generate_copy_impl: {str(e)}", exc_info=True)
        return ["Error generating copy. Please try again."]


def generate_image_impl(caption: str, brand_colors: List[str]) -> str:
    """
    Generate a campaign poster image using Amazon Titan Image Generator.
    
    This function creates a vibrant social media poster based on the provided
    caption and brand colors, then uploads it to S3 and returns the public URL.
    
    Args:
        caption: The social media caption to feature in the poster
        brand_colors: List of hex color codes for brand consistency
    
    Returns:
        Public S3 URL of the generated image, or empty string on failure
    """
    try:
        # Construct the image generation prompt
        colors_text = ", ".join(brand_colors) if brand_colors else "vibrant orange, blue, and purple"
        
        prompt = f"""Create a professional, eye-catching social media poster for Indian youth audience.

Content: {caption}

Design Requirements:
- Modern, vibrant design with colors: {colors_text}
- Include abstract geometric shapes or gradients
- Professional typography with good readability
- Suitable for Instagram/Facebook posts
- Indian cultural aesthetic (modern, not traditional)
- High energy, youth-focused vibe
- No text in the image (text will be added separately)

Style: Modern, minimalist, professional, vibrant, youth-oriented"""

        # Prepare the request body for Titan Image Generator
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 8.0,
                "quality": "premium"
            }
        }
        
        # Invoke Bedrock Titan Image Generator
        logger.info("Invoking Titan Image Generator for campaign poster")
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-image-generator-v1",
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        
        # Extract base64 image data
        base64_image = response_body['images'][0]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_image)
        
        # Generate unique filename
        image_filename = f"campaigns/{uuid.uuid4()}.png"
        
        # Upload to S3
        logger.info(f"Uploading generated image to S3: {S3_BUCKET}/{image_filename}")
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=image_filename,
            Body=image_bytes,
            ContentType='image/png'
        )
        
        # Construct public S3 URL
        s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{image_filename}"
        
        logger.info(f"Image successfully generated and uploaded: {s3_url}")
        return s3_url
    
    except ClientError as e:
        logger.error(f"AWS ClientError in generate_image_impl: {str(e)}", exc_info=True)
        return ""
    
    except Exception as e:
        logger.error(f"Unexpected error in generate_image_impl: {str(e)}", exc_info=True)
        return ""


# ============================================================================
# STRANDS SDK TOOLS (Phase 3)
# ============================================================================

# Define Strands Tools wrapping our implementation functions
generate_copy_tool = Tool(
    name="generate_copy",
    description="Generates 3 Hinglish captions based on a campaign plan and brand context.",
    func=generate_copy_impl
)

generate_image_tool = Tool(
    name="generate_image",
    description="Generates a campaign poster and uploads it to S3. Returns the S3 URL.",
    func=generate_image_impl
)


# ============================================================================
# STRANDS AGENT INITIALIZATION (Phase 3)
# ============================================================================

creative_director = Agent(
    name="CreativeDirector",
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    tools=[generate_copy_tool, generate_image_tool],
    instructions="""You are Prachar.ai, an expert Indian marketing creative director specializing in campaigns for Indian students and creators.

Your task is to autonomously plan and execute social media campaigns:

1. ANALYZE the user's goal and create a strategic Campaign Plan with:
   - hook: An attention-grabbing opening line
   - offer: The core value proposition
   - cta: A clear call-to-action

2. USE the generate_copy tool to create 3 Hinglish captions based on your plan.

3. RESPOND with ONLY valid JSON in this exact format:
{
  "plan": {
    "hook": "Your hook here",
    "offer": "Your offer here",
    "cta": "Your CTA here"
  },
  "captions": ["Caption 1", "Caption 2", "Caption 3"]
}

Do NOT include any markdown formatting, explanations, or extra text. Return ONLY the JSON object."""
)

logger.info("Strands Agent 'CreativeDirector' initialized successfully")


# ============================================================================
# LAMBDA HANDLER
# ============================================================================

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for Prachar.ai campaign generation.
    
    Handles API Gateway requests with proper CORS support, request validation,
    and error handling. Logs all requests to CloudWatch for audit trails.
    
    Args:
        event: API Gateway event object containing HTTP request data
        context: Lambda context object with runtime information
    
    Returns:
        Dict containing statusCode, headers, and body for API Gateway response
    
    Raises:
        Exception: Caught and returned as 500 error response
    """
    
    # Log incoming request for audit trail
    logger.info(f"Received request: {json.dumps(event, default=str)}")
    logger.info(f"Request ID: {context.request_id}")
    
    # ========================================================================
    # CORS PREFLIGHT HANDLING
    # ========================================================================
    
    if event.get('httpMethod') == 'OPTIONS':
        logger.info("Handling CORS preflight request")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'CORS preflight successful'})
        }
    
    # ========================================================================
    # MAIN REQUEST PROCESSING
    # ========================================================================
    
    try:
        # Extract and validate request body
        body = event.get('body')
        
        if not body:
            logger.warning("Request body is missing")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'Request body is required'
                })
            }
        
        # Parse JSON payload
        try:
            payload = json.loads(body) if isinstance(body, str) else body
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in request body: {str(e)}")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'Invalid JSON format in request body'
                })
            }
        
        # Validate required fields
        goal = payload.get('goal')
        
        if not goal:
            logger.warning("Missing required field: goal")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'Missing required field: goal'
                })
            }
        
        # Extract optional fields
        user_id = payload.get('user_id', 'anonymous')
        brand_context = payload.get('brand_context', '')
        
        # Try to extract user_id from Cognito authorizer if available
        user_context = get_user_context(event)
        if user_context and user_context.get('user_id'):
            user_id = user_context['user_id']
            logger.info(f"User authenticated via Cognito: {user_id}")
        
        logger.info(f"Processing campaign request - User: {user_id}, Goal: {goal}")
        
        # ====================================================================
        # PHASE 3: AGENTIC CAMPAIGN GENERATION
        # ====================================================================
        
        # Construct the agent prompt
        agent_prompt = f"Create a campaign for this goal: '{goal}'. Return ONLY a JSON object with 'plan' (hook, offer, cta) and 'captions' (array of 3 strings)."
        
        logger.info(f"Executing Strands Agent with prompt: {agent_prompt}")
        
        # Execute the Strands Agent
        agent_response = creative_director.run(agent_prompt)
        
        logger.info(f"Agent response received: {agent_response}")
        
        # Parse the agent response (handle potential markdown formatting)
        try:
            # Remove markdown code blocks if present
            response_text = agent_response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove trailing ```
            
            response_text = response_text.strip()
            
            # Parse JSON
            parsed_response = json.loads(response_text)
            
            logger.info("Agent response parsed successfully")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response as JSON: {str(e)}")
            logger.error(f"Raw agent response: {agent_response}")
            
            # Fallback response if agent returns malformed JSON
            parsed_response = {
                "plan": {
                    "hook": "Attention Indian students!",
                    "offer": f"Amazing opportunity: {goal}",
                    "cta": "Join us today!"
                },
                "captions": [
                    f"🚀 {goal} - Yeh opportunity miss mat karo! 🎯",
                    f"Arre bhai, {goal} ke liye ready ho jao! 💪✨",
                    f"Indian students, {goal} is calling! Join now! 🇮🇳🔥"
                ]
            }
        
        # Extract campaign plan and captions
        campaign_plan = parsed_response.get('plan', {})
        captions = parsed_response.get('captions', ['Default caption'])
        
        # Select the first caption for image generation
        selected_caption = captions[0] if captions else 'Default campaign poster'
        
        logger.info(f"Generating image for caption: {selected_caption}")
        
        # Generate campaign poster (using default brand colors for now)
        image_url = generate_image_impl(selected_caption, ["#FF5733", "#3498DB"])
        
        if not image_url:
            logger.warning("Image generation failed, using placeholder")
            image_url = "https://via.placeholder.com/1024x1024.png?text=Campaign+Poster"
        
        # ====================================================================
        # DYNAMODB PERSISTENCE
        # ====================================================================
        
        # Generate unique campaign ID
        campaign_id = str(uuid.uuid4())
        
        # Construct campaign record
        campaign_record = {
            'campaign_id': campaign_id,
            'user_id': user_id,
            'goal': goal,
            'plan': campaign_plan,
            'captions': captions,
            'image_url': image_url,
            'status': 'completed',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save to DynamoDB
        try:
            table = dynamodb.Table(DYNAMODB_TABLE)
            table.put_item(Item=campaign_record)
            logger.info(f"Campaign saved to DynamoDB: {campaign_id}")
        except ClientError as e:
            logger.error(f"Failed to save campaign to DynamoDB: {str(e)}")
            # Continue execution even if DynamoDB save fails
        
        # ====================================================================
        # SUCCESS RESPONSE
        # ====================================================================
        
        logger.info(f"Campaign generation completed successfully for user: {user_id}")
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(campaign_record)
        }
    
    except Exception as e:
        # Log full stack trace for debugging
        logger.error(f"Unhandled exception in lambda_handler: {str(e)}", exc_info=True)
        
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred while processing your request',
                'request_id': context.request_id
            })
        }


# ============================================================================
# HELPER FUNCTIONS (For Future Phases)
# ============================================================================

def validate_environment() -> bool:
    """
    Validate that all required environment variables are configured.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    required_vars = ['DYNAMODB_TABLE', 'S3_BUCKET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    return True


def get_user_context(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract user context from API Gateway authorizer (Cognito JWT).
    
    Args:
        event: API Gateway event object
    
    Returns:
        Dict containing user_id and other claims, or None if not authenticated
    """
    authorizer = event.get('requestContext', {}).get('authorizer', {})
    
    if not authorizer:
        logger.warning("No authorizer context found in request")
        return None
    
    claims = authorizer.get('claims', {})
    
    return {
        'user_id': claims.get('sub'),
        'email': claims.get('email'),
        'username': claims.get('cognito:username')
    }


# ============================================================================
# ENTRY POINT VALIDATION
# ============================================================================

if __name__ == '__main__':
    # Local testing support
    logger.info("Lambda handler loaded successfully")
    logger.info(f"Environment: DynamoDB={DYNAMODB_TABLE}, S3={S3_BUCKET}")
    
    # Test event for local development
    test_event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'goal': 'Test campaign for local development',
            'user_id': 'test-user-123'
        })
    }
    
    # Mock context
    class MockContext:
        request_id = 'local-test-request-id'
        function_name = 'prachar-ai-backend'
        memory_limit_in_mb = 512
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:prachar-ai-backend'
    
    # Test handler
    response = lambda_handler(test_event, MockContext())
    print(json.dumps(response, indent=2))
