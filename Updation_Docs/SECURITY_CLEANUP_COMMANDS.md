# 🚨 SECURITY CLEANUP - QUICK COMMAND REFERENCE

**CRITICAL: Execute these commands immediately to remove exposed AWS credentials**

---

## ⚡ QUICK START (5 Minutes)

### STEP 1: REVOKE AWS CREDENTIALS (DO THIS FIRST!)

```bash
# Option A: AWS Console (Easiest)
# Go to: https://console.aws.amazon.com/iam/
# Navigate to: IAM → Users → [Your User] → Security Credentials
# Find: AKIAZDPUGKTI3ZMABT4Q
# Click: "Make Inactive" or "Delete"

# Option B: AWS CLI
aws iam update-access-key --access-key-id AKIAZDPUGKTI3ZMABT4Q --status Inactive --user-name [YOUR_IAM_USERNAME]
aws iam delete-access-key --access-key-id AKIAZDPUGKTI3ZMABT4Q --user-name [YOUR_IAM_USERNAME]
```

---

### STEP 2: REMOVE .ENV FROM GIT HISTORY

**Method 1: git filter-repo (Recommended - Fastest)**

```bash
# Install git-filter-repo
pip install git-filter-repo

# Navigate to repository
cd Prachar.ai

# Remove backend/.env from entire Git history
git filter-repo --path backend/.env --invert-paths --force

# Verify removal
git log --all --full-history -- backend/.env
# Should return nothing
```

**Method 2: Manual filter-branch (If filter-repo not available)**

```bash
cd Prachar.ai

# Remove from all commits
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch backend/.env" --prune-empty --tag-name-filter cat -- --all

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

### STEP 3: FORCE PUSH TO GITHUB

```bash
cd Prachar.ai

# Force push to overwrite remote history
git push origin --force --all

# Force push tags (if any)
git push origin --force --tags
```

**⚠️ WARNING:** This rewrites Git history. Team members must re-clone!

---

### STEP 4: SET UP AWS LAMBDA ENVIRONMENT VARIABLES

**Option A: AWS Console**

1. Go to: https://console.aws.amazon.com/lambda/
2. Select: `prachar-ai-backend` (or your Lambda function name)
3. Go to: Configuration → Environment Variables
4. Click: "Edit"
5. Add:
   - `AWS_ACCESS_KEY_ID` = [NEW_ACCESS_KEY_ID]
   - `AWS_SECRET_ACCESS_KEY` = [NEW_SECRET_ACCESS_KEY]
   - `AWS_REGION` = us-east-1
6. Click: "Save"

**Option B: AWS CLI**

```bash
# Create new IAM user and get credentials first
aws iam create-access-key --user-name [YOUR_IAM_USERNAME]

# Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment "Variables={AWS_ACCESS_KEY_ID=[NEW_KEY],AWS_SECRET_ACCESS_KEY=[NEW_SECRET],AWS_REGION=us-east-1}"
```

---

### STEP 5: VERIFY CLEANUP

```bash
cd Prachar.ai

# 1. Verify .env is not in Git history
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
```

---

## 🔐 BEST PRACTICE: USE IAM ROLES (RECOMMENDED)

**Why IAM Roles are Better:**
- No credentials to manage
- Automatic rotation by AWS
- No risk of leaks
- Fine-grained permissions

### Setup IAM Role for Lambda

```bash
# 1. Create IAM role
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

# 2. Attach Bedrock permissions
aws iam attach-role-policy \
  --role-name PracharAI-Lambda-Bedrock-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# 3. Attach Lambda execution permissions
aws iam attach-role-policy \
  --role-name PracharAI-Lambda-Bedrock-Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# 4. Get your AWS Account ID
aws sts get-caller-identity --query Account --output text

# 5. Update Lambda to use this role
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/PracharAI-Lambda-Bedrock-Role
```

### Update Lambda Code (If Using IAM Roles)

**Before:**
```python
import boto3
import os

bedrock = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']
)
```

**After:**
```python
import boto3

# AWS SDK automatically uses the Lambda's IAM role
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
```

---

## 📊 VERIFICATION CHECKLIST

Run these commands to confirm cleanup:

```bash
# Navigate to repository
cd Prachar.ai

# Check 1: No .env in Git history
git log --all --full-history -- backend/.env
# Expected: (nothing)

