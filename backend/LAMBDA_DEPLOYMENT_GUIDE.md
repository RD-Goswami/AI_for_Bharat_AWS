# 🚀 AWS Lambda Deployment Guide - Prachar.ai Backend

**Complete guide for deploying the enterprise-grade Lambda handler**

---

## 📋 OVERVIEW

The `aws_lambda_handler.py` is now complete with all three phases:

- ✅ **Phase 1:** Infrastructure skeleton (AWS clients, CORS, logging)
- ✅ **Phase 2:** Bedrock AI tools (Claude 3.5 Sonnet, Titan Image Generator)
- ✅ **Phase 3:** Strands Agent integration and DynamoDB persistence

---

## 🏗️ ARCHITECTURE SUMMARY

```
API Gateway → Lambda Handler → Strands Agent → Bedrock (Claude + Titan)
                    ↓                              ↓
                DynamoDB ← Campaign Record ← S3 (Images)
```

**Flow:**
1. User submits goal via API Gateway
2. Lambda validates request and extracts user context
3. Strands Agent autonomously plans campaign
4. Claude 3.5 generates 3 Hinglish captions
5. Titan generates campaign poster
6. Image uploaded to S3
7. Campaign saved to DynamoDB
8. Complete campaign returned to user

---

## 📦 STEP 1: PREPARE DEPLOYMENT PACKAGE

### 1.1 Install Dependencies

```bash
cd Prachar.ai/backend

# Create deployment directory
mkdir lambda_deployment
cd lambda_deployment

# Install dependencies to this directory
pip install --target . boto3 strands-sdk

# Copy the handler
cp ../aws_lambda_handler.py .

# Create deployment package
zip -r prachar-ai-lambda.zip .
```

### 1.2 Alternative: Using Lambda Layers

**For Strands SDK (recommended):**

```bash
# Create layer directory
mkdir -p lambda_layer/python

# Install Strands SDK
pip install --target lambda_layer/python strands-sdk

# Create layer zip
cd lambda_layer
zip -r strands-layer.zip python/
```

---

## ☁️ STEP 2: CREATE AWS RESOURCES

### 2.1 Create DynamoDB Table

```bash
aws dynamodb create-table \
  --table-name prachar-ai-campaigns \
  --attribute-definitions \
    AttributeName=campaign_id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=campaign_id,KeyType=HASH \
  --global-secondary-indexes \
    "[{
      \"IndexName\": \"user-index\",
      \"KeySchema\": [{\"AttributeName\":\"user_id\",\"KeyType\":\"HASH\"}],
      \"Projection\": {\"ProjectionType\":\"ALL\"},
      \"ProvisionedThroughput\": {\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
    }]" \
  --provisioned-throughput \
    ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1
```

### 2.2 Create S3 Bucket

```bash
aws s3 mb s3://prachar-ai-assets --region us-east-1

# Enable public read access for campaign images
aws s3api put-bucket-policy \
  --bucket prachar-ai-assets \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::prachar-ai-assets/campaigns/*"
    }]
  }'
```

### 2.3 Create IAM Role for Lambda

```bash
# Create trust policy
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name PracharAI-Lambda-ExecutionRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name PracharAI-Lambda-ExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name PracharAI-Lambda-ExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam attach-role-policy \
  --role-name PracharAI-Lambda-ExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
  --role-name PracharAI-Lambda-ExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

---

## 🔧 STEP 3: CREATE LAMBDA FUNCTION

### 3.1 Using AWS Console

1. Go to: https://console.aws.amazon.com/lambda/
2. Click **"Create function"**
3. Choose **"Author from scratch"**
4. Configuration:
   - **Function name:** `prachar-ai-backend`
   - **Runtime:** Python 3.11
   - **Architecture:** x86_64
   - **Execution role:** Use existing role → `PracharAI-Lambda-ExecutionRole`
5. Click **"Create function"**

### 3.2 Using AWS CLI

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create Lambda function
aws lambda create-function \
  --function-name prachar-ai-backend \
  --runtime python3.11 \
  --role arn:aws:iam::${ACCOUNT_ID}:role/PracharAI-Lambda-ExecutionRole \
  --handler aws_lambda_handler.lambda_handler \
  --zip-file fileb://prachar-ai-lambda.zip \
  --timeout 300 \
  --memory-size 512 \
  --region us-east-1
```

