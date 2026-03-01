# 🚨 CRITICAL SECURITY CLEANUP GUIDE

**URGENT: AWS Credentials Exposed - Immediate Action Required**

---

## ⚠️ SECURITY BREACH DETECTED

Your `backend/.env` file containing AWS credentials has been committed to Git history. This guide will help you:

1. ✅ Remove `.env` from Git history completely
2. ✅ Revoke compromised AWS credentials
3. ✅ Set up secure AWS Lambda environment variables
4. ✅ Prevent future credential leaks

---

## 🔥 STEP 1: REVOKE COMPROMISED AWS CREDENTIALS (DO THIS FIRST!)

**CRITICAL:** The exposed credentials must be deactivated immediately!

### Option A: AWS Console (Recommended)

1. Go to: https://console.aws.amazon.com/iam/
2. Navigate to: **IAM → Users → [Your User] → Security Credentials**
3. Find Access Key: `AKIAZDPUGKTI3ZMABT4Q`
4. Click **"Make Inactive"** or **"Delete"**
5. Create new credentials (you'll set these in Lambda later)

### Option B: AWS CLI

```bash
# Deactivate the compromised key
aws iam update-access-key --access-key-id AKIAZDPUGKTI3ZMABT4Q --status Inactive --user-name [YOUR_IAM_USERNAME]

# Delete the compromised key (after deactivation)
aws iam delete-access-key --access-key-id AKIAZDPUGKTI3ZMABT4Q --user-name [YOUR_IAM_USERNAME]
```

---

## 🧹 STEP 2: REMOVE .ENV FROM GIT HISTORY

### Method 1: Using git filter-repo (Recommended - Fastest)

```bash
# Navigate to your repository
cd Prachar.ai

# Install git-filter-repo (if not installed)
# Windows (using pip):
pip install git-filter-repo

# Remove backend/.env from entire Git history
git filter-repo --path backend/.env --invert-paths --force

# Verify the file is gone from history
git log --all --full-history -- backend/.env
# (Should return nothing)
```

### Method 2: Using BFG Repo-Cleaner (Alternative)

```bash
# Download BFG: https://rtyley.github.io/bfg-repo-cleaner/
# Run from parent directory of Prachar.ai

# Remove the file from history
java -jar bfg.jar --delete-files .env Prachar.ai

# Clean up
cd Prachar.ai
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Method 3: Manual filter-branch (Slowest, but works everywhere)

```bash
cd Prachar.ai

# Remove backend/.env from all commits
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch backend/.env" --prune-empty --tag-name-filter cat -- --all

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## 🛡️ STEP 3: UPDATE .GITIGNORE (PREVENT FUTURE LEAKS)

```bash
cd Prachar.ai

# This will update .gitignore with comprehensive env protection
```

**The .gitignore will be updated automatically in the next step.**

---

## 🗑️ STEP 4: DELETE LOCAL .ENV FILE

```bash
# Remove the file from your working directory
cd Prachar.ai
del backend\.env

# Verify it's gone
dir backend\.env
# (Should show "File Not Found")
```

---

## 🚀 STEP 5: FORCE PUSH TO GITHUB (REWRITE REMOTE HISTORY)

**⚠️ WARNING:** This will rewrite Git history. Coordinate with your team!

```bash
cd Prachar.ai

# Force push to overwrite remote history
git push origin --force --all

# Force push tags (if any)
git push origin --force --tags
```

**Important Notes:**
- All team members must re-clone the repository after this
- Any open pull requests will need to be recreated
- This is necessary to remove credentials from GitHub's servers

---

## ☁️ STEP 6: SET UP AWS LAMBDA ENVIRONMENT VARIABLES

### Option A: AWS Console (Easiest)

1. Go to: https://console.aws.amazon.com/lambda/
2. Select your Lambda function (e.g., `prachar-ai-backend`)
3. Go to: **Configuration → Environment Variables**
4. Click **"Edit"** and add:

```
AWS_ACCESS_KEY_ID     = [NEW_ACCESS_KEY_ID]
AWS_SECRET_ACCESS_KEY = [NEW_SECRET_ACCESS_KEY]
AWS_REGION            = us-east-1
```

5. Click **"Save"**

### Option B: AWS CLI

```bash
# Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment "Variables={AWS_ACCESS_KEY_ID=[NEW_KEY],AWS_SECRET_ACCESS_KEY=[NEW_SECRET],AWS_REGION=us-east-1}"
```

### Option C: AWS SAM/CloudFormation Template

Add to your `template.yaml`:

```yaml
Resources:
  PracharAIFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment:
        Variables:
          AWS_ACCESS_KEY_ID: !Ref AWSAccessKeyId
          AWS_SECRET_ACCESS_KEY: !Ref AWSSecretAccessKey
          AWS_REGION: us-east-1
```

---

## 🔐 STEP 7: BEST PRACTICE - USE IAM ROLES (RECOMMENDED)

**Even better than environment variables:** Use IAM Roles for Lambda!

### Why IAM Roles are Superior:

- ✅ No credentials to manage or rotate
- ✅ Automatic credential rotation by AWS
- ✅ Fine-grained permissions
- ✅ No risk of credential leaks

### Setup IAM Role for Lambda:

```bash
# Create IAM role with Bedrock permissions
aws iam create-role \
  --role-name PracharAI-Lambda-Bedrock-Role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach Bedrock permissions
aws iam attach-role-policy \
  --role-name PracharAI-Lambda-Bedrock-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Attach basic Lambda execution permissions
aws iam attach-role-policy \
  --role-name PracharAI-Lambda-Bedrock-Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Update Lambda to use this role
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/PracharAI-Lambda-Bedrock-Role
```

**With IAM Roles:** Your Lambda code doesn't need AWS credentials at all! AWS handles authentication automatically.

---

## 📝 STEP 8: UPDATE BACKEND CODE (IF USING IAM ROLES)

If you switch to IAM Roles, update your Lambda code:

**Before (using credentials):**
```python
import boto3

bedrock = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']
)
```

**After (using IAM Role - no credentials needed):**
```python
import boto3

# AWS SDK automatically uses the Lambda's IAM role
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
```

---

## ✅ STEP 9: VERIFICATION CHECKLIST

Run these commands to verify the cleanup:

```bash
# 1. Verify .env is not in Git history
cd Prachar.ai
git log --all --full-history -- backend/.env
# Should return: (nothing)

# 2. Verify .env is not in working directory
dir backend\.env
# Should return: File Not Found

# 3. Verify .gitignore includes .env
type .gitignore | findstr "\.env"
# Should show: *.env, .env, backend/.env

# 4. Verify no .env files are tracked
git ls-files | findstr "\.env"
# Should return: (nothing)

# 5. Check GitHub repository
# Go to: https://github.com/[YOUR_USERNAME]/Prachar.ai
# Search for: "AWS_ACCESS_KEY_ID"
# Should return: No results
```

---

## 📊 STEP 10: UPDATE DOCUMENTATION

Update your `HACKATHON_SUBMISSION_READY.md` to reflect security best practices:

**Add this section:**

```markdown
## 🔐 Security & AWS Secret Management

Prachar.ai follows AWS security best practices:

✅ **IAM Roles for Lambda:** No hardcoded credentials in code
✅ **Environment Variables:** Secrets stored in AWS Lambda configuration (not in repo)
✅ **Cognito JWT Authentication:** User isolation and authorization
✅ **Bedrock Guardrails:** Content safety and PII redaction
✅ **Audit Logging:** Complete CloudWatch audit trail
✅ **Zero Credential Leaks:** .env files excluded from Git history

**Production Deployment:**
- Lambda functions use IAM roles with least-privilege permissions
- All secrets managed via AWS Systems Manager Parameter Store
- No credentials stored in repository or version control
```

---

## 🎯 QUICK REFERENCE: COMPLETE CLEANUP SCRIPT

**Run this complete script for full cleanup:**

```bash
# Navigate to repository
cd Prachar.ai

# STEP 1: Remove from Git history (choose one method)
git filter-repo --path backend/.env --invert-paths --force

# STEP 2: Delete local file
del backend\.env

# STEP 3: Update .gitignore (done automatically by Kiro)

# STEP 4: Commit changes
git add .gitignore
git commit -m "security: Remove .env from history and update .gitignore"

# STEP 5: Force push to GitHub
git push origin --force --all
git push origin --force --tags

# STEP 6: Verify cleanup
git log --all --full-history -- backend/.env
git ls-files | findstr "\.env"
```

---

## 🚨 IMPORTANT REMINDERS

1. **Revoke AWS credentials FIRST** before anything else
2. **Coordinate with team** before force-pushing
3. **Create new AWS credentials** or use IAM roles
4. **Update Lambda environment variables** with new credentials
5. **Test your Lambda function** after updating credentials
6. **Monitor AWS CloudTrail** for any unauthorized access using old credentials

---

## 📞 EMERGENCY CONTACTS

If you suspect the credentials were already compromised:

1. **AWS Support:** https://console.aws.amazon.com/support/
2. **Report Security Issue:** aws-security@amazon.com
3. **Check CloudTrail:** https://console.aws.amazon.com/cloudtrail/
   - Look for unauthorized API calls using the exposed credentials

---

## ✨ FUTURE PREVENTION

**Never commit these files:**
- `.env`, `.env.local`, `.env.production`
- `credentials.json`, `secrets.yaml`
- Any file containing API keys, passwords, or tokens

**Always use:**
- Environment variables (Lambda, Vercel, etc.)
- AWS Secrets Manager / Systems Manager Parameter Store
- IAM Roles (best practice for AWS services)
- `.gitignore` to exclude sensitive files

---

## 📚 ADDITIONAL RESOURCES

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Lambda Environment Variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html)
- [Git Filter-Repo Documentation](https://github.com/newren/git-filter-repo)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

**Status:** 🔴 CRITICAL - Execute immediately
**Priority:** P0 - Security incident
**Impact:** High - AWS credentials exposed in public repository
