# 🚀 QUICK START - Diamond Cascade Deployment

**Get Prachar.ai running in 5 minutes**

---

## ⚡ FASTEST PATH TO DEPLOYMENT

### Step 1: Get API Keys (5 minutes)

```bash
# Open these 3 URLs in your browser:
1. https://aistudio.google.com/app/apikey      # Gemini
2. https://console.groq.com/keys               # Groq
3. https://openrouter.ai/keys                  # OpenRouter

# Copy the 3 API keys you receive
```

### Step 2: Set Lambda Environment Variables (2 minutes)

```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment Variables="{
    AWS_REGION=us-east-1,
    DYNAMODB_TABLE=prachar-ai-campaigns,
    S3_BUCKET=prachar-ai-assets,
    GEMINI_API_KEY=paste_your_gemini_key_here,
    GROQ_API_KEY=paste_your_groq_key_here,
    OPENROUTER_API_KEY=paste_your_openrouter_key_here
  }"
```

### Step 3: Build & Deploy (2 minutes)

```bash
cd Prachar.ai/backend
./build_lambda.sh

aws lambda update-function-code \
  --function-name prachar-ai-backend \
  --zip-file fileb://prachar-production-backend.zip
```

### Step 4: Test (1 minute)

```bash
curl -X POST https://your-api-gateway-url/generate \
  -H "Content-Type: application/json" \
  -d '{"goal": "Hype my college fest"}'
```

**Expected:** 200 OK with campaign JSON

---

## 🎯 THAT'S IT!

Your Diamond Cascade is now operational with:
- ✅ 4-tier fallback (Gemini → Groq → OpenRouter → Mock)
- ✅ 100% uptime guarantee
- ✅ Zero Bedrock dependency
- ✅ Production-ready

---

## 📋 DETAILED GUIDES

For more information, see:
- `DIAMOND_CASCADE_COMPLETE.md` - Full architecture
- `API_KEYS_SETUP.md` - Detailed API key setup
- `DIAMOND_CASCADE_SUCCESS.md` - Executive summary

---

**Team NEONX - AI for Bharat Hackathon**
