#!/usr/bin/env python3
"""
Test script to verify SageMaker setup without actually deploying
"""

import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel

def test_sagemaker_setup():
    """Test if SageMaker setup is working correctly"""
    
    try:
        print("🧪 Testing SageMaker setup...")
        
        # Test boto3 session
        session = boto3.Session()
        region = session.region_name or 'us-east-1'
        print(f"✅ AWS Region: {region}")
        
        # Test SageMaker session
        sagemaker_session = sagemaker.Session()
        print(f"✅ SageMaker Region: {sagemaker_session.boto_region_name}")
        
        # Test execution role (this might fail if not in SageMaker environment)
        try:
            from sagemaker import get_execution_role
            role = get_execution_role()
            print(f"✅ Execution Role: {role}")
        except Exception as e:
            print(f"⚠️  Execution Role: {str(e)}")
            print("   Note: This is expected if running outside SageMaker environment")
            print("   You'll need to provide an IAM role when deploying")
        
        # Test HuggingFace model creation (without deploying)
        print("\n🤖 Testing Hugging Face model configuration...")
        
        hub_config = {
            'HF_MODEL_ID': 'ByteDance-Seed/UI-TARS-1.5-7B',
            'HF_TASK': 'image-to-text'
        }
        
        # Create model object without deploying
        dummy_role = "arn:aws:iam::123456789012:role/SageMakerExecutionRole"
        
        huggingface_model = HuggingFaceModel(
            env=hub_config,
            role=dummy_role,
            transformers_version="4.37",
            pytorch_version="2.1",
            py_version="py310"
        )
        
        print(f"✅ Model ID: {hub_config['HF_MODEL_ID']}")
        print(f"✅ Task: {hub_config['HF_TASK']}")
        print(f"✅ Transformers Version: 4.37")
        print(f"✅ PyTorch Version: 2.1")
        
        print(f"\n🎉 Setup test completed successfully!")
        print(f"You're ready to deploy UI-TARS to SageMaker!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {str(e)}")
        return False

def show_deployment_instructions():
    """Show instructions for deployment"""
    
    print(f"\n📋 Next Steps:")
    print(f"1. Ensure you have a SageMaker execution role with proper permissions")
    print(f"2. Run: python deploy_ui_tars_directly.py")
    print(f"3. Wait 10-15 minutes for deployment to complete")
    print(f"4. Test your endpoint with multimodal inputs")
    
    print(f"\n💡 Tips:")
    print(f"- Use ml.g5.2xlarge or larger for optimal performance")
    print(f"- UI-TARS works best with image + text inputs")
    print(f"- Remember to delete endpoints when not in use")

if __name__ == "__main__":
    print("=== UI-TARS SageMaker Setup Test ===\n")
    
    success = test_sagemaker_setup()
    
    if success:
        show_deployment_instructions()
    else:
        print("\n❌ Please fix the setup issues before proceeding")
