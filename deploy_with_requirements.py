#!/usr/bin/env python3
"""
Deploy UI-TARS with requirements.txt approach for updated transformers
"""
import boto3
import time
import json

def create_requirements_txt():
    """Create requirements.txt with UI-TARS dependencies"""
    requirements = """
transformers>=4.40.0
torch>=2.0.0
accelerate>=0.20.0
pillow>=8.0.0
huggingface-hub>=0.16.0
"""
    with open('requirements.txt', 'w') as f:
        f.write(requirements.strip())
    print("✅ Created requirements.txt with UI-TARS dependencies")

def create_inference_code():
    """Create inference.py for SageMaker"""
    code = '''
import os
import json
import logging
import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import base64
import io

logger = logging.getLogger(__name__)

def model_fn(model_dir):
    """Load the model for inference"""
    try:
        model_name = os.environ.get('HF_MODEL_ID', 'ByteDance-Seed/UI-TARS-1.5-7B')
        
        # Load model and tokenizer
        model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        return {"model": model, "tokenizer": tokenizer}
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def input_fn(request_body, content_type):
    """Parse input data"""
    if content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model_dict):
    """Run inference"""
    try:
        model = model_dict["model"]
        tokenizer = model_dict["tokenizer"]
        
        # Get inputs
        text_prompt = input_data.get("text", "Describe this image")
        image_data = input_data.get("image")
        
        # Process image
        if isinstance(image_data, str):
            # Base64 encoded image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            raise ValueError("Image must be base64 encoded string")
        
        # Run inference
        with torch.no_grad():
            response = model.chat(
                image=image,
                msgs=[{"role": "user", "content": text_prompt}],
                tokenizer=tokenizer
            )
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error during inference: {str(e)}")
        return {"error": str(e)}

def output_fn(prediction, accept):
    """Format output"""
    if accept == 'application/json':
        return json.dumps(prediction), 'application/json'
    else:
        raise ValueError(f"Unsupported accept type: {accept}")
'''
    
    with open('inference.py', 'w') as f:
        f.write(code)
    print("✅ Created inference.py for SageMaker")

def deploy_ui_tars_with_requirements():
    """Deploy UI-TARS using requirements.txt approach"""
    
    sagemaker = boto3.client('sagemaker')
    
    # Configuration
    model_name = f'ui-tars-requirements-{int(time.time())}'
    endpoint_config_name = f'ui-tars-config-{int(time.time())}'
    endpoint_name = f'ui-tars-endpoint-{int(time.time())}'
    
    # Get role ARN from existing deployments or use default
    try:
        existing_models = sagemaker.list_models(NameContains='ui-tars')['Models']
        if existing_models:
            role_arn = sagemaker.describe_model(ModelName=existing_models[0]['ModelName'])['ExecutionRoleArn']
        else:
            # Default role (update this with your actual role)
            account_id = boto3.client('sts').get_caller_identity()['Account']
            role_arn = f'arn:aws:iam::{account_id}:role/SageMakerExecutionRole'
    except:
        account_id = boto3.client('sts').get_caller_identity()['Account']
        role_arn = f'arn:aws:iam::{account_id}:role/SageMakerExecutionRole'
    
    # Use Hugging Face container with code upload
    region = boto3.Session().region_name or 'us-east-1'
    container_uri = f'763104351884.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-gpu-py39-cu117-ubuntu20.04'
    
    try:
        # 1. Create Model with code upload
        print("Creating SageMaker model with custom code...")
        sagemaker.create_model(
            ModelName=model_name,
            PrimaryContainer={
                'Image': container_uri,
                'Environment': {
                    'HF_MODEL_ID': 'ByteDance-Seed/UI-TARS-1.5-7B',
                    'HF_TASK': 'image-to-text',
                    'SAGEMAKER_PROGRAM': 'inference.py',
                    'SAGEMAKER_REQUIREMENTS': 'requirements.txt'
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
        
        print(f"✅ Endpoint '{endpoint_name}' is being created...")
        print("This approach uploads requirements.txt and inference.py to handle the Transformers version issue")
        return endpoint_name
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Deploying UI-TARS with requirements.txt approach...")
    
    # Create necessary files
    create_requirements_txt()
    create_inference_code()
    
    # Deploy
    endpoint_name = deploy_ui_tars_with_requirements()
    
    if endpoint_name:
        print(f"\n🎉 Deployment initiated!")
        print(f"Endpoint: {endpoint_name}")
        print("\nThis approach should handle the Transformers version compatibility issue.")
    else:
        print("\n❌ Deployment failed")