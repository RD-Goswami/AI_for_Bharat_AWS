# ✅ SCHEMA SYNC - COMPLETE

**Synced Python Code with Live AWS Environment**

---

## 🎯 PROBLEM

The Python Lambda handler was using outdated environment variable names and DynamoDB schema that didn't match Sayandip's live AWS environment.

---

## 🔧 FIXES APPLIED

### Fix 1: Environment Variable Names

**BEFORE:**
```python
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'prachar-ai-campaigns')
S3_BUCKET = os.environ.get('S3_BUCKET', 'prachar-ai-assets')
```

**AFTER:**
```python
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', 'prachar-campaigns')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'prachar-assets-kiit-2026')
```

**Changes:**
- ✅ `DYNAMODB_TABLE` → `DYNAMODB_TABLE_NAME`
- ✅ `prachar-ai-campaigns` → `prachar-campaigns`
- ✅ `S3_BUCKET` → `S3_BUCKET_NAME`
- ✅ `prachar-ai-assets` → `prachar-assets-kiit-2026`

---

### Fix 2: DynamoDB Schema (camelCase Keys)

**BEFORE (Line 665-674):**
```python
campaign_record = {
    'campaign_id': campaign_id,  # snake_case
    'user_id': user_id,          # snake_case
    'goal': goal,
    'plan': campaign_plan,
    'captions': captions,
    'image_url': image_url,
    'status': 'completed',
    'created_at': datetime.utcnow().isoformat()
}
```

**AFTER:**
```python
campaign_record = {
    'campaignId': campaign_id,   # camelCase (PRIMARY KEY)
    'userId': user_id,           # camelCase (SORT KEY)
    'goal': goal,
    'plan': campaign_plan,
    'captions': captions,
    'image_url': image_url,
    'status': 'completed',
    'created_at': datetime.utcnow().isoformat()
}
```

**BEFORE (Line 731-741 - Error Handler):**
```python
campaign_record = {
    'campaign_id': campaign_id,  # snake_case
    'user_id': user_id,          # snake_case
    'goal': goal,
    'plan': mock_campaign['plan'],
    'captions': mock_campaign['captions'],
    'image_url': mock_campaign['image_url'],
    'status': 'completed',
    'created_at': datetime.utcnow().isoformat(),
    'error_recovered': True
}
```

**AFTER:**
```python
campaign_record = {
    'campaignId': campaign_id,   # camelCase (PRIMARY KEY)
    'userId': user_id,           # camelCase (SORT KEY)
    'goal': goal,
    'plan': mock_campaign['plan'],
    'captions': mock_campaign['captions'],
    'image_url': mock_campaign['image_url'],
    'status': 'completed',
    'created_at': datetime.utcnow().isoformat(),
    'error_recovered': True
}
```

**Changes:**
- ✅ `campaign_id` → `campaignId` (matches DynamoDB primary key)
- ✅ `user_id` → `userId` (matches DynamoDB sort key)
- ✅ Updated in both success and error handlers

---

## 📊 LIVE AWS ENVIRONMENT

### DynamoDB Table Schema

**Table Name:** `prachar-campaigns`

**Primary Key:**
- Partition Key: `campaignId` (String)
- Sort Key: `userId` (String)

**Attributes:**
```json
{
  "campaignId": "uuid-string",
  "userId": "user-id-string",
  "goal": "Campaign goal text",
  "plan": {
    "hook": "...",
    "offer": "...",
    "cta": "..."
  },
  "captions": ["...", "...", "..."],
  "image_url": "https://...",
  "status": "completed",
  "created_at": "2026-03-05T10:30:00.000Z"
}
```

### S3 Bucket

**Bucket Name:** `prachar-assets-kiit-2026`

**Purpose:** Store generated campaign images

---

## 🚀 DEPLOYMENT

### Update Lambda Environment Variables

```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment Variables="{
    AWS_REGION=us-east-1,
    DYNAMODB_TABLE_NAME=prachar-campaigns,
    S3_BUCKET_NAME=prachar-assets-kiit-2026,
    GEMINI_API_KEY=your_gemini_key,
    GROQ_API_KEY=your_groq_key,
    OPENROUTER_API_KEY=your_openrouter_key
  }"
```

