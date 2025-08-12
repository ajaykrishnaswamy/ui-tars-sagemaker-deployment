#!/usr/bin/env python3
"""
Script to deploy UI-TARS model directly from Hugging Face Hub to Amazon SageMaker
This approach is more efficient as it doesn't require manual downloading and packaging.
"""

import sagemaker
from sagemaker.huggingface import HuggingFaceModel
from sagemaker import get_execution_role
import time

def deploy_ui_tars_from_hub(endpoint_name=None):
    """Deploy UI-TARS model directly from Hugging Face Hub to SageMaker"""
    
    try:
        # Get SageMaker execution role and session
        role = get_execution_role()
        sess = sagemaker.Session()
        
        print(f"Using SageMaker role: {role}")
        print(f"SageMaker session region: {sess.boto_region_name}")
        
        # Define the model configuration for UI-TARS-1.5-7B
        hub_config = {
            'HF_MODEL_ID': 'ByteDance-Seed/UI-TARS-1.5-7B',
            'HF_TASK': 'image-to-text'  # UI-TARS is a multimodal model for GUI tasks
        }
        
        print(f"Model ID: {hub_config['HF_MODEL_ID']}")
        print(f"Task: {hub_config['HF_TASK']}")
        
        # Create a Hugging Face Model object
        huggingface_model = HuggingFaceModel(
            env=hub_config,
            role=role,
            transformers_version="4.37",  # Latest supported version for multimodal models
            pytorch_version="2.1",        # Latest supported version
            py_version="py310",           # Python 3.10
            model_server_workers=1        # Single worker for large 7B model
        )
        
        # Generate endpoint name if not provided
        if endpoint_name is None:
            endpoint_name = f"ui-tars-endpoint-{int(time.time())}"
        
        print(f"\nDeploying model to endpoint: {endpoint_name}")
        print("This process may take 10-15 minutes...")
        print("SageMaker will:")
        print("1. Pull the model from Hugging Face Hub")
        print("2. Build the inference container")
        print("3. Launch the endpoint")
        
        # Deploy the model to a SageMaker Endpoint
        predictor = huggingface_model.deploy(
            initial_instance_count=1,
            instance_type="ml.g5.2xlarge",  # GPU instance suitable for 7B multimodal model
            endpoint_name=endpoint_name,
            wait=True  # Wait for deployment to complete
        )
        
        print(f"\n✅ Successfully deployed UI-TARS model!")
        print(f"Endpoint name: {predictor.endpoint_name}")
        print(f"Model: ByteDance-Seed/UI-TARS-1.5-7B")
        
        return predictor
        
    except Exception as e:
        print(f"❌ Error deploying model: {str(e)}")
        return None

def test_ui_tars_endpoint(predictor):
    """Test the deployed UI-TARS endpoint with sample inputs"""
    
    try:
        print("\n🧪 Testing UI-TARS endpoint...")
        
        # Sample input for UI-TARS multimodal model
        # Note: For a real test, you'd need to provide image data
        test_input = {
            "inputs": "Describe what you see on the screen and suggest the next action.",
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        print(f"Sending test request...")
        response = predictor.predict(test_input)
        
        print(f"✅ Endpoint test successful!")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")
        print("Note: UI-TARS requires image inputs for full functionality.")
        print("The endpoint is deployed but may need proper multimodal inputs.")
        return False

def get_endpoint_info(predictor):
    """Display endpoint information and usage instructions"""
    
    print(f"\n📋 Endpoint Information:")
    print(f"Endpoint Name: {predictor.endpoint_name}")
    print(f"Instance Type: ml.g5.2xlarge")
    print(f"Model: ByteDance-Seed/UI-TARS-1.5-7B")
    
    print(f"\n🔧 Usage Example:")
    print(f"""
import boto3
import json

# Create SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime')

# Prepare your input (example for text-only)
payload = {{
    "inputs": "Take a screenshot and describe what you see",
    "parameters": {{
        "max_new_tokens": 100,
        "temperature": 0.7
    }}
}}

# Make prediction
response = sagemaker_runtime.invoke_endpoint(
    EndpointName='{predictor.endpoint_name}',
    ContentType='application/json',
    Body=json.dumps(payload)
)

result = json.loads(response['Body'].read().decode())
print(result)
""")
    
    print(f"\n💰 Cost Considerations:")
    print(f"Instance Type: ml.g5.2xlarge (~$1.50/hour)")
    print(f"Remember to delete the endpoint when not in use to avoid charges.")
    
    print(f"\n🗑️  Cleanup Command:")
    print(f"aws sagemaker delete-endpoint --endpoint-name {predictor.endpoint_name}")

def main():
    """Main deployment workflow"""
    
    print("=== UI-TARS Direct Deployment from Hugging Face Hub ===\n")
    
    # Deploy the model
    print("🚀 Starting deployment...")
    predictor = deploy_ui_tars_from_hub()
    
    if not predictor:
        print("❌ Deployment failed!")
        return
    
    # Test the endpoint
    test_ui_tars_endpoint(predictor)
    
    # Display endpoint information
    get_endpoint_info(predictor)
    
    print(f"\n🎉 UI-TARS deployment completed successfully!")
    print(f"Your multimodal AI agent is now ready for GUI automation tasks!")

if __name__ == "__main__":
    main()
