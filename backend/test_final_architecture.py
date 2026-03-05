#!/usr/bin/env python3
"""
Test script for Final Production Architecture
Tests the single entry point with Amazon models only
"""

import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work correctly."""
    print("\n" + "="*60)
    print("🧪 TEST 1: IMPORTS")
    print("="*60)
    
    try:
        from aws_lambda_handler import (
            lambda_handler,
            generate_copy,
            generate_image,
            creative_director,
            get_mock_campaign,
            NOVA_PRO_MODEL_ID,
            NOVA_LITE_MODEL_ID,
            TITAN_TEXT_MODEL_ID,
            AGENT_MODEL_ID
        )
        
        print("✅ All imports successful")
        print(f"   Agent Model: {AGENT_MODEL_ID}")
        print(f"   Fallback Cascade: {NOVA_PRO_MODEL_ID} → {NOVA_LITE_MODEL_ID} → {TITAN_TEXT_MODEL_ID}")
        return True
    
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_strands_sdk():
    """Test that Strands SDK is correctly configured."""
    print("\n" + "="*60)
    print("🧪 TEST 2: STRANDS SDK")
    print("="*60)
    
    try:
        from strands import Agent, tool
        print("✅ Strands SDK import successful (lowercase 't')")
        
        from aws_lambda_handler import creative_director
        print(f"✅ Agent initialized: {creative_director}")
        print(f"   Model: {creative_director.model if hasattr(creative_director, 'model') else 'N/A'}")
        
        return True
    
    except ImportError as e:
        print(f"❌ Strands SDK import failed: {e}")
        print("   Install: pip install strands-sdk")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_mock_campaigns():
    """Test that mock campaigns are properly configured."""
    print("\n" + "="*60)
    print("🧪 TEST 3: MOCK CAMPAIGNS")
    print("="*60)
    
    try:
        from aws_lambda_handler import get_mock_campaign, MOCK_CAMPAIGNS
        
        print(f"✅ Mock campaigns loaded: {len(MOCK_CAMPAIGNS)} categories")
        
        # Test different goal types
        test_goals = [
            ("Python AI Workshop", "tech"),
            ("College fest celebration", "fest"),
            ("Coding bootcamp", "workshop"),
            ("Generic campaign", "default")
        ]
        
        for goal, expected_type in test_goals:
            campaign = get_mock_campaign(goal)
            print(f"   Goal: '{goal}' → {len(campaign['captions'])} captions")
            
            # Verify structure
            assert 'plan' in campaign
            assert 'captions' in campaign
            assert 'image_url' in campaign
            assert len(campaign['captions']) == 3
        
        print("✅ All mock campaigns valid")
        return True
    
    except Exception as e:
        print(f"❌ Mock campaign test failed: {e}")
        return False


def test_lambda_handler():
    """Test the Lambda handler with a mock event."""
    print("\n" + "="*60)
    print("🧪 TEST 4: LAMBDA HANDLER")
    print("="*60)
    
    try:
        from aws_lambda_handler import lambda_handler
        
        # Create test event
        test_event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'goal': 'Python AI Workshop for college students',
                'user_id': 'test-user-123'
            })
        }
        
        # Mock context
        class MockContext:
            request_id = 'test-request-id'
            function_name = 'prachar-ai-backend'
            memory_limit_in_mb = 512
        
        print("Invoking lambda_handler with test event...")
        response = lambda_handler(test_event, MockContext())
        
        # Verify response structure
        assert 'statusCode' in response
        assert 'headers' in response
        assert 'body' in response
        
        print(f"✅ Lambda handler returned: {response['statusCode']}")
        
        # Parse body
        body = json.loads(response['body'])
        
        # Verify campaign structure
        assert 'campaign_id' in body
        assert 'plan' in body
        assert 'captions' in body
        assert 'image_url' in body
        
        print(f"   Campaign ID: {body['campaign_id']}")
        print(f"   Plan: {body['plan']['hook'][:50]}...")
        print(f"   Captions: {len(body['captions'])} generated")
        print(f"   Image: {body['image_url'][:60]}...")
        
        print("✅ Lambda handler test passed")
        return True
    
    except Exception as e:
        print(f"❌ Lambda handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cors_preflight():
    """Test CORS preflight handling."""
    print("\n" + "="*60)
    print("🧪 TEST 5: CORS PREFLIGHT")
    print("="*60)
    
    try:
        from aws_lambda_handler import lambda_handler
        
        # Create OPTIONS request
        test_event = {
            'httpMethod': 'OPTIONS'
        }
        
        class MockContext:
            request_id = 'test-cors-request'
        
        response = lambda_handler(test_event, MockContext())
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        
        print("✅ CORS preflight handled correctly")
        return True
    
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False


def test_global_safety_net():
    """Test that global safety net returns 200 even on errors."""
    print("\n" + "="*60)
    print("🧪 TEST 6: GLOBAL SAFETY NET")
    print("="*60)
    
    try:
        from aws_lambda_handler import lambda_handler
        
        # Create invalid event (should trigger safety net)
        test_event = {
            'httpMethod': 'POST',
            'body': 'invalid json'
        }
        
        class MockContext:
            request_id = 'test-safety-net'
        
        response = lambda_handler(test_event, MockContext())
        
        # Should return 400 for invalid JSON (not 502)
        assert response['statusCode'] in [200, 400]
        assert 'body' in response
        
        print(f"✅ Safety net working: returned {response['statusCode']}")
        return True
    
    except Exception as e:
        print(f"❌ Safety net test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🚀 FINAL ARCHITECTURE TEST SUITE")
    print("="*60)
    print("Testing: aws_lambda_handler.py (ONLY entry point)")
    print("Models: Amazon only (no Anthropic)")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Strands SDK", test_strands_sdk),
        ("Mock Campaigns", test_mock_campaigns),
        ("Lambda Handler", test_lambda_handler),
        ("CORS Preflight", test_cors_preflight),
        ("Global Safety Net", test_global_safety_net)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print("="*60)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Architecture is production-ready")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("   Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
