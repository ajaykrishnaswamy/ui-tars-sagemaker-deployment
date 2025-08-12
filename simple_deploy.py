#!/usr/bin/env python3
"""
Simplified deployment script for UI-TARS model using boto3 directly
"""

import boto3
import json
import time

def create_sagemaker_model(model_name, execution_role, region='us-east-1'):
    """Create a SageMaker model for UI-TARS using Hugging Face container"""
    
    sagemaker_client = boto3.client('sagemaker', region_name=region)
    
    # Hugging Face inference container URI for the region
    container_uris = {
        'us-east-1': '763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04',
        'us-west-2': '763104351884.dkr.ecr.us-west-2.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04',
        'eu-west-1': '763104351884.dkr.ecr.eu-west-1.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04'
    }
    
    image_uri = container_uris.get(region, container_uris['us-east-1'])
    
    # Environment variables for Hugging Face model
    environment = {
        'HF_MODEL_ID': 'ByteDance-Seed/UI-TARS-1.5-7B',
        'HF_TASK': 'image-to-text',
        'SAGEMAKER_CONTAINER_LOG_LEVEL': '20',
        'SAGEMAKER_REGION': region
    }
    
    try:
        response = sagemaker_client.create_model(
            ModelName=model_name,
            PrimaryContainer={
                'Image': image_uri,
                'Environment': environment
            },
            ExecutionRoleArn=execution_role
        )
        
        print(f"✅ Model created: {model_name}")
        return response['ModelArn']
        
    except Exception as e:
        print(f"❌ Error creating model: {str(e)}")
        return None

def create_endpoint_config(config_name, model_name, instance_type='ml.g5.2xlarge'):
    """Create endpoint configuration"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    try:
        response = sagemaker_client.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InitialInstanceCount': 1,
                    'InstanceType': instance_type,
                    'InitialVariantWeight': 1
                }
            ]
        )
        
        print(f"✅ Endpoint config created: {config_name}")
        return response['EndpointConfigArn']
        
    except Exception as e:
        print(f"❌ Error creating endpoint config: {str(e)}")
        return None

def create_endpoint(endpoint_name, config_name):
    """Create SageMaker endpoint"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    try:
        response = sagemaker_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )
        
        print(f"✅ Endpoint creation started: {endpoint_name}")
        return response['EndpointArn']
        
    except Exception as e:
        print(f"❌ Error creating endpoint: {str(e)}")
        return None

def wait_for_endpoint(endpoint_name, max_wait_time=1800):  # 30 minutes
    """Wait for endpoint to be in service"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    print(f"⏳ Waiting for endpoint {endpoint_name} to be in service...")
    print("This may take 10-15 minutes...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            status = response['EndpointStatus']
            
            if status == 'InService':
                print(f"✅ Endpoint {endpoint_name} is now in service!")
                return True
            elif status == 'Failed':
                failure_reason = response.get('FailureReason', 'Unknown')
                print(f"❌ Endpoint failed: {failure_reason}")
                return False
            else:
                print(f"🔄 Status: {status}")
                time.sleep(30)
                
        except Exception as e:
            print(f"❌ Error checking endpoint status: {str(e)}")
            return False
    
    print(f"⏰ Timeout waiting for endpoint")
    return False

def test_endpoint(endpoint_name):
    """Test the deployed endpoint"""
    
    runtime_client = boto3.client('sagemaker-runtime')
    
    test_payload = {
        "inputs": "Describe what you see and suggest the next action",
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7
        }
    }
    
    try:
        response = runtime_client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps(test_payload)
        )
        
        result = json.loads(response['Body'].read().decode())
        print(f"✅ Test successful!")
        print(f"Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("Note: UI-TARS may require image inputs for full functionality")
        return False

def main():
    """Main deployment function"""
    
    print("=== UI-TARS Direct Deployment ===\n")
    
    # Configuration
    timestamp = int(time.time())
    model_name = f"ui-tars-model-{timestamp}"
    config_name = f"ui-tars-config-{timestamp}"
    endpoint_name = f"ui-tars-endpoint-{timestamp}"
    
    # Get execution role from user
    execution_role = input("Enter your SageMaker execution role ARN: ").strip()
    if not execution_role:
        print("❌ Execution role is required!")
        return
    
    # Get AWS region
    session = boto3.Session()
    region = session.region_name or 'us-east-1'
    print(f"Using region: {region}")
    
    # Step 1: Create model
    print(f"\n1️⃣ Creating SageMaker model...")
    model_arn = create_sagemaker_model(model_name, execution_role, region)
    if not model_arn:
        return
    
    # Step 2: Create endpoint configuration
    print(f"\n2️⃣ Creating endpoint configuration...")
    config_arn = create_endpoint_config(config_name, model_name)
    if not config_arn:
        return
    
    # Step 3: Create endpoint
    print(f"\n3️⃣ Creating endpoint...")
    endpoint_arn = create_endpoint(endpoint_name, config_name)
    if not endpoint_arn:
        return
    
    # Step 4: Wait for endpoint
    print(f"\n4️⃣ Waiting for endpoint to be ready...")
    if not wait_for_endpoint(endpoint_name):
        return
    
    # Step 5: Test endpoint
    print(f"\n5️⃣ Testing endpoint...")
    test_endpoint(endpoint_name)
    
    # Summary
    print(f"\n🎉 Deployment completed successfully!")
    print(f"Endpoint name: {endpoint_name}")
    print(f"Model: ByteDance-Seed/UI-TARS-1.5-7B")
    print(f"Instance type: ml.g5.2xlarge")
    
    print(f"\n💰 Remember to delete the endpoint when done:")
    print(f"aws sagemaker delete-endpoint --endpoint-name {endpoint_name}")

if __name__ == "__main__":
    main()
