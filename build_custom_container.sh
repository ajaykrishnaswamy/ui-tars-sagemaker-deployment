#!/bin/bash

# Build and deploy custom UI-TARS container
set -e

# Configuration
REGION=${AWS_REGION:-us-east-1}
REPOSITORY_NAME="ui-tars-custom"

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORY_NAME}:latest"

echo "Building custom UI-TARS container..."
echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION" 
echo "ECR URI: $ECR_URI"

# Create ECR repository if it doesn't exist
echo "Creating ECR repository..."
aws ecr create-repository --repository-name $REPOSITORY_NAME --region $REGION || echo "Repository already exists"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build the container
echo "Building Docker container..."
docker build -t $REPOSITORY_NAME:latest -f Dockerfile.uitars .

# Tag for ECR
echo "Tagging container..."
docker tag $REPOSITORY_NAME:latest $ECR_URI

# Push to ECR
echo "Pushing to ECR..."
docker push $ECR_URI

echo "✅ Container built and pushed successfully!"
echo "Container URI: $ECR_URI"
echo ""
echo "Next: Update deploy_custom_container.py with your IAM role and run:"
echo "python deploy_custom_container.py"