# Check 2: No .env in working directory
dir backend\.env
# Expected: File Not Found

# Check 3: .gitignore includes .env
type .gitignore | findstr "\.env"
# Expected: Multiple .env patterns

# Check 4: No .env files tracked
git ls-files | findstr "\.env"
# Expected: (nothing)

# Check 5: GitHub search
# Go to: https://github.com/[YOUR_USERNAME]/Prachar.ai
# Search: "AWS_ACCESS_KEY_ID"
# Expected: No results
```

---

## 🚨 EMERGENCY CHECKLIST

If credentials were already compromised:

1. **Check CloudTrail for unauthorized access:**
   ```bash
   aws cloudtrail lookup-events \
     --lookup-attributes AttributeKey=Username,AttributeValue=[YOUR_IAM_USERNAME] \
     --max-results 50
   ```

2. **Review recent API calls:**
   - Go to: https://console.aws.amazon.com/cloudtrail/
   - Check for suspicious activity using the exposed credentials

3. **Contact AWS Support:**
   - https://console.aws.amazon.com/support/
   - Report potential credential compromise

4. **Enable AWS GuardDuty (if not already):**
   ```bash
   aws guardduty create-detector --enable
   ```

---

## 📝 COMPLETE CLEANUP SCRIPT

**Copy and run this complete script:**

```bash
# ============================================
# PRACHAR.AI SECURITY CLEANUP SCRIPT
# ============================================

# Navigate to repository
cd Prachar.ai

# STEP 1: Remove from Git history
echo "Removing .env from Git history..."
git filter-repo --path backend/.env --invert-paths --force

# STEP 2: Update .gitignore (already done by Kiro)
echo ".gitignore updated"

# STEP 3: Commit changes
echo "Committing security updates..."
git add .gitignore
git commit -m "security: Remove .env from history and update .gitignore"

# STEP 4: Force push to GitHub
echo "Force pushing to GitHub..."
git push origin --force --all
git push origin --force --tags

# STEP 5: Verify cleanup
echo "Verifying cleanup..."
echo "Checking Git history for .env..."
git log --all --full-history -- backend/.env

echo "Checking for tracked .env files..."
git ls-files | findstr "\.env"

echo "============================================"
echo "CLEANUP COMPLETE!"
echo "============================================"
echo ""
echo "NEXT STEPS:"
echo "1. Revoke old AWS credentials in IAM Console"
echo "2. Create new credentials or set up IAM role"
echo "3. Update Lambda environment variables"
echo "4. Test Lambda function with new credentials"
echo "============================================"
```

---

## 🎯 POST-CLEANUP ACTIONS

### 1. Create New AWS Credentials

```bash
# Create new access key
aws iam create-access-key --user-name [YOUR_IAM_USERNAME]

# Save the output securely (not in Git!)
```

### 2. Update Lambda Environment Variables

```bash
# Update with new credentials
aws lambda update-function-configuration \
  --function-name prachar-ai-backend \
  --environment "Variables={AWS_ACCESS_KEY_ID=[NEW_KEY],AWS_SECRET_ACCESS_KEY=[NEW_SECRET],AWS_REGION=us-east-1}"
```

### 3. Test Lambda Function

```bash
# Invoke Lambda to test
aws lambda invoke \
  --function-name prachar-ai-backend \
  --payload '{"test": true}' \
  response.json

# Check response
type response.json
```

### 4. Monitor CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/prachar-ai-backend --follow
```

---

## 📚 ADDITIONAL RESOURCES

- **Full Guide:** `SECURITY_CLEANUP_GUIDE.md`
- **AWS IAM Best Practices:** https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Lambda Environment Variables:** https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html
- **Git Filter-Repo:** https://github.com/newren/git-filter-repo

---

## ✅ STATUS

- [x] `.env` file deleted from working directory
- [x] `.gitignore` updated with comprehensive patterns
- [ ] **TODO:** Remove `.env` from Git history (run commands above)
- [ ] **TODO:** Revoke old AWS credentials
- [ ] **TODO:** Force push to GitHub
- [ ] **TODO:** Set up new credentials or IAM role
- [ ] **TODO:** Update Lambda environment variables
- [ ] **TODO:** Test Lambda function

---

**Priority:** 🔴 P0 - CRITICAL  
**Impact:** High - AWS credentials exposed  
**Time to Fix:** 5-10 minutes  
**Status:** Ready to execute
