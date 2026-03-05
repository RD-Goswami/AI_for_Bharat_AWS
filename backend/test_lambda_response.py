"""
Test Lambda Handler Response Format
Verifies that lambda_handler returns correct API Gateway/Function URL proxy format
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Mock environment variables
os.environ['DYNAMODB_TABLE'] = 'test-table'
os.environ['S3_BUCKET'] = 'test-bucket'
os.environ['AWS_REGION'] = 'us-east-1'

# Import the handler
from aws_lambda_handler import lambda_handler

# Mock context
class MockContext:
    request_id = 'test-request-id'
    function_name = 'test-function'
    memory_limit_in_mb = 512
    invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test'

def test_lambda_response_format():
    """Test that lambda_handler returns correct proxy format"""
    
    print("🧪 Testing Lambda Handler Response Format\n")
    
    # Test 1: Valid request
    print("Test 1: Valid request with goal")
    event = {
        'body': json.dumps({
            'goal': 'Hype my college tech fest'
        })
    }
    
    response = lambda_handler(event, MockContext())
    
    # Verify response structure
    assert 'statusCode' in response, "❌ Missing statusCode"
    assert 'headers' in response, "❌ Missing headers"
    assert 'body' in response, "❌ Missing body"
    
    print(f"✅ statusCode: {response['statusCode']}")
    print(f"✅ headers: {response['headers']}")
    
    # Verify body is a string (JSON serialized)
    assert isinstance(response['body'], str), "❌ Body must be a JSON string"
    print(f"✅ body is JSON string: {len(response['body'])} chars")
    
    # Verify body can be parsed
    try:
        body_data = json.loads(response['body'])
        print(f"✅ body is valid JSON")
        print(f"✅ campaign_id: {body_data.get('campaign_id', 'N/A')}")
        print(f"✅ goal: {body_data.get('goal', 'N/A')}")
        print(f"✅ captions count: {len(body_data.get('captions', []))}")
    except json.JSONDecodeError as e:
        print(f"❌ Body is not valid JSON: {e}")
        return False
    
    # Verify CORS headers
    assert 'Access-Control-Allow-Origin' in response['headers'], "❌ Missing CORS header"
    print(f"✅ CORS headers present")
    
    print("\n" + "="*60)
    
    # Test 2: Empty body (should use default goal)
    print("\nTest 2: Empty body (should use default goal)")
    event = {
        'body': '{}'
    }
    
    response = lambda_handler(event, MockContext())
    
    assert response['statusCode'] == 200, f"❌ Expected 200, got {response['statusCode']}"
    print(f"✅ statusCode: {response['statusCode']}")
    
    body_data = json.loads(response['body'])
    print(f"✅ goal: {body_data.get('goal', 'N/A')}")
    
    print("\n" + "="*60)
    
    # Test 3: CORS preflight
    print("\nTest 3: CORS preflight (OPTIONS)")
    event = {
        'httpMethod': 'OPTIONS'
    }
    
    response = lambda_handler(event, MockContext())
    
    assert response['statusCode'] == 200, f"❌ Expected 200, got {response['statusCode']}"
    print(f"✅ statusCode: {response['statusCode']}")
    print(f"✅ CORS preflight handled")
    
    print("\n" + "="*60)
    
    # Test 4: Stringified body
    print("\nTest 4: Stringified JSON body")
    event = {
        'body': '{"goal": "Python workshop for students"}'
    }
    
    response = lambda_handler(event, MockContext())
    
    assert response['statusCode'] == 200, f"❌ Expected 200, got {response['statusCode']}"
    body_data = json.loads(response['body'])
    print(f"✅ statusCode: {response['statusCode']}")
    print(f"✅ goal: {body_data.get('goal', 'N/A')}")
    
    print("\n" + "="*60)
    print("\n🎉 ALL TESTS PASSED!")
    print("\n✅ Lambda handler returns correct API Gateway proxy format")
    print("✅ Response body is properly JSON serialized")
    print("✅ CORS headers are present")
    print("✅ Ready for deployment")
    
    return True

if __name__ == '__main__':
    try:
        success = test_lambda_response_format()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
