#!/usr/bin/env python3
"""
Test script for Enterprise Multi-Model Fallback Router

This script tests the 4-tier fallback cascade:
1. Nova Pro (primary)
2. Nova Lite (fallback 1)
3. Titan Text Express (fallback 2)
4. Intelligent Mock Data (final fallback)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the agent module
from agent import invoke_bedrock_with_fallback, NOVA_PRO_MODEL_ID, NOVA_LITE_MODEL_ID, TITAN_TEXT_MODEL_ID

def test_fallback_router():
    """Test the multi-model fallback router with a sample prompt."""
    
    print("\n" + "="*60)
    print("🧪 TESTING ENTERPRISE MULTI-MODEL FALLBACK ROUTER")
    print("="*60 + "\n")
    
    # Test prompt
    test_prompt = """Generate 3 Hinglish social media captions for a college tech fest.

Requirements:
- Mix Hindi and English naturally
- Use emojis for Indian youth
- Keep under 280 characters each
- Make it energetic and authentic

Output format:
1. [First caption]
2. [Second caption]
3. [Third caption]"""
    
    test_goal = "College tech fest promotion"
    
    print(f"Test Prompt: {test_prompt[:100]}...")
    print(f"Test Goal: {test_goal}")
    print("\n" + "="*60 + "\n")
    
    # Test the fallback router
    try:
        result = invoke_bedrock_with_fallback(test_prompt, test_goal)
        
        print("\n" + "="*60)
        print("✅ TEST PASSED: Fallback router returned result")
        print("="*60)
        print(f"\nGenerated Text:\n{result}")
        print("\n" + "="*60)
        
        # Verify result is not empty
        if result and len(result) > 50:
            print("\n✅ Result validation: PASSED")
            print(f"   - Length: {len(result)} characters")
            print(f"   - Contains content: YES")
            return True
        else:
            print("\n⚠️  Result validation: WARNING")
            print(f"   - Length: {len(result)} characters")
            print(f"   - Result may be too short")
            return False
    
    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED: Exception occurred")
        print("="*60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_availability():
    """Test if all models are accessible in the configured region."""
    
    print("\n" + "="*60)
    print("🔍 CHECKING MODEL AVAILABILITY")
    print("="*60 + "\n")
    
    import boto3
    from botocore.exceptions import ClientError
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"Region: {region}")
    print(f"Models to check:")
    print(f"  1. {NOVA_PRO_MODEL_ID}")
    print(f"  2. {NOVA_LITE_MODEL_ID}")
    print(f"  3. {TITAN_TEXT_MODEL_ID}")
    print("\n" + "-"*60 + "\n")
    
    # Initialize Bedrock client
    try:
        bedrock = boto3.client('bedrock', region_name=region)
        
        # List foundation models
        response = bedrock.list_foundation_models()
        available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
        
        # Check each model
        models_to_check = [
            ("Nova Pro", NOVA_PRO_MODEL_ID),
            ("Nova Lite", NOVA_LITE_MODEL_ID),
            ("Titan Text", TITAN_TEXT_MODEL_ID)
        ]
        
        all_available = True
        for name, model_id in models_to_check:
            if model_id in available_models:
                print(f"✅ {name}: Available")
            else:
                print(f"⚠️  {name}: Not found in region")
                all_available = False
        
        print("\n" + "-"*60)
        
        if all_available:
            print("\n✅ All models are available in the region")
        else:
            print("\n⚠️  Some models may not be available")
            print("   Check AWS Bedrock Console → Model access")
        
        return all_available
    
    except ClientError as e:
        print(f"❌ AWS Error: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False


def test_credentials():
    """Test if AWS credentials are properly configured."""
    
    print("\n" + "="*60)
    print("🔑 CHECKING AWS CREDENTIALS")
    print("="*60 + "\n")
    
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    
    try:
        # Try to get caller identity
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print("✅ AWS Credentials: Valid")
        print(f"   Account: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        print(f"   User ID: {identity['UserId']}")
        
        return True
    
    except NoCredentialsError:
        print("❌ AWS Credentials: Not found")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")
        return False
    
    except ClientError as e:
        print(f"❌ AWS Credentials: Invalid")
        print(f"   Error: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False


def main():
    """Run all tests."""
    
    print("\n" + "="*60)
    print("🚀 ENTERPRISE MULTI-MODEL FALLBACK ROUTER TEST SUITE")
    print("="*60)
    
    # Test 1: Credentials
    creds_ok = test_credentials()
    
    # Test 2: Model Availability (only if credentials are valid)
    if creds_ok:
        models_ok = test_model_availability()
    else:
        models_ok = False
        print("\n⚠️  Skipping model availability check (credentials invalid)")
    
    # Test 3: Fallback Router
    router_ok = test_fallback_router()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"  Credentials: {'✅ PASS' if creds_ok else '❌ FAIL'}")
    print(f"  Model Availability: {'✅ PASS' if models_ok else '⚠️  WARNING'}")
    print(f"  Fallback Router: {'✅ PASS' if router_ok else '❌ FAIL'}")
    print("="*60)
    
    if creds_ok and router_ok:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        print("   The fallback router is working correctly.")
        return 0
    elif router_ok:
        print("\n✅ FALLBACK ROUTER WORKING")
        print("   Some models may not be available, but fallback is functional.")
        return 0
    else:
        print("\n❌ TESTS FAILED")
        print("   Check the errors above and fix configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