### Rebuild and Deploy

```bash
# 1. Rebuild Lambda package
cd Prachar.ai/backend
./build_lambda.sh

# 2. Deploy to Lambda
aws lambda update-function-code \
  --function-name prachar-ai-backend \
  --zip-file fileb://prachar-production-backend.zip
```

### Test DynamoDB Write

```bash
curl -X POST https://your-lambda-function-url \
  -H "Content-Type: application/json" \
  -d '{"goal": "Test campaign"}'
```

**Expected:** Campaign saved to DynamoDB with `campaignId` and `userId` keys

---

## 🧪 VERIFICATION

### File Compilation
```bash
python -m py_compile Prachar.ai/backend/aws_lambda_handler.py
# ✅ Exit Code: 0
```

### Environment Variables
```bash
grep "DYNAMODB_TABLE_NAME\|S3_BUCKET_NAME" aws_lambda_handler.py
# ✅ Found: DYNAMODB_TABLE_NAME, S3_BUCKET_NAME
```

### Schema Keys
```bash
grep "campaignId\|userId" aws_lambda_handler.py
# ✅ Found: campaignId (2 locations), userId (2 locations)
```

---

## 📋 CHECKLIST

### Environment Variables
- [x] Changed `DYNAMODB_TABLE` to `DYNAMODB_TABLE_NAME`
- [x] Changed default value to `prachar-campaigns`
- [x] Changed `S3_BUCKET` to `S3_BUCKET_NAME`
- [x] Changed default value to `prachar-assets-kiit-2026`

### DynamoDB Schema
- [x] Changed `campaign_id` to `campaignId` (success handler)
- [x] Changed `user_id` to `userId` (success handler)
- [x] Changed `campaign_id` to `campaignId` (error handler)
- [x] Changed `user_id` to `userId` (error handler)
- [x] Left other keys unchanged (goal, plan, captions, etc.)

### Testing
- [x] File compiles without errors
- [x] Environment variables verified
- [x] Schema keys verified
- [x] Ready for deployment

---

## 🔍 DEBUGGING

### Check DynamoDB Item

```bash
aws dynamodb get-item \
  --table-name prachar-campaigns \
  --key '{"campaignId": {"S": "your-campaign-id"}, "userId": {"S": "your-user-id"}}'
```

### Check CloudWatch Logs

```bash
aws logs tail /aws/lambda/prachar-ai-backend --follow
```

**Look for:**
- ✅ "Campaign saved to DynamoDB: {campaignId}"
- ✅ No "ValidationException" errors
- ✅ No "ResourceNotFoundException" errors

---

## ⚠️ IMPORTANT NOTES

### Why camelCase?

The live DynamoDB table uses camelCase for primary keys:
- `campaignId` (Partition Key)
- `userId` (Sort Key)

This is a common pattern in AWS/JavaScript ecosystems and must match exactly for DynamoDB operations to work.

### Why Different Environment Variable Names?

The live Lambda function uses:
- `DYNAMODB_TABLE_NAME` (not `DYNAMODB_TABLE`)
- `S3_BUCKET_NAME` (not `S3_BUCKET`)

This matches AWS naming conventions and the existing infrastructure.

---

## 🎉 FINAL STATUS

**Issue:** Schema mismatch with live AWS environment  
**Root Cause:** Outdated environment variable names and snake_case keys  
**Fix Applied:** Updated to match live AWS configuration  
**Testing:** ✅ File compiles, schema verified  
**Status:** 🟢 SYNCED  

---

## 📚 RELATED FILES

- `aws_lambda_handler.py` - Updated handler
- `DIAMOND_CASCADE_COMPLETE.md` - Architecture docs
- `502_FIX_COMPLETE.md` - Response format fix
- `GEMINI_404_FIX.md` - Gemini endpoint fix

---

**Team NEONX - AI for Bharat Hackathon**  
**Date:** March 5, 2026  
**Fix:** Schema Synced with Live AWS Environment
