# 🔑 API KEYS SETUP GUIDE - 4-Tier Diamond Cascade

**Quick Reference for Setting Up External AI Provider API Keys**

---

## 🎯 REQUIRED API KEYS

You need 3 API keys for the Diamond Cascade to work optimally:

1. **GEMINI_API_KEY** (Tier 1 - Primary)
2. **GROQ_API_KEY** (Tier 2 - Secondary)
3. **OPENROUTER_API_KEY** (Tier 3 - Tertiary)

**Note:** If any key is missing, the cascade will skip that tier and move to the next. Tier 4 (Titanium Shield) always works as the final fallback.

---

## 📋 STEP-BY-STEP SETUP

### 1. Google Gemini API Key (Tier 1)

**Get Your Key:**
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

**Free Tier Limits:**
- 15 requests per minute
- 1 million tokens per minute
- No credit card required

**Model Used:**
- `gemini-2.0-flash-exp` (Experimental, best quality)

**Add to Lambda:**
```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment Variables="{GEMINI_API_KEY=AIzaSy...your_key_here}"
```

---

### 2. Groq API Key (Tier 2)

**Get Your Key:**
1. Visit: https://console.groq.com/keys
2. Sign up with email or GitHub
3. Click "Create API Key"
4. Give it a name (e.g., "Prachar.ai Production")
5. Copy the key (starts with `gsk_...`)

**Free Tier Limits:**
- 30 requests per minute
- 6,000 tokens per minute
- No credit card required

**Model Used:**
- `llama3-70b-8192` (Ultra-fast inference)

**Add to Lambda:**
```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment Variables="{GROQ_API_KEY=gsk_...your_key_here}"
```

---

### 3. OpenRouter API Key (Tier 3)

**Get Your Key:**
1. Visit: https://openrouter.ai/keys
2. Sign in with Google or GitHub
3. Click "Create Key"
4. Give it a name (e.g., "Prachar.ai")
5. Copy the key (starts with `sk-or-v1-...`)

**Free Tier Limits:**
- Unlimited requests (community-funded models)
- No rate limits on free models
- No credit card required

**Model Used:**
- `meta-llama/llama-3-8b-instruct:free` (Free, reliable)

**Add to Lambda:**
```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment Variables="{OPENROUTER_API_KEY=sk-or-v1-...your_key_here}"
```

---

## 🚀 COMPLETE LAMBDA ENVIRONMENT SETUP

### All Environment Variables at Once

```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment Variables="{
    AWS_REGION=us-east-1,
    DYNAMODB_TABLE=prachar-ai-campaigns,
    S3_BUCKET=prachar-ai-assets,
    GEMINI_API_KEY=AIzaSy...your_gemini_key,
    GROQ_API_KEY=gsk_...your_groq_key,
    OPENROUTER_API_KEY=sk-or-v1-...your_openrouter_key
  }"
```

### Via AWS Console

1. Go to AWS Lambda Console
2. Select `prachar-ai-backend` function
3. Click "Configuration" tab
4. Click "Environment variables"
5. Click "Edit"
6. Add each key-value pair:
   - Key: `GEMINI_API_KEY`, Value: `AIzaSy...`
   - Key: `GROQ_API_KEY`, Value: `gsk_...`
   - Key: `OPENROUTER_API_KEY`, Value: `sk-or-v1-...`
7. Click "Save"

---

## 🧪 TESTING YOUR KEYS

### Test Locally

Create a test file `test_api_keys.py`:

