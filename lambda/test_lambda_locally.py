"""
Local test script for Lambda handler
Simulates AWS Lambda environment locally before deployment
"""

import sys
import os
from unittest.mock import MagicMock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Mock AWS environment variables from .env
from config import Config

os.environ['OBP_BASE_URL'] = Config.OBP_BASE_URL
os.environ['OBP_API_VERSION'] = Config.OBP_API_VERSION
os.environ['OBP_USERNAME'] = Config.OBP_USERNAME
os.environ['OBP_PASSWORD'] = Config.OBP_PASSWORD
os.environ['OBP_CONSUMER_KEY'] = Config.OBP_CONSUMER_KEY
os.environ['OBP_DIRECTLOGIN_ENDPOINT'] = Config.OBP_DIRECTLOGIN_ENDPOINT
os.environ['S3_BUCKET_NAME'] = 'local-test-bucket'

# Mock S3 client BEFORE importing lambda_handler
def mock_put_object(Bucket, Key, Body, ContentType):
    """Mock S3 put_object - saves to local file instead"""
    local_file = f"local_test_{Key.replace('/', '_')}"
    with open(local_file, 'w') as f:
        f.write(Body)
    print(f"[LOCAL TEST] Saved to: {local_file}")
    return {'ETag': 'mock-etag'}

# Create mock S3 client
mock_s3_client = MagicMock()
mock_s3_client.put_object = mock_put_object

# Patch boto3.client to return our mock
import boto3
original_boto3_client = boto3.client
boto3.client = lambda service_name, **kwargs: mock_s3_client if service_name == 's3' else original_boto3_client(service_name, **kwargs)

# NOW import lambda handler (after patching boto3)
from lambda_handler import lambda_handler

def main():
    """Run Lambda handler locally"""
    print("=" * 70)
    print("LOCAL LAMBDA TEST")
    print("=" * 70)
    print("\nThis simulates AWS Lambda execution locally")
    print("S3 uploads will be saved as local files instead\n")
    
    # Mock Lambda event and context
    event = {}
    context = MagicMock()
    context.function_name = 'local-test'
    context.request_id = 'local-request-id'
    
    try:
        # Execute Lambda handler
        result = lambda_handler(event, context)
        
        print("\n" + "=" * 70)
        print("LAMBDA EXECUTION RESULT")
        print("=" * 70)
        print(f"Status Code: {result['statusCode']}")
        print(f"Response Body:")
        print(result['body'])
        
        if result['statusCode'] == 200:
            print("\n[SUCCESS] Lambda handler executed successfully!")
            print("\nLocal test files created:")
            print("  - local_test_raw_banks_*.csv")
            print("  - local_test_raw_accounts_*.csv")
            print("  - local_test_raw_transactions_*.csv")
        else:
            print("\n[ERROR] Lambda handler failed")
            
    except Exception as e:
        print(f"\n[ERROR] Lambda execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

