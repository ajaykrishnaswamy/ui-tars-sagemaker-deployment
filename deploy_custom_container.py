#!/usr/bin/env python3
"""
Deploy UI-TARS using custom container with updated Transformers
"""
import boto3
import time
from datetime import datetime

def build_and_push_container():
    """Build and push custom container to ECR"""
    
    # Get AWS account and region
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    region = boto3.Session().region_name or 'us-east-1'
    
    ecr_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/ui-tars-custom:latest"
    
    print("Building and pushing custom container...")
    print("Run these commands manually:")
    print(f"""
    # Create ECR repository
    aws ecr create-repository --repository-name ui-tars-custom --region {region}
    
    # Get login token
    aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com
    
    # Build container
    docker build -t ui-tars-custom:latest -f Dockerfile.uitars .
    
    # Tag for ECR
    docker tag ui-tars-custom:latest {ecr_uri}
    
    # Push to ECR
    docker push {ecr_uri}
    """)
    
    return ecr_uri

def deploy_with_custom_container(image_uri):
    """Deploy UI-TARS using custom container"""
    
    sagemaker = boto3.client('sagemaker')
    
    # Configuration
    model_name = f'ui-tars-custom-{int(time.time())}'
    endpoint_config_name = f'ui-tars-config-{int(time.time())}'
    endpoint_name = f'ui-tars-endpoint-{int(time.time())}'
    
    # IAM role (use existing or create one)
    role_arn = 'arn:aws:iam::YOUR_ACCOUNT:role/SageMakerExecutionRole'  # Update this
    
    try:
        # 1. Create Model
        print("Creating SageMaker model...")
        sagemaker.create_model(
            ModelName=model_name,
            PrimaryContainer={
                'Image': image_uri,
                'Environment': {
                    'HF_MODEL_ID': 'ByteDance-Seed/UI-TARS-1.5-7B',
                    'HF_TASK': 'image-to-text',
                    'HF_MODEL_TRUST_REMOTE_CODE': 'TRUE'
                }
            },
            ExecutionRoleArn=role_arn
        )
        
        # 2. Create Endpoint Configuration
        print("Creating endpoint configuration...")
        sagemaker.create_endpoint_config(
            EndpointConfigName=endpoint_config_name,
            ProductionVariants=[{
                'VariantName': 'primary',
                'ModelName': model_name,
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.g5.2xlarge'
            }]
        )
        
        # 3. Create Endpoint
        print("Creating endpoint...")
        sagemaker.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
        
        print(f"Endpoint '{endpoint_name}' is being created...")
        return endpoint_name
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Step 1: Build custom container
    image_uri = build_and_push_container()
    
    print("\nAfter building and pushing the container, update the role_arn and run:")
    print(f"python -c \"from deploy_custom_container import deploy_with_custom_container; deploy_with_custom_container('{image_uri}')\"")