```python
import os
import json
from urllib.request import Request, urlopen

# Test Gemini
def test_gemini():
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return False
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Say hello"}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        req = Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}, method='POST')
        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            print("✅ Gemini API key works!")
            return True
    except Exception as e:
        print(f"❌ Gemini API key failed: {e}")
        return False

# Test Groq
def test_groq():
    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        print("❌ GROQ_API_KEY not set")
        return False
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    try:
        req = Request(url, data=json.dumps(payload).encode(), headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }, method='POST')
        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            print("✅ Groq API key works!")
            return True
    except Exception as e:
        print(f"❌ Groq API key failed: {e}")
        return False

# Test OpenRouter
def test_openrouter():
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set")
        return False
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    try:
        req = Request(url, data=json.dumps(payload).encode(), headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }, method='POST')
        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            print("✅ OpenRouter API key works!")
            return True
    except Exception as e:
        print(f"❌ OpenRouter API key failed: {e}")
        return False

if __name__ == '__main__':
    print("🔷 Testing Diamond Cascade API Keys...\n")
    
    gemini_ok = test_gemini()
    groq_ok = test_groq()
    openrouter_ok = test_openrouter()
    
    print("\n📊 Results:")
    print(f"Tier 1 (Gemini): {'✅' if gemini_ok else '❌'}")
    print(f"Tier 2 (Groq): {'✅' if groq_ok else '❌'}")
    print(f"Tier 3 (OpenRouter): {'✅' if openrouter_ok else '❌'}")
    print(f"Tier 4 (Titanium Shield): ✅ (Always works)")
    
    if gemini_ok or groq_ok or openrouter_ok:
        print("\n✅ At least one API key is working. Diamond Cascade is operational!")
    else:
        print("\n⚠️ No API keys working. Will use Tier 4 (Titanium Shield) only.")
```

**Run the test:**
```bash
export GEMINI_API_KEY="your_key_here"
export GROQ_API_KEY="your_key_here"
export OPENROUTER_API_KEY="your_key_here"

python test_api_keys.py
```

---

## 🔒 SECURITY BEST PRACTICES

### DO:
- ✅ Store keys in AWS Lambda Environment Variables
- ✅ Use AWS Secrets Manager for production
- ✅ Rotate keys regularly
- ✅ Monitor API usage
- ✅ Set up billing alerts

### DON'T:
- ❌ Commit keys to Git
- ❌ Share keys in Slack/Discord
- ❌ Use the same key across projects
- ❌ Store keys in code files
- ❌ Log keys in CloudWatch

---

## 📊 MONITORING API USAGE

### Gemini Usage Dashboard
- Visit: https://aistudio.google.com/app/apikey
- Click on your API key
- View usage statistics

### Groq Usage Dashboard
- Visit: https://console.groq.com/usage
- View requests per minute
- Monitor token consumption

### OpenRouter Usage Dashboard
- Visit: https://openrouter.ai/activity
- View request history
- Monitor credits (if using paid models)

---

## 🆘 TROUBLESHOOTING

### "Invalid API Key" Error

**Gemini:**
- Check key starts with `AIza`
- Verify key is enabled in Google AI Studio
- Check API is enabled for your project

**Groq:**
- Check key starts with `gsk_`
- Verify account is active
- Check rate limits not exceeded

**OpenRouter:**
- Check key starts with `sk-or-v1-`
- Verify account is active
- Check model is available

### "Rate Limit Exceeded" Error

**Solution:**
- Wait for rate limit to reset (1 minute)
- Cascade will automatically move to next tier
- Tier 4 (Titanium Shield) has no rate limits

### "Timeout" Error

**Solution:**
- Check internet connectivity
- Increase timeout in code (currently 15s)
- Cascade will automatically move to next tier

---

## 🎯 RECOMMENDED SETUP

### For Development:
- Set up all 3 API keys
- Test each tier individually
- Monitor CloudWatch logs

### For Production:
- Set up all 3 API keys
- Use AWS Secrets Manager
- Set up CloudWatch alarms
- Monitor API usage dashboards

### For Demo/Hackathon:
- At minimum, set up Gemini (Tier 1)
- Tier 4 (Titanium Shield) always works as backup
- 100% uptime guaranteed

---

## ✅ VERIFICATION CHECKLIST

- [ ] Created Gemini API key
- [ ] Created Groq API key
- [ ] Created OpenRouter API key
- [ ] Added keys to Lambda environment variables
- [ ] Tested keys locally
- [ ] Verified keys in AWS Console
- [ ] Monitored first API call in CloudWatch
- [ ] Set up billing alerts (optional)

---

**Status:** Ready for API Key Setup  
**Required Keys:** 3 (Gemini, Groq, OpenRouter)  
**Minimum Keys:** 0 (Tier 4 always works)  
**Setup Time:** 10-15 minutes  
**Cost:** $0 (all free tiers)  

**Team NEONX - AI for Bharat Hackathon**  
**Date:** March 5, 2026
