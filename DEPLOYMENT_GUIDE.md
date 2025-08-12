# UI-TARS SageMaker Deployment Guide

## 🎯 Overview

This guide provides step-by-step instructions to deploy the [ByteDance UI-TARS-1.5-7B model](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B) to Amazon SageMaker for automated GUI interaction and computer vision tasks.

## 🚀 Quick Start

### Option 1: Direct Deployment (Recommended)

Deploy directly from Hugging Face Hub without downloading:

```bash
python simple_deploy.py
```

### Option 2: Advanced Deployment

Use the full SageMaker SDK:

```bash
python deploy_ui_tars_directly.py
```

## 📋 Prerequisites

1. **AWS Account** with SageMaker access
2. **AWS CLI** configured with your credentials
3. **Python 3.8+**
4. **SageMaker execution role** with necessary permissions

### Setting up AWS CLI

```bash
aws configure
```

### Creating SageMaker Execution Role

Your execution role needs these policies:
- `AmazonSageMakerFullAccess`
- `AmazonS3ReadOnlyAccess` (for Hugging Face model access)

## 📦 Installation

```bash
# Clone or download this repository
git clone <repository-url>
cd tiktokui

# Install dependencies
pip install boto3 sagemaker huggingface-hub
```

## 🔧 Deployment Steps

### Step 1: Choose Your Deployment Method

**Simple Deployment (Recommended for beginners):**
- Uses boto3 directly
- Fewer dependencies
- More explicit control

**Advanced Deployment:**
- Uses SageMaker Python SDK
- More features and abstractions
- Requires more dependencies

### Step 2: Run Deployment Script

```bash
# For simple deployment
python simple_deploy.py

# For advanced deployment
python deploy_ui_tars_directly.py
```

### Step 3: Provide Required Information

When prompted, provide:
- **SageMaker execution role ARN** (format: `arn:aws:iam::123456789012:role/SageMakerExecutionRole`)
- **AWS region** (will use your default if not specified)

### Step 4: Wait for Deployment

The deployment process takes 10-15 minutes and includes:
1. Creating SageMaker model
2. Creating endpoint configuration
3. Creating and starting endpoint
4. Downloading model from Hugging Face Hub
5. Testing the endpoint

## 💡 Model Specifications

- **Model**: ByteDance-Seed/UI-TARS-1.5-7B
- **Size**: 8.29B parameters
- **Type**: Multimodal (vision + language)
- **Capabilities**: GUI automation, screen understanding, computer vision
- **Instance**: ml.g5.2xlarge (GPU-accelerated)

## 🎮 Performance Benchmarks

UI-TARS-1.5 achieves state-of-the-art results:

| Benchmark | UI-TARS-1.5 | OpenAI CUA | Claude 3.7 |
|-----------|-------------|------------|------------|
| OSWorld | **42.5%** | 36.4% | 28% |
| Windows Agent Arena | **42.1%** | - | 28% |
| Android World | **64.2%** | - | - |
| ScreensSpot-V2 | **94.2%** | 87.9% | 87.6% |

## 📖 Usage Examples

### Basic Text Input

```python
import boto3
import json

# Create SageMaker runtime client
runtime = boto3.client('sagemaker-runtime')

# Prepare payload
payload = {
    "inputs": "Describe what you see on the screen",
    "parameters": {
        "max_new_tokens": 100,
        "temperature": 0.7
    }
}

# Make prediction
response = runtime.invoke_endpoint(
    EndpointName='your-endpoint-name',
    ContentType='application/json',
    Body=json.dumps(payload)
)

result = json.loads(response['Body'].read().decode())
print(result)
```

### Multimodal Input (Image + Text)

For full GUI automation capabilities, UI-TARS works best with image inputs. The model can process screenshots and provide action recommendations.

## 💰 Cost Estimation

| Component | Cost (per hour) | Notes |
|-----------|----------------|--------|
| ml.g5.2xlarge | ~$1.50 | GPU instance for inference |
| Data transfer | Variable | Depends on usage |
| Storage | Minimal | Model loaded from HF Hub |

**Total estimated cost: ~$1.50-2.00 per hour**

## 🛠️ Troubleshooting

### Common Issues

1. **Role Permissions**: Ensure your execution role has SageMaker and S3 access
2. **Region Support**: Use regions that support GPU instances (us-east-1, us-west-2, eu-west-1)
3. **Instance Limits**: Check your AWS account limits for GPU instances
4. **Dependencies**: Install all required Python packages

### Error Messages

- **"No module named 'sagemaker'"**: Run `pip install sagemaker`
- **"AccessDenied"**: Check your IAM role permissions
- **"InsufficientInstanceCapacity"**: Try a different region or instance type

## 🔍 Testing Your Deployment

The deployment scripts include automatic testing. You can also test manually:

```bash
# Test endpoint status
aws sagemaker describe-endpoint --endpoint-name your-endpoint-name

# Test inference (requires endpoint to be InService)
python test_endpoint.py
```

## 🗑️ Cleanup

**Important**: Remember to delete your endpoint when finished to avoid ongoing charges:

```bash
# Delete endpoint
aws sagemaker delete-endpoint --endpoint-name your-endpoint-name

# Delete endpoint configuration
aws sagemaker delete-endpoint-config --endpoint-config-name your-config-name

# Delete model
aws sagemaker delete-model --model-name your-model-name
```

## 📚 Additional Resources

- [UI-TARS Paper](https://arxiv.org/abs/2501.12326)
- [Hugging Face Model Page](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B)
- [SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [GitHub Repository](https://github.com/bytedance/UI-TARS)

## 🤝 Support

For issues related to:
- **Model functionality**: Contact TARS@bytedance.com
- **SageMaker deployment**: Check AWS documentation
- **This guide**: Create an issue in the repository

## 📄 License

This project follows the Apache 2.0 license of the original UI-TARS model.
