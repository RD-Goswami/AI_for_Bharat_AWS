# 🔧 AWS CONFIGURATION REFERENCE

**Quick Reference for Live AWS Environment**

---

## 📋 LAMBDA ENVIRONMENT VARIABLES

### Required Variables

```bash
# AWS Infrastructure
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=prachar-campaigns
S3_BUCKET_NAME=prachar-assets-kiit-2026

# Diamond Cascade API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Set via AWS CLI

```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment Variables="{
    AWS_REGION=us-east-1,
    DYNAMODB_TABLE_NAME=prachar-campaigns,
    S3_BUCKET_NAME=prachar-assets-kiit-2026,
    GEMINI_API_KEY=AIzaSy...,
    GROQ_API_KEY=gsk_...,
    OPENROUTER_API_KEY=sk-or-v1-...
  }"
```

---

## 🗄️ DYNAMODB TABLE SCHEMA

### Table Details

**Table Name:** `prachar-campaigns`

**Primary Key:**
- Partition Key: `campaignId` (String)
- Sort Key: `userId` (String)

### Item Structure

```json
{
  "campaignId": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "user-123",
  "goal": "Hype my college tech fest",
  "plan": {
    "hook": "🚀 Ready to dominate your campus?",
    "offer": "Exclusive AI & ML workshop strategies...",
    "cta": "Join the tech revolution today!"
  },
  "captions": [
    "Bhai log, time to build! 💻🔥...",
    "From dorm rooms to board rooms...",
    "Campus tech fests just got an AI upgrade..."
  ],
  "image_url": "https://images.unsplash.com/photo-...",
  "status": "completed",
  "created_at": "2026-03-05T10:30:00.000Z"
}
```

### Key Points

- ✅ Use `campaignId` (camelCase, not snake_case)
- ✅ Use `userId` (camelCase, not snake_case)
- ✅ Both keys are required for all operations
- ✅ `campaignId` is a UUID string
- ✅ `userId` can be "anonymous" for unauthenticated users

---

## 🪣 S3 BUCKET

### Bucket Details

**Bucket Name:** `prachar-assets-kiit-2026`

**Region:** `us-east-1`

**Purpose:** Store generated campaign images

### Object Structure

```
prachar-assets-kiit-2026/
└── campaigns/
    ├── 550e8400-e29b-41d4-a716-446655440000.png
    ├── 660e8400-e29b-41d4-a716-446655440001.png
    └── ...
```

### Public URL Format

```
https://prachar-assets-kiit-2026.s3.amazonaws.com/campaigns/{uuid}.png
```

---

## 🚀 DEPLOYMENT COMMANDS

### Full Deployment

```bash
# 1. Navigate to backend
cd Prachar.ai/backend

# 2. Build Lambda package
./build_lambda.sh

# 3. Deploy code
aws lambda update-function-code \
  --function-name prachar-ai-backend \
  --zip-file fileb://prachar-production-backend.zip

# 4. Update environment variables (if needed)
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment Variables="{...}"

# 5. Test
curl -X POST https://your-lambda-function-url \
  -H "Content-Type: application/json" \
  -d '{"goal": "Test campaign"}'
```

---

## 🧪 TESTING COMMANDS

### Test Lambda Locally

```bash
cd Prachar.ai/backend
python aws_lambda_handler.py
```

### Test DynamoDB Connection

```bash
aws dynamodb describe-table --table-name prachar-campaigns
```

### Test S3 Bucket

```bash
aws s3 ls s3://prachar-assets-kiit-2026/
```

### Query DynamoDB Item

```bash
aws dynamodb get-item \
  --table-name prachar-campaigns \
  --key '{"campaignId": {"S": "your-id"}, "userId": {"S": "user-123"}}'
```

---

## 📊 MONITORING

### CloudWatch Logs

```bash
# Tail logs
aws logs tail /aws/lambda/prachar-ai-backend --follow

# Get recent logs
aws logs tail /aws/lambda/prachar-ai-backend --since 1h
```

### Lambda Metrics

```bash
# Get invocation count
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=prachar-ai-backend \
  --start-time 2026-03-05T00:00:00Z \
  --end-time 2026-03-05T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

---

## ⚠️ COMMON ISSUES

### Issue 1: ValidationException

**Error:** `One or more parameter values were invalid: Missing the key campaignId`

**Solution:** Ensure you're using `campaignId` (camelCase), not `campaign_id`

### Issue 2: ResourceNotFoundException

**Error:** `Requested resource not found: Table: prachar-ai-campaigns not found`

**Solution:** Update environment variable to `DYNAMODB_TABLE_NAME=prachar-campaigns`

### Issue 3: AccessDeniedException

**Error:** `User is not authorized to perform: dynamodb:PutItem`

**Solution:** Check Lambda execution role has DynamoDB permissions

---

## ✅ VERIFICATION CHECKLIST

### Environment Variables
- [ ] `DYNAMODB_TABLE_NAME` set to `prachar-campaigns`
- [ ] `S3_BUCKET_NAME` set to `prachar-assets-kiit-2026`
- [ ] `GEMINI_API_KEY` configured
- [ ] `GROQ_API_KEY` configured
- [ ] `OPENROUTER_API_KEY` configured

### DynamoDB
- [ ] Table `prachar-campaigns` exists
- [ ] Primary key is `campaignId` (String)
- [ ] Sort key is `userId` (String)
- [ ] Lambda has PutItem permission

### S3
- [ ] Bucket `prachar-assets-kiit-2026` exists
- [ ] Lambda has PutObject permission
- [ ] Bucket is in `us-east-1` region

### Lambda
- [ ] Function name: `prachar-ai-backend`
- [ ] Runtime: Python 3.x
- [ ] Handler: `aws_lambda_handler.lambda_handler`
- [ ] Timeout: 60 seconds (recommended)
- [ ] Memory: 512 MB (recommended)

---

**Team NEONX - AI for Bharat Hackathon**  
**Date:** March 5, 2026  
**Version:** Production