---

## 🔐 STEP 4: CONFIGURE ENVIRONMENT VARIABLES

### 4.1 Using AWS Console

1. Go to Lambda function → **Configuration** → **Environment variables**
2. Click **"Edit"**
3. Add variables:

```
DYNAMODB_TABLE          = prachar-ai-campaigns
S3_BUCKET               = prachar-ai-assets
AWS_REGION              = us-east-1
GUARDRAIL_ID            = (optional - your guardrail ID)
GUARDRAIL_VERSION       = DRAFT
```

### 4.2 Using AWS CLI

```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment "Variables={
    DYNAMODB_TABLE=prachar-ai-campaigns,
    S3_BUCKET=prachar-ai-assets,
    AWS_REGION=us-east-1,
    GUARDRAIL_VERSION=DRAFT
  }"
```

---

## 🌐 STEP 5: CREATE API GATEWAY

### 5.1 Create REST API

```bash
# Create API
API_ID=$(aws apigateway create-rest-api \
  --name "Prachar.ai API" \
  --description "API for Prachar.ai campaign generation" \
  --endpoint-configuration types=REGIONAL \
  --query 'id' \
  --output text)

echo "API ID: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' \
  --output text)

# Create /generate resource
RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part generate \
  --query 'id' \
  --output text)

# Create POST method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE

# Create OPTIONS method (CORS)
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method OPTIONS \
  --authorization-type NONE

# Integrate with Lambda
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:${ACCOUNT_ID}:function:prachar-ai-backend/invocations

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
  --function-name prachar-ai-backend \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:${ACCOUNT_ID}:${API_ID}/*/*"

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod

echo "API Endpoint: https://${API_ID}.execute-api.us-east-1.amazonaws.com/prod/generate"
```

---

## 🧪 STEP 6: TEST THE DEPLOYMENT

### 6.1 Test via AWS Console

1. Go to Lambda function → **Test** tab
2. Create new test event:

```json
{
  "httpMethod": "POST",
  "body": "{\"goal\": \"Python AI Workshop for college students\", \"user_id\": \"test-user-123\"}"
}
```

3. Click **"Test"**
4. Check response and CloudWatch logs

### 6.2 Test via API Gateway

```bash
# Get your API endpoint
API_ENDPOINT="https://${API_ID}.execute-api.us-east-1.amazonaws.com/prod/generate"

# Test campaign generation
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Python AI Workshop for college students",
    "user_id": "test-user-123"
  }'
```

### 6.3 Expected Response

```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "test-user-123",
  "goal": "Python AI Workshop for college students",
  "plan": {
    "hook": "Arre Python enthusiasts!",
    "offer": "Master AI with hands-on workshop",
    "cta": "Register now - limited seats!"
  },
  "captions": [
    "🐍 Python AI Workshop - Yeh opportunity miss mat karo! 🤖✨",
    "Arre bhai, AI seekhna hai? Join our Python workshop! 💪🔥",
    "College students, Python + AI = Your future! Register now! 🚀🇮🇳"
  ],
  "image_url": "https://prachar-ai-assets.s3.amazonaws.com/campaigns/550e8400-e29b-41d4-a716-446655440000.png",
  "status": "completed",
  "created_at": "2026-02-28T10:30:00.000000"
}
```

---

## 📊 STEP 7: MONITORING & DEBUGGING

### 7.1 View CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/prachar-ai-backend --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/prachar-ai-backend \
  --filter-pattern "ERROR"
```

### 7.2 Check DynamoDB Records

```bash
# Scan table
aws dynamodb scan --table-name prachar-ai-campaigns

# Query by user
aws dynamodb query \
  --table-name prachar-ai-campaigns \
  --index-name user-index \
  --key-condition-expression "user_id = :uid" \
  --expression-attribute-values '{":uid":{"S":"test-user-123"}}'
```

### 7.3 Check S3 Images

```bash
# List generated images
aws s3 ls s3://prachar-ai-assets/campaigns/

