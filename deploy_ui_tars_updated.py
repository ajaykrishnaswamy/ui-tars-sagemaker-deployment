#!/usr/bin/env python3
"""
Updated deployment script for UI-TARS model with newer Transformers version
"""

import boto3
import json
import time

def create_sagemaker_model_updated(model_name, execution_role, region='us-east-1'):
    """Create a SageMaker model for UI-TARS using newer Hugging Face container"""
    
    sagemaker_client = boto3.client('sagemaker', region_name=region)
    
    # Use the latest Hugging Face inference container with newer Transformers
    container_uris = {
        'us-east-1': '763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.44.0-gpu-py310-cu121-ubuntu20.04',
        'us-west-2': '763104351884.dkr.ecr.us-west-2.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.44.0-gpu-py310-cu121-ubuntu20.04',
        'eu-west-1': '763104351884.dkr.ecr.eu-west-1.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.44.0-gpu-py310-cu121-ubuntu20.04'
    }
    
    image_uri = container_uris.get(region, container_uris['us-east-1'])
    
    # Environment variables for Hugging Face model
    environment = {
        'HF_MODEL_ID': 'ByteDance-Seed/UI-TARS-1.5-7B',
        'HF_TASK': 'image-to-text',
        'SAGEMAKER_CONTAINER_LOG_LEVEL': '20',
        'SAGEMAKER_REGION': region,
        'TRANSFORMERS_CACHE': '/tmp',
        'HF_HUB_CACHE': '/tmp'
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

def delete_existing_resources(endpoint_name):
    """Delete existing SageMaker resources if they exist"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    try:
        # Try to delete existing endpoint
        print(f"🗑️ Cleaning up existing endpoint: {endpoint_name}")
        sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
        
        # Wait for deletion
        while True:
            try:
                sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
                print("⏳ Waiting for endpoint deletion...")
                time.sleep(10)
            except sagemaker_client.exceptions.EndpointNotFound:
                print("✅ Endpoint deleted")
                break
                
    except Exception as e:
        if "does not exist" in str(e) or "could not be found" in str(e):
            print("ℹ️ No existing endpoint to delete")
        else:
            print(f"⚠️ Error during cleanup: {str(e)}")

def create_endpoint_config_updated(config_name, model_name, instance_type='ml.g5.xlarge'):
    """Create endpoint configuration with larger instance"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    try:
        response = sagemaker_client.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InitialInstanceCount': 1,
                    'InstanceType': instance_type,  # Using larger instance
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

def wait_for_endpoint(endpoint_name, max_wait_time=2400):  # 40 minutes for larger model
    """Wait for endpoint to be in service"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    print(f"⏳ Waiting for endpoint {endpoint_name} to be in service...")
    print("This may take 15-25 minutes for the 7B model...")
    
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
                elapsed = int(time.time() - start_time)
                print(f"🔄 Status: {status} (elapsed: {elapsed//60}m {elapsed%60}s)")
                time.sleep(30)
                
        except Exception as e:
            print(f"❌ Error checking endpoint status: {str(e)}")
            return False
    
    print(f"⏰ Timeout waiting for endpoint")
    return False

def test_endpoint_simple(endpoint_name):
    """Test the deployed endpoint with text-only input"""
    
    runtime_client = boto3.client('sagemaker-runtime')
    
    # Simple text input that doesn't require vision capabilities
    test_payload = {
        "inputs": "What can you help me with?",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.1,
            "do_sample": False
        }
    }
    
    try:
        print("🧪 Testing endpoint with simple text input...")
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
        return False

def main():
    """Main deployment function with updated approach"""
    
    print("=== UI-TARS Updated Deployment ===\n")
    
    # Use the existing endpoint name from previous deployment
    existing_endpoint = "ui-tars-endpoint-1754960119"
    
    # Configuration for new deployment
    timestamp = int(time.time())
    model_name = f"ui-tars-model-updated-{timestamp}"
    config_name = f"ui-tars-config-updated-{timestamp}"
    endpoint_name = f"ui-tars-endpoint-updated-{timestamp}"
    
    # Get execution role (use the same one from before)
    execution_role = "arn:aws:iam::908196778839:role/service-role/AmazonSageMaker-ExecutionRole-20250811T205896"
    
    # Get AWS region
    session = boto3.Session()
    region = session.region_name or 'us-east-1'
    print(f"Using region: {region}")
    
    # Step 0: Clean up existing endpoint if needed
    print(f"\n0️⃣ Cleaning up previous deployment...")
    delete_existing_resources(existing_endpoint)
    
    # Step 1: Create model with updated container
    print(f"\n1️⃣ Creating SageMaker model with updated Transformers...")
    model_arn = create_sagemaker_model_updated(model_name, execution_role, region)
    if not model_arn:
        return
    
    # Step 2: Create endpoint configuration with larger instance
    print(f"\n2️⃣ Creating endpoint configuration...")
    config_arn = create_endpoint_config_updated(config_name, model_name, 'ml.g5.xlarge')
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
    test_endpoint_simple(endpoint_name)
    
    # Summary
    print(f"\n🎉 Updated deployment completed!")
    print(f"Endpoint name: {endpoint_name}")
    print(f"Model: ByteDance-Seed/UI-TARS-1.5-7B")
    print(f"Instance type: ml.g5.xlarge")
    print(f"Container: Transformers 4.44.0 (supports qwen2_5_vl)")
    
    print(f"\n💰 Remember to delete the endpoint when done:")
    print(f"aws sagemaker delete-endpoint --endpoint-name {endpoint_name}")

if __name__ == "__main__":
    main()
