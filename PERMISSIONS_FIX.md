# DynamoDB Permissions Fix

## Issue
Lambda function was getting AccessDeniedException when trying to:
- Query conversation history from DynamoDB
- Save conversations to DynamoDB

Error:
```
User: arn:aws:sts::482548785371:assumed-role/whatsapp-llama-bot-role-9t42wmrl/whatsapp-llama-bot 
is not authorized to perform: dynamodb:Query on resource: 
arn:aws:dynamodb:ap-south-1:482548785371:table/kisaanmitra-conversations
```

## Root Cause
The Lambda IAM role (whatsapp-llama-bot-role-9t42wmrl) only had:
- AWSLambdaBasicExecutionRole (CloudWatch Logs)
- AmazonBedrockFullAccess (Bedrock models)
- BedrockCrossRegionAccess (Custom inline policy)

Missing: DynamoDB permissions

## Fix Applied
Added inline policy "DynamoDBAccess" to the Lambda role with permissions:
- dynamodb:GetItem
- dynamodb:PutItem
- dynamodb:Query
- dynamodb:Scan
- dynamodb:UpdateItem
- dynamodb:DeleteItem

Resource pattern: `arn:aws:dynamodb:ap-south-1:482548785371:table/kisaanmitra-*`

This covers all KisaanMitra tables:
- kisaanmitra-conversations
- kisaanmitra-market-data
- kisaanmitra-finance
- kisaanmitra-user-preferences

## Verification
```bash
aws iam list-role-policies --role-name whatsapp-llama-bot-role-9t42wmrl
```

Output:
```json
{
    "PolicyNames": [
        "BedrockCrossRegionAccess",
        "DynamoDBAccess"
    ]
}
```

## Result
✅ Conversation memory now works
✅ No more AccessDeniedException errors
✅ Bot can remember previous messages
✅ Context-aware responses enabled

## Testing
Send multiple messages to the bot:
1. "Hi" → Bot responds with greeting
2. "I want to grow tomato" → Bot asks for details
3. "1 acre in pune" → Bot generates budget using context from previous message

The bot now remembers the conversation flow!