# Download an image
aws s3 cp s3://prachar-ai-assets/campaigns/[IMAGE_ID].png ./test-image.png
```

---

## 🔐 STEP 8: ADD COGNITO AUTHENTICATION (Optional)

### 8.1 Create Cognito User Pool

```bash
# Create user pool
USER_POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name prachar-ai-users \
  --auto-verified-attributes email \
  --query 'UserPool.Id' \
  --output text)

# Create app client
CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-name prachar-ai-web \
  --query 'UserPoolClient.ClientId' \
  --output text)

echo "User Pool ID: $USER_POOL_ID"
echo "Client ID: $CLIENT_ID"
```

### 8.2 Add Cognito Authorizer to API Gateway

```bash
# Create authorizer
AUTHORIZER_ID=$(aws apigateway create-authorizer \
  --rest-api-id $API_ID \
  --name CognitoAuthorizer \
  --type COGNITO_USER_POOLS \
  --provider-arns arn:aws:cognito-idp:us-east-1:${ACCOUNT_ID}:userpool/${USER_POOL_ID} \
  --identity-source method.request.header.Authorization \
  --query 'id' \
  --output text)

# Update POST method to use authorizer
aws apigateway update-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --patch-operations op=replace,path=/authorizationType,value=COGNITO_USER_POOLS \
    op=replace,path=/authorizerId,value=$AUTHORIZER_ID

# Redeploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

---

## 🚀 STEP 9: PERFORMANCE OPTIMIZATION

### 9.1 Increase Lambda Resources

```bash
# Increase memory (also increases CPU)
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --memory-size 1024 \
  --timeout 300
```

### 9.2 Enable Lambda Provisioned Concurrency

```bash
# Publish version
VERSION=$(aws lambda publish-version \
  --function-name prachar-ai-backend \
  --query 'Version' \
  --output text)

# Set provisioned concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name prachar-ai-backend \
  --provisioned-concurrent-executions 2 \
  --qualifier $VERSION
```

---

## 📝 STEP 10: UPDATE FRONTEND

Update your Next.js frontend to use the new API endpoint:

```typescript
// prachar-ai/src/app/api/generate/route.ts

const API_ENDPOINT = process.env.NEXT_PUBLIC_API_ENDPOINT || 
  'https://[YOUR_API_ID].execute-api.us-east-1.amazonaws.com/prod/generate';

export async function POST(request: Request) {
  const body = await request.json();
  
  const response = await fetch(API_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // Add Authorization header if using Cognito
      // 'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(body)
  });
  
  return response;
}
```

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] DynamoDB table created (`prachar-ai-campaigns`)
- [ ] S3 bucket created (`prachar-ai-assets`)
- [ ] IAM role created with proper permissions
- [ ] Lambda function deployed with handler code
- [ ] Environment variables configured
- [ ] API Gateway created and deployed
- [ ] Lambda permissions granted to API Gateway
- [ ] Test successful via API Gateway
- [ ] CloudWatch logs verified
- [ ] DynamoDB records verified
- [ ] S3 images verified
- [ ] Frontend updated with API endpoint
- [ ] (Optional) Cognito authentication configured
- [ ] (Optional) Bedrock Guardrails configured

---

## 🐛 TROUBLESHOOTING

### Issue: "Module not found: strands"

**Solution:** Install Strands SDK in deployment package or create Lambda layer

```bash
pip install --target . strands-sdk
```

### Issue: "Access Denied" errors

**Solution:** Check IAM role has Bedrock, DynamoDB, and S3 permissions

```bash
aws iam list-attached-role-policies --role-name PracharAI-Lambda-ExecutionRole
```

### Issue: Lambda timeout

**Solution:** Increase timeout to 300 seconds (5 minutes)

```bash
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --timeout 300
```

### Issue: CORS errors in browser

**Solution:** Verify CORS headers in Lambda response and OPTIONS method in API Gateway

---

## 📚 ADDITIONAL RESOURCES

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Strands SDK Documentation](https://github.com/strands-ai/strands-sdk)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)

---

**Status:** 🚀 Ready for Production Deployment  
**Estimated Deployment Time:** 30-45 minutes  
**Cost:** ~$0.01 per campaign generation (Bedrock + Lambda + DynamoDB + S3)
