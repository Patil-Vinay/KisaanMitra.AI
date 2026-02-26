#!/usr/bin/env python3
"""Clear all user data from DynamoDB tables"""

import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

# Tables
tables = {
    'profiles': dynamodb.Table('kisaanmitra-user-profiles'),
    'onboarding': dynamodb.Table('kisaanmitra-onboarding'),
    'conversations': dynamodb.Table('kisaanmitra-conversations')
}

def clear_table(table_name, table):
    """Clear all items from a table"""
    print(f"\nClearing {table_name}...")
    
    try:
        # Scan and delete all items
        response = table.scan()
        items = response.get('Items', [])
        
        if not items:
            print(f"  ✓ {table_name} is already empty")
            return
        
        # Get key schema
        key_schema = table.key_schema
        key_names = [key['AttributeName'] for key in key_schema]
        
        # Delete each item
        count = 0
        for item in items:
            key = {k: item[k] for k in key_names if k in item}
            table.delete_item(Key=key)
            count += 1
        
        print(f"  ✓ Deleted {count} items from {table_name}")
        
    except ClientError as e:
        print(f"  ✗ Error clearing {table_name}: {e}")

def main():
    print("=" * 50)
    print("Clearing All DynamoDB Tables")
    print("=" * 50)
    
    for name, table in tables.items():
        clear_table(name, table)
    
    print("\n" + "=" * 50)
    print("Verification")
    print("=" * 50)
    
    for name, table in tables.items():
        count = table.scan(Select='COUNT')['Count']
        print(f"{name}: {count} items")
    
    print("\n✅ All data cleared!")

if __name__ == "__main__":
    main()
