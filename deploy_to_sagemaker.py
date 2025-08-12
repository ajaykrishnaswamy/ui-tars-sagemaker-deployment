#!/usr/bin/env python3
"""
Script to deploy UI-TARS model to Amazon SageMaker
"""

import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel
from sagemaker import get_execution_role
import time

def upload_model_to_s3(bucket_name, model_file="ui-tars-model.tar.gz"):
    """Upload the model package to S3"""
    
    s3_client = boto3.client('s3')
    s3_key = f"models/ui-tars/{int(time.time())}/model.tar.gz"
    
    try:
        print(f"Uploading {model_file} to s3://{bucket_name}/{s3_key}...")
        s3_client.upload_file(model_file, bucket_name, s3_key)
        s3_uri = f"s3://{bucket_name}/{s3_key}"
        print(f"Successfully uploaded to: {s3_uri}")
        return s3_uri
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        return None

def deploy_ui_tars_model(s3_model_uri, endpoint_name=None):
    """Deploy UI-TARS model to SageMaker endpoint"""
    
    try:
        # Get SageMaker execution role and session
        role = get_execution_role()
        sess = sagemaker.Session()
        
        print(f"Using SageMaker role: {role}")
        print(f"Model S3 URI: {s3_model_uri}")
        
        # Create a Hugging Face Model object
        huggingface_model = HuggingFaceModel(
            model_data=s3_model_uri,
            role=role,
            transformers_version="4.37",  # Latest supported version
            pytorch_version="2.1",        # Latest supported version
            py_version="py310",           # Python 3.10
            model_server_workers=1        # Single worker for 7B model
        )
        
        # Generate endpoint name if not provided
        if endpoint_name is None:
            endpoint_name = f"ui-tars-endpoint-{int(time.time())}"
        
        print(f"Deploying model to endpoint: {endpoint_name}")
        print("This may take 10-15 minutes...")
        
        # Deploy the model to a SageMaker Endpoint
        predictor = huggingface_model.deploy(
            initial_instance_count=1,
            instance_type="ml.g5.2xlarge",  # GPU instance suitable for 7B model
            endpoint_name=endpoint_name
        )
        
        print(f"✅ Successfully deployed model!")
        print(f"Endpoint name: {predictor.endpoint_name}")
        print(f"Endpoint URL: {predictor.endpoint_name}")
        
        return predictor
        
    except Exception as e:
        print(f"Error deploying model: {str(e)}")
        return None

def test_endpoint(predictor):
    """Test the deployed endpoint with a sample request"""
    
    try:
        print("\nTesting endpoint...")
        
        # Sample input for UI-TARS model
        test_input = {
            "inputs": "Take a screenshot and describe what you see on the screen",
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7
            }
        }
        
        response = predictor.predict(test_input)
        print(f"✅ Endpoint test successful!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error testing endpoint: {str(e)}")

def main():
    """Main deployment workflow"""
    
    print("=== UI-TARS SageMaker Deployment ===\n")
    
    # Configuration
    bucket_name = input("Enter your S3 bucket name: ").strip()
    if not bucket_name:
        print("Error: S3 bucket name is required!")
        return
    
    model_file = "ui-tars-model.tar.gz"
    
    # Step 1: Upload model to S3
    print("\n1. Uploading model to S3...")
    s3_model_uri = upload_model_to_s3(bucket_name, model_file)
    if not s3_model_uri:
        return
    
    # Step 2: Deploy to SageMaker
    print("\n2. Deploying to SageMaker...")
    predictor = deploy_ui_tars_model(s3_model_uri)
    if not predictor:
        return
    
    # Step 3: Test the endpoint
    print("\n3. Testing endpoint...")
    test_endpoint(predictor)
    
    print(f"\n🎉 Deployment completed successfully!")
    print(f"Endpoint name: {predictor.endpoint_name}")
    print(f"\nTo clean up resources later, run:")
    print(f"aws sagemaker delete-endpoint --endpoint-name {predictor.endpoint_name}")

if __name__ == "__main__":
    main